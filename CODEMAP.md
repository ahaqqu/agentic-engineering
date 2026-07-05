# CODEMAP.md — AI-Readable Repository Map

> Read this INSTEAD of crawling the tree (AGENTS.md lazy-loading rule). One line per
> file: path — purpose. Stale entries are defects; update in Phase 4 of every task.

## Repo type
Meta/template repository with validated scaffolding: ground-truth docs + OpenCode workspace
memory + verified Hono/htmx app skeleton for a suite of Cloudflare Workers apps.

## Source files
| Path | Purpose |
|---|---|
| src/index.tsx | Hono app entry point: routes, layout, ItemRow fragment |
| src/routes/health.ts | `GET /health` — liveness check for BDD harness |
| src/routes/items.tsx | `POST /items`, `POST /items/:id/archive` — item CRUD + archive toggle |
| src/lib/session.ts | HMAC-SHA256 signed-cookie tokens, session/requireSession middleware |
| migrations/0001_init.sql | Items table (user_id, title, done, archived) |
| migrations/0002_items_archived.sql | Fix: removed FK constraint (auth is session-based) |
| features/items_archive.feature | BDD feature: archive toggle, auth guards, refresh survival |
| features/steps/api.steps.ts | API steps: signed-in cookie injection, POST, status assertions |
| features/steps/ui.steps.ts | UI steps: Playwright browser, archive click, badge assert, reload |
| features/support/world.ts | Custom cucumber-js World (MyWorld interface) |
| features/support/hooks.ts | BeforeAll/AfterAll: wrangler dev lifecycle; Before: DB reset; After: browser teardown |
| features/support/auth.ts | Session cookie generation using shared src/lib/session.ts |
| public/htmx.min.js | Self-hosted htmx 2.x (no CDN dependency for Capacitor offline) |
| public/app.css | Application stylesheet (placeholder) |

## Docs
| Path | Purpose |
|---|---|
| docs/ARCHITECTURE_DEEP_DIVE.md | Stack blueprint, topology, data flow, 10ms covenant, anti-patterns |
| docs/SECURITY_AND_AUTH_RUNBOOK.md | Signed-cookie sessions, CSRF, Google SSO web+mobile, secrets |
| docs/TESTING_AND_QUALITY_SPEC.md | BDD-only gate: cucumber-js+Playwright vs wrangler dev, CI/CD yml |
| docs/PRODUCT_PLAYBOOK.md | Vibe-to-Spec protocol, Agentic PRD template, 10ms checklist, ToDo example |
| docs/ENGINEERING_FLOW.md | 4-phase loop, self-correction (≤3), check-in thresholds, worked example |

## OpenCode workspace
| Path | Purpose |
|---|---|
| AGENTS.md | Core directives gate, loaded every session (<900 tokens) |
| CODEMAP.md | This map; replaces codebase crawling |
| scripts/deploy.sh | Quality-gated e2e deploy (pnpm-only): gates → D1 → wrangler → health |
| .opencode/skills/index.json | Lazy-load map: task archetype → skill file |
| .opencode/skills/template_blueprint.md | Mandatory structure for extracted skills |
| .opencode/skills/memory_manager.md | Hermes loop: extraction, compaction, ledger, CODEMAP upkeep |
| .opencode/skills/lessons.md | Self-correction ledger (staging; rules promoted then deleted) |
| .opencode/skills/htmx-fragment-swap.md | Seed skill: persistent-state fragment swap pattern |
| .opencode/skills/d1-migration.md | Seed skill: additive migrations, destructive-change gate |
| .opencode/skills/sso-auth.md | Seed skill: session/guard/OAuth patterns |
| .opencode/skills/kv-fragment-cache.md | Seed skill: TTL fragment cache, poisoning guards |
| .opencode/skills/mobile-capacitor.md | Seed skill: bundled shell, deep-link OAuth handoff |
| .opencode/skills/bdd-harness.md | Seed skill: hooks, cookie-injection bypass, flake fixes |
| .opencode/skills/pr-creation.md | PR skill: summary, architecture changes, BDD behavioural proof, security/performance/docs checklists, manual test list, engineering flow changes, limitations |

## Config root files
| Path | Purpose |
|---|---|
| package.json | pnpm-only, scripts: dev/check/typecheck/test/deploy/db:migrate |
| wrangler.toml | Cloudflare Workers config: D1 binding, static assets, TSX entry |
| tsconfig.json | Strict TS for src/ with hono/jsx |
| tsconfig.features.json | Strict TS for features/ + shared session lib |
| biome.json | Lint + format config (preset: recommended) |
| cucumber.cjs | Cucumber-js config: tsx loader, support/steps paths |
| .dev.vars | Local secrets (gitignored): SESSION_SECRET |
| .gitignore | node_modules, .wrangler, .dev.vars, logs |
