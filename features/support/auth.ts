import { makePayload, signToken } from "../../src/lib/session";

const SESSION_SECRET = process.env.SESSION_SECRET || "test-secret-do-not-use-in-prod";

export async function signedInCookie(email: string): Promise<string> {
  const payload = makePayload(`test-${email}`, email, "Test User");
  return signToken(payload, SESSION_SECRET);
}

export async function sessionCookieFor(
  email: string,
): Promise<{ name: string; value: string; path: string; domain?: string }> {
  const value = await signedInCookie(email);
  return { name: "session", value, path: "/", domain: "localhost" };
}
