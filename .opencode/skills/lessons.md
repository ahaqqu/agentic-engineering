# lessons.md — Self-Correction Ledger (staging area; rules get promoted then deleted)

| date | app | symptom | root cause | rule to never repeat |
|---|---|---|---|---|
| 2026-07-05 | agentic-engineering-template | Session HMAC verification failed (silent → 302) | `hmacSign` used `btoa` (standard base64) but Node's crypto used base64url; sigs never matched | Every HMAC base64 path must convert `+`→`-`, `/`→`_` and strip `=` for cross-env portability. Always test sig round-trip across Worker + Node before declaring session done. |
| 2026-07-05 | agentic-engineering-template | `atob` in `hmacVerify` threw "Invalid character" | base64url signature passed directly to `atob` without converting `-_`→`+/` | `atob` only handles standard base64; always convert base64url before decoding. |
| 2026-07-05 | agentic-engineering-template | FOREIGN KEY constraint failed on item insert | `items.user_id FK → users(sub)` but no user row existed (auth is session-based, not DB) | Session-based auth means no DB user table — remove the FK constraint from the migration. |
| 2026-07-05 | agentic-engineering-template | Unauthenticated archive test expected 401 but got 404 | `fetch` follows 302 redirects automatically; middleware returned 302 (not 401) for non-htmx requests | Test unauthenticated requests as htmx (`HX-Request: true`) so middleware returns 401 directly, or test for 302 + redirect Location. |
