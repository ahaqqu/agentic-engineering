# ARCHITECTURE_DEEP_DIVE.md

> Ground truth for every app built from this template. AI agents: this file defines the
> stack, topology, data flow, and hard performance guardrails. Violations are defects.

## 1. Stack Blueprint (v2 — locked)

| Layer | Choice | Notes |
|---|---|---|
| Compute | Cloudflare Workers (native JS runtime, GA) | Free tier: 100k req/day, **10ms CPU/invocation** |
| Framework | **Hono 4.x** (TypeScript, `strict: true`) | Router + middleware + JSX renderer |
| Validation | **Zod** via `@hono/zod-validator` | Every request boundary is a Zod schema |
| Templates | **`hono/jsx`** server-rendered fragments | No React, no hydration, no client build step |
| Frontend | **htmx 2.x + Alpine.js 3.x + Tailwind CSS 4 + daisyUI 5** | Self-hosted static files via Workers Assets (not CDN — required for the Capacitor offline shell) |
| Database | **Cloudflare D1** (serverless SQLite) | Raw SQL prepared statements; migrations via `wrangler d1 migrations` |
| Cache | **Cloudflare KV** | **Cache only. Never a source of truth. Never sessions.** (eventual consistency ≤ 60s) |
| Sessions | **Stateless HMAC-signed cookies** (`hono/cookie` signed helpers) | `HttpOnly; Secure; SameSite=Lax`; short TTL + rolling refresh |
| Auth | Google OAuth2 (server-side code flow) | Mobile: system browser (Custom Tabs / ASWebAuthenticationSession), **never in-WebView** |
| Mobile | **Capacitor.js bundled shell** | Local shell assets + native OAuth plugin; NOT a remote-URL wrapper (App Store 4.2) |
| Quality gate | **Biome** (lint + format) + `tsc --noEmit` | Agents never hand-format; tools do |
| BDD | **@cucumber/cucumber + Playwright** against `wrangler dev` | The only test layer. No unit tests. |
| CI/CD | GitHub Actions → `wrangler deploy` | See `docs/TESTING_AND_QUALITY_SPEC.md` |

Rationale for the runtime swap (was Python/Pyodide): Python Workers are beta, Pyodide is
3–10x slower per CPU cycle, and Pydantic/Jinja2-in-WASM jeopardizes the 10ms budget.
Hono+JSX preserves the identical hypermedia architecture at <1ms typical render cost.

## 2. Directory Topology (agent-optimized)

One concept per directory. One resource per file. Names are contracts.

```
app/
├── wrangler.toml            # bindings: DB (D1), CACHE (KV), ASSETS; vars per env
├── package.json             # scripts: dev, check, test, deploy
├── tsconfig.json            # strict, jsx: react-jsx, jsxImportSource: hono/jsx
├── biome.json
├── src/
│   ├── index.ts             # Hono app: mount middleware + routes ONLY (no logic)
│   ├── routes/              # 1 file per resource: items.ts, auth.ts, health.ts
│   ├── views/
│   │   ├── layout.tsx       # full-page shell (rendered ONLY on non-HX requests)
│   │   ├── pages/           # full pages composed from fragments
│   │   └── fragments/       # htmx swap targets: itemRow.tsx, itemList.tsx ...
│   ├── db/                  # 1 file per table: items.ts (typed query fns, raw SQL)
│   ├── schemas/             # Zod schemas: items.ts, auth.ts (shared by routes+tests)
│   └── lib/                 # session.ts, csrf.ts, cache.ts, oauth.ts, hx.ts
├── migrations/              # 0001_init.sql ... (wrangler d1 migrations)
├── features/                # BDD ground truth
│   ├── *.feature
│   ├── steps/               # api.steps.ts, ui.steps.ts
│   └── support/             # world.ts, hooks.ts (wrangler dev lifecycle, auth bypass)
├── public/                  # htmx.min.js, alpine.min.js, app.css (Tailwind build output), icons
└── capacitor/               # mobile shell project (see SECURITY_AND_AUTH_RUNBOOK)
```

## 3. Request Data Flow (the only mutation path)

