# SECURITY_AND_AUTH_RUNBOOK.md

> How identity, sessions, and secrets work in every app built from this template.
> AI agents: implement auth ONLY through `src/lib/session.py`, `src/lib/csrf.py`.

## 1. Session Model — Stateless Signed Cookies

**Decision:** sessions are HMAC-SHA256-signed cookies (Python stdlib via `hmac` + `hashlib`).
No KV sessions (eventual consistency makes logout/permission changes lag ≤60s).
No D1 session reads (costs CPU/IO budget on every request).

Cookie payload (kept < 1KB):

```json
{ "sub": "google-user-id", "email": "a@b.c", "name": "Ada", "iat": 1730000000, "exp": 1730604800 }
```

Properties (all mandatory):

| Property | Value | Defends against |
|---|---|---|
| `HttpOnly` | yes | XSS cookie theft — JS can never read it |
| `Secure` | yes | plaintext interception |
| `SameSite` | `Lax` | CSRF on cross-site POSTs; still allows top-level OAuth redirects |
| `Path` | `/` | — |
| `Max-Age` | 7 days, **rolling refresh** when > 24h old | stale sessions |
| Signature | HMAC-SHA256 with `SESSION_SECRET` | forgery/tamper |

Revocation strategy for stateless sessions: short exp + rolling refresh. For hard-ban
cases, keep a tiny D1 `revoked_subs` table checked **only** on refresh, not per request.

### CSRF (required — SameSite=Lax is not sufficient alone)
Use a FastAPI dependency globally on mutation routes: it rejects state-changing requests
whose `Origin` doesn't match the request `Host`. htmx sends `Origin` on POST automatically.
No hidden-token plumbing needed; do NOT roll a custom token system.

```python
# src/lib/csrf.py
from fastapi import Request, HTTPException


async def csrf_check(request: Request):
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    origin = request.headers.get("Origin")
    if not origin:
        raise HTTPException(status_code=403, detail="CSRF: missing Origin")
    host = request.headers.get("Host", "")
    if origin not in [f"http://{host}", f"https://{host}"]:
        raise HTTPException(status_code=403, detail="CSRF: Origin mismatch")
```

## 2. Google SSO Lifecycle — Web

Server-side authorization-code flow. No client-side Google JS SDK.

```
1. GET /auth/login      → 302 to accounts.google.com (scope: openid email profile,
                          state = random nonce stored in short-lived signed cookie)
2. Google redirects     → GET /auth/callback?code=...&state=...
3. Worker verifies state, exchanges code (fetch to oauth2.googleapis.com/token,
   client_secret from Wrangler secret), verifies the ID token (iss, aud, exp, sig
   against Google JWKS — cache JWKS in KV, TTL 6h)
4. Upsert user row in D1 (users table)
5. Set signed session cookie → 302 to "/"
6. GET /auth/logout     → clear cookie → 302 to "/"
```

Route guard: `require_session` dependency. Browser requests → 302 `/auth/login`;
htmx requests (`HX-Request: true`) → `HX-Redirect: /auth/login` header with 401.

## 3. Google SSO Lifecycle — Capacitor Mobile (bundled shell)

Google **blocks OAuth inside WebViews** (`disallowed_useragent`). The mobile flow must
use the system browser. Standing design:

```
1. Shell (bundled Capacitor app) opens https://<app>/auth/login?platform=mobile
   in the SYSTEM browser (@capacitor/browser → Custom Tabs / ASWebAuthenticationSession).
2. Same server-side code flow as web (§2).
3. Callback with platform=mobile 302s to  com.<org>.<app>://auth?token=<one-time-code>
   (one-time code = 60s-TTL row in D1, single use).
4. Shell catches the deep link (App URL listener), calls POST /auth/exchange
   { code } → server validates + burns the code → sets the session cookie on the
   WebView's origin → shell reloads the app view.
```

Shell composition (satisfies App Store Guideline 4.2 — not a bare remote wrapper):
- Bundled local assets: splash, offline screen, error retry view, htmx/alpine/css.
- Native touches: deep-link handling, share sheet, push-ready scaffold.
- App content served from the production origin inside the WebView **after** auth;
  offline → bundled fallback page with retry.

## 4. Secrets Management

| Environment | Mechanism |
|---|---|
| Local dev | `.dev.vars` (gitignored) — read by `pywrangler dev` |
| CI | GitHub Actions encrypted secrets → env |
| Production | `wrangler secret put <NAME>` (or `pywrangler secret put`) |

Required secrets: `SESSION_SECRET` (32B random), `GOOGLE_CLIENT_ID`,
`GOOGLE_CLIENT_SECRET`. Test-only: `TEST_SESSION_SECRET` (never set in production).

Hard rules:
- ❌ Never in code, `wrangler.toml`, or committed files. Access only via `c.env`.
- ❌ Never log secrets or full cookies.
- `SESSION_SECRET` rotation: support `SESSION_SECRET_PREV` for dual-verify during rotation.

## 5. Test Auth Bypass (see TESTING_AND_QUALITY_SPEC for code)

BDD suites must not hit Google. Bypass = **cookie injection, not mock routes**:
the test harness signs a session cookie with the same HMAC scheme using the
environment's secret (`.dev.vars` sets `SESSION_SECRET=test-secret` locally/CI) and
injects it into the Playwright context / API client. Zero auth code paths differ
between test and production; nothing mock ships in the deploy artifact.

## 6. Threat Checklist (verify per feature, per PRD)

- [ ] XSS: Jinja2 escapes by default — `{{ value|safe }}` is forbidden
      without human sign-off.
- [ ] CSRF: global `csrf_check` dependency present; new POST routes covered.
- [ ] IDOR: every D1 query on user data filters by `session.sub` — no bare `WHERE id=?`.
- [ ] Open redirect: `/auth/*` redirects only to same-origin paths or the app scheme.
- [ ] Cache poisoning: KV fragment keys must include every variable that changes output
      (incl. user id for personalized fragments — or don't cache them).
- [ ] Session fixation: cookie is re-issued at login; state nonce verified in callback.
