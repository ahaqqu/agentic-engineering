# AGENTS.md — Core Directives (loaded every session; keep <900 tokens)

Stack: Hono 4 + TS strict + hono/jsx + Zod on Cloudflare Workers. D1 (SQL truth),
KV (cache ONLY — never sessions/truth). htmx 2 + Alpine 3 + Tailwind 4 + daisyUI 5,
self-hosted static, NO frontend build/npm UI deps. Sessions = HMAC-signed cookies
(HttpOnly/Secure/Lax). Capacitor bundled shell; OAuth via system browser only.

## Hard constraints
1. BDD gate: no `.ts/.tsx/.sql` edits before a `.feature` file + printed plan exist.
   Follow the 4-phase loop in `docs/ENGINEERING_FLOW.md` for every task.
2. 10ms CPU covenant (target ≤5ms): paginate (LIMIT 50), fragment renders only,
   `db.batch()`, hoist schemas/constants to module scope. No CPU-heavy transforms.
3. Boundary matrix: persists-after-refresh → htmx endpoint; ephemeral UI → Alpine.
   Never JSON-to-htmx, never client stores, never SPA drift.
4. Every mutation route: session middleware + `csrf()` + Zod validator + owner filter
   (`WHERE ... session.sub`). Fragments branch on `HX-Request` for deep links.
5. No Node APIs at runtime; env via `c.env`. Secrets via wrangler secrets/`.dev.vars`,
   never code or wrangler.toml.
6. No unit tests. Verification = cucumber-js + Playwright vs `wrangler dev` only.
   Never hand-format; `biome check --write` owns style.
7. New dependency, destructive migration, auth change, or CPU-limit breach → STOP and
   ask the human. Syntax/type/lint/CSS issues → fix autonomously (≤3 self-repair loops).
8. Adopt a one-line persona and a treehouse worktree (`tree <task-slug>`) before work.
9. Keep docs true on every task: update `CODEMAP.md` + the PRD you touched.

## Lazy-loading memory (token budget)
You are FORBIDDEN from guessing historical/architectural patterns. When a task maps to
a known archetype (htmx swap, D1 migration, SSO, caching, mobile, ...):
read `.opencode/skills/index.json`, open ONLY the matching skill file, apply it.
No match → proceed from `docs/` ground truth, then extract a new skill on success per
`.opencode/skills/memory_manager.md`. Read `CODEMAP.md` instead of crawling source.

## Commands
- `pnpm run check`      # biome lint+format (autofix)
- `pnpm run typecheck`  # tsc --noEmit
- `pnpm test`           # cucumber-js + Playwright vs wrangler dev
- `pnpm run dev` · `pnpm run db:migrate:local` · `pnpm run deploy`

## Ground truth (read on demand, not upfront)
`docs/ARCHITECTURE_DEEP_DIVE.md` · `docs/SECURITY_AND_AUTH_RUNBOOK.md` ·
`docs/TESTING_AND_QUALITY_SPEC.md` · `docs/PRODUCT_PLAYBOOK.md` ·
`docs/ENGINEERING_FLOW.md`