```
[Browser DOM]
   │  htmx attribute fires (hx-post="/items/:id/archive", HX-Request: true)
   ▼
[Cloudflare Worker: Hono router]
   │  middleware: session verify (HMAC cookie) → CSRF (Origin check) → zod-validator
   ▼
[db/<table>.ts]  prepared statement → D1 (batch when >1 statement)
   ▼
[views/fragments/<name>.tsx]  JSX fragment render (c.html(...))
   ▼
[htmx swap]  hx-target + hx-swap replaces exactly one DOM node
```

Rules encoded by this flow:
- **Routes contain no business logic**; they orchestrate `schemas → db → views`.
- **Every POST/PUT/PATCH/DELETE returns an HTML fragment**, never JSON (JSON only for
  non-htmx machine endpoints, which are rare and must be justified in the PRD).
- **Full page vs fragment**: branch on the `HX-Request` header via `lib/hx.ts`; a GET hit
  directly (deep link, refresh) returns `layout(page)`, an htmx hit returns the fragment.

## 4. htmx vs Alpine Boundary Matrix (non-negotiable)

| Behavior | Owner |
|---|---|
| Any data that survives refresh (CRUD, lists, auth state) | **htmx → server** |
| Optimistic-feel UI while request in flight | htmx (`hx-indicator`, `hx-disabled-elt`) |
| Dropdowns, modals open/close, tabs, local toggles, input masks | **Alpine.js** |
| Form validation UX (pre-submit hints) | Alpine (server re-validates with Zod, always) |
| Client-side data stores, fetch calls, routing | **FORBIDDEN** — that's SPA drift |

Alpine state must never mirror server state. If a value exists in D1, htmx owns it.

## 5. The 10ms CPU Covenant

Free-tier hard limit: 10ms CPU per invocation (wall-clock I/O to D1/KV does not count).
Design budget: **≤ 5ms CPU** per request. Enforcement patterns:

1. **Paginate everything.** Default `LIMIT 50`. No unbounded `SELECT`.
2. **Render fragments, not pages**, on every htmx interaction.
3. **`db.batch()`** for multi-statement writes; never sequential awaits in a loop.
4. **Module scope = free init.** Hoist constants, compiled regexes, Zod schemas to module
   top level. Never construct schemas per request.
5. **KV fragment cache** for expensive shared reads (`lib/cache.ts`, TTL 60–300s), keyed
   `frag:<name>:<params>`. Invalidate by TTL, not by delete-fanout.
6. **No heavy CPU in-request**: no sync crypto loops, no big `JSON.parse`, no markdown
   rendering of large docs, no image work. Push to Queues/cron if ever needed (paid tier).

## 6. Anti-Patterns — agents must NEVER

- ❌ Add React/Vue/Svelte, a bundler for the frontend, npm UI packages, or client routers.
- ❌ Return JSON to htmx and rebuild HTML client-side.
- ❌ Use KV for sessions, counters, or anything requiring read-after-write consistency.
- ❌ Use Node APIs (`fs`, `net`, `process.env` at runtime) — Workers runtime only.
  Config comes from `c.env` bindings.
- ❌ Store secrets in code or `wrangler.toml` — Wrangler secrets / `.dev.vars` only.
- ❌ Skip the `HX-Request` branch (breaks deep links) or swap more DOM than targeted.
- ❌ Write `ALTER TABLE`/`DROP` migrations without human review (see ENGINEERING_FLOW §check-ins).
- ❌ Hand-write code a vetted library already provides — but ask the human before adding
  any new dependency (principle #7).

## 7. Free-Tier Budget Sheet (design-time constraints)

| Resource | Free limit | Design rule |
|---|---|---|
| Worker requests | 100k/day | fine for prototypes |
| Worker CPU | 10ms/invocation | ≤5ms budget (§5) |
| D1 reads / writes | 5M / 100k rows/day | paginate; batch writes |
| D1 storage | 5GB | fine |
| KV reads / writes | 100k / 1k per day | **KV writes are scarce** — cache long-TTL fragments only |
| Static assets | free, unlimited requests | self-host all JS/CSS |

## 8. Blindspots Register (accepted risks)

- D1 is single-writer, single-region; no multi-region writes. Acceptable for this suite.
- KV eventual consistency handled by policy (§ cache-only).
- Observability: enable Workers Logs; every route logs `{route, ms, userId?}` on error.
- Rate limiting: none on free tier by default; add a signed-cookie + IP heuristic guard on
  auth endpoints (`lib/oauth.ts`) before public launch.
