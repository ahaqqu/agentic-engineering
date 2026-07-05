import { getCookie } from "hono/cookie";
import { createMiddleware } from "hono/factory";

type Env = {
  Bindings: { DB: D1Database; SESSION_SECRET: string };
  Variables: { session: SessionPayload };
};

const COOKIE_NAME = "session";
const SESSION_TTL = 7 * 86400;
const ALGO = { name: "HMAC", hash: "SHA-256" };

export type SessionPayload = {
  sub: string;
  email: string;
  name: string;
  iat: number;
  exp: number;
};

async function hmacSign(data: string, secret: string): Promise<string> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), ALGO, false, ["sign"]);
  const sig = await crypto.subtle.sign(ALGO, key, enc.encode(data));
  return btoa(String.fromCharCode(...new Uint8Array(sig)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

async function hmacVerify(data: string, sigB64: string, secret: string): Promise<boolean> {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), ALGO, false, ["verify"]);
  const sig = Uint8Array.from(atob(sigB64.replace(/-/g, "+").replace(/_/g, "/")), (c) =>
    c.charCodeAt(0),
  );
  return crypto.subtle.verify(ALGO, key, sig, enc.encode(data));
}

function toB64(obj: unknown): string {
  return btoa(JSON.stringify(obj)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromB64(b64: string): unknown {
  return JSON.parse(atob(b64.replace(/-/g, "+").replace(/_/g, "/")));
}

export async function signToken(payload: SessionPayload, secret: string): Promise<string> {
  const encoded = toB64(payload);
  const sig = await hmacSign(encoded, secret);
  return `${encoded}.${sig}`;
}

export async function verifyToken(token: string, secret: string): Promise<SessionPayload | null> {
  const dot = token.lastIndexOf(".");
  if (dot === -1) return null;
  const encoded = token.slice(0, dot);
  const sig = token.slice(dot + 1);
  const ok = await hmacVerify(encoded, sig, secret);
  if (!ok) return null;
  const payload = fromB64(encoded) as SessionPayload;
  if (typeof payload !== "object" || !payload?.sub) return null;
  return payload;
}

function makePayload(sub: string, email: string, name: string): SessionPayload {
  const now = Math.floor(Date.now() / 1000);
  return { sub, email, name, iat: now, exp: now + SESSION_TTL };
}

export { makePayload };

export const session = () =>
  createMiddleware<Env>(async (c, next) => {
    const secret = c.env.SESSION_SECRET || "insecure-dev-default";
    const raw = getCookie(c, COOKIE_NAME);
    if (raw) {
      try {
        const payload = await verifyToken(raw, secret);
        if (payload) c.set("session", payload);
      } catch {
        // ignore
      }
    }
    await next();
  });

export const requireSession = createMiddleware<Env>(async (c, next) => {
  const session = c.get("session");
  if (!session) {
    if (c.req.header("HX-Request")) {
      c.header("HX-Redirect", "/auth/login");
      return c.text("Unauthorized", 401);
    }
    return c.redirect("/auth/login");
  }
  await next();
});
