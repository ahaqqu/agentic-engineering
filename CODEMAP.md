# CODEMAP.md — AI-Readable Repository Map

> Read this INSTEAD of crawling the tree (AGENTS.md lazy-loading rule). One line per
> file: path — purpose. Stale entries are defects; update in Phase 4 of every task.

## Repo type
Meta/template repository with validated scaffolding: ground-truth docs + OpenCode workspace
memory + verified FastAPI/Python app skeleton for a suite of Cloudflare Workers apps.

## Source files
| Path | Purpose |
|---|---|
| src/entry.py | Python Worker entrypoint: WorkerEntrypoint → asgi.fetch(app, request, env) |
| src/app.py | FastAPI app: middleware, dependencies, route mounting |
| src/routes/items.py | `POST /items` (Pydantic `ItemCreateBody`), `POST /items/{item_id}/archive` — item CRUD + archive toggle |
| src/lib/session.py | HMAC-SHA256 signed-cookie tokens, session middleware, require_session dependency |
| src/lib/csrf.py | Origin-check CSRF dependency for mutation routes |
| src/db/items.py | D1 query helpers: Item model, typed query functions with owner filters |
| src/schemas/items.py | Pydantic models: ItemResponse, ItemCreateBody |
| src/templates.py | Module-scoped Jinja2 environment (FastAPI Jinja2Templates) |
| src/templates/layout.html | Full-page shell: DOCTYPE, htmx script, title, includes item_list |
| src/templates/item_list.html | `<ul id="item-list">` loop over items, renders item_row |
| src/templates/item_row.html | Single `<li>` fragment with archive button, hx-post swap target |
| migrations/0001_init.sql | Items table (user_id, title, done) |
| migrations/0002_items_archived.sql | Additive migration: items gain `archived INTEGER NOT NULL DEFAULT 0` |
| features/items_archive.feature | BDD feature: archive toggle, auth guards, refresh survival |
| features/steps/test_items_archive.py | pytest-bdd step definitions: API + UI steps |
| features/template_defects.feature | BDD feature: Pydantic validation on create + additive migration safety |
| features/steps/test_template_defects.py | pytest-bdd step definitions: create-item validation + migration smoke test |
| features/workflow.feature | BDD feature: workflow scripts exist and pytest markers are registered |
| features/steps/test_workflow.py | pytest-bdd step definitions: file-existence, exit-code, marker-listing steps |
| features/conftest.py | pytest fixtures: pywrangler dev lifecycle, DB reset, Playwright browsers, signed cookies; uses `uv` from PATH |
| public/htmx.min.js | Self-hosted htmx 2.x (no CDN dependency for Capacitor offline) |
| public/app.css | Application stylesheet (placeholder) |

## Docs
| Path | Purpose |
|---|---|
| docs/ARCHITECTURE_DEEP_DIVE.md | Stack blueprint, topology, data flow, 10ms covenant, anti-patterns |
| docs/SECURITY_AND_AUTH_RUNBOOK.md | Signed-cookie sessions, CSRF, Google SSO web+mobile, secrets |
| docs/TESTING_AND_QUALITY_SPEC.md | BDD-only gate: pytest-bdd + Playwright vs pywrangler dev |
| docs/PRODUCT_PLAYBOOK.md | Vibe-to-Spec protocol, Agentic PRD template, 10ms checklist, ToDo example |
| docs/ENGINEERING_FLOW.md | 4-phase loop, self-correction (≤3), check-in thresholds, worked example |

## OpenCode workspace
| Path | Purpose |
|---|---|
| AGENTS.md | Core directives gate, loaded every session (<900 tokens) |
| CODEMAP.md | This map; replaces codebase crawling |
| scripts/deploy.sh | Quality-gated e2e deploy: gates → D1 → pywrangler → health |
| scripts/bootstrap-worktree.sh | Copies .dev.vars from main checkout to a new git worktree |
| scripts/ensure-wrangler.sh | Checks/upgrades global wrangler to the minimum required version |
| scripts/test.sh | Single-command gate: wrangler check → kill stale servers → ruff → pyright → pytest |
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
| .opencode/skills/no-mistakes.md | Validation gate: review, test, lint, docs, PR, CI — use only when explicitly invoked |

## Config root files
| Path | Purpose |
|---|---|
| pyproject.toml | Python project: FastAPI/Jinja2 deps, dev deps (pytest-bdd, ruff, pyright, workers-py), ruff/pyright config |
| wrangler.toml | Cloudflare Workers config: D1 binding, static assets, Python entry + python_workers flag |
| .dev.vars | Local secrets (gitignored): SESSION_SECRET |
| .gitignore | .venv, .wrangler, .dev.vars, logs, __pycache__ |
