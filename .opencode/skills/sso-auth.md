# Skill: sso-auth            (seed · from docs/SECURITY_AND_AUTH_RUNBOOK.md)

## Context
Login/logout/session/guards. Auth changes ALWAYS require the human gate (AGENTS.md #7).
Sessions = stateless HMAC-signed cookies. KV sessions are forbidden.

## Pattern
```python
# src/lib/session.py owns: make_session_cookie(payload, secret), verify_session(request)
# cookie: HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=7d; rolling refresh >24h
# payload: { sub, email, name, iat, exp }  — keep <1KB

# route guard — middleware
app.middleware("http")(session_middleware)
# /app/* guarded by require_session dependency: browser 302 /auth/login,
#                                       htmx (HX-Request): 401 + HX-Redirect header
# global csrf_check() dependency — Origin check; htmx sends Origin on POST

# flow: GET /auth/login → Google (state nonce in 5min signed cookie)
#       GET /auth/callback → verify state → exchange code → verify ID token (JWKS
#       cached in KV 6h) → upsert users → set cookie → 302 /
```

## Proof
```gherkin
@ui Scenario: unauthenticated visit to /app redirects to login
@api Scenario: mutation without session cookie → 401
```

## Gotchas
- Tests NEVER hit Google: inject cookie signed with the env's SESSION_SECRET
  (features/conftest.py). No mock routes may exist.
- Mobile: OAuth in system browser only; deep-link one-time code exchange (runbook §3).
- Support SESSION_SECRET_PREV dual-verify during rotation.
