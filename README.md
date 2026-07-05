# agentic-engineering

AI-first application factory for Hono/TypeScript + htmx on Cloudflare Workers.
Generate, validate, and deploy hypermedia-driven PWAs — with AI agents writing 99% of the code.

---

## For developers — using the agentic flow

Every feature follows the same deterministic loop. The agent plans, implements, and verifies itself; you design and review.

### Quick start

```bash
pnpm install
pnpm exec wrangler d1 migrations apply DB --local
pnpm exec playwright install chromium      # one-time
pnpm dev                                    # http://localhost:8787
pnpm test                                   # BDD suite vs wrangler dev
```

### How to build a feature

1. Write a **one-line task** (e.g. "Add archive toggle to items, daisyUI button, htmx POST").
2. The agent runs the **[4-phase Engineering Flow](docs/ENGINEERING_FLOW.md)**: prints a plan → writes `.feature` file → implements → self-verifies.
3. Agent creates a **[standardized PR](.opencode/skills/pr-creation.md)** with: architecture changes, BDD proof, security/performance review, and check-in notes.
4. You review the PR — not the code line-by-line, but the behavioural proof + checklists.

### Key docs for agent guidance

| File | Purpose |
|---|---|
| [AGENTS.md](AGENTS.md) | Core directives loaded every agent session (hard constraints, commands) |
| [docs/ENGINEERING_FLOW.md](docs/ENGINEERING_FLOW.md) | The 4-phase deterministic loop every task must follow |
| [docs/PRODUCT_PLAYBOOK.md](docs/PRODUCT_PLAYBOOK.md) | Vibe-to-Spec protocol + Agentic PRD template |
| [docs/ARCHITECTURE_DEEP_DIVE.md](docs/ARCHITECTURE_DEEP_DIVE.md) | Stack blueprint, data flow, 10ms CPU covenant |
| [docs/TESTING_AND_QUALITY_SPEC.md](docs/TESTING_AND_QUALITY_SPEC.md) | BDD-only quality gate, CI/CD spec |
| [CODEMAP.md](CODEMAP.md) | AI-readable source map (never crawl the tree) |
| [.opencode/skills/](.opencode/skills/) | Lazy-load skill library: session auth, D1 migrations, htmx swaps, PR creation |

### Stack constraints (agent-enforced)

- **No build step.** htmx + Alpine + Tailwind (via CDN or self-hosted static assets). No npm UI packages, no bundlers.
- **No JSON-to-htmx.** State that survives refresh is owned by the server; ephemeral UI is Alpine. Never client stores, never SPA drift.
- **No KV sessions.** HMAC-signed cookies only. KV is cache — eventually consistent (<60s).
- **10ms CPU budget.** Paginate everything (LIMIT 50), fragment renders only, `db.batch()`, module-scope schemas.

---

## For cloud ops — deploying changes

### Architecture overview

```
[Browser / Capacitor shell]
        │ htmx (AJAX) or full-page load
        ▼
[Cloudflare Worker — Hono]
        ├── D1 (SQLite — source of truth)
        ├── KV (cache only — fragment HTML, JWKS)
        └── Static Assets (htmx.js, CSS, icons)
```

### Prerequisites

- Cloudflare account with Workers paid (or free) plan
- D1 database created: `pnpm exec wrangler d1 create <db-name>`
- Secrets set: `pnpm exec wrangler secret put SESSION_SECRET`

### Deploy

```bash
# Full quality-gated deploy (biome → tsc → BDD tests → D1 migrations → wrangler deploy)
./scripts/deploy.sh

# Or step by step:
pnpm check
pnpm typecheck
pnpm test                                             # requires wrangler dev running
pnpm exec wrangler d1 migrations apply DB --remote    # prod D1
pnpm exec wrangler deploy                             # prod worker
```

The deploy script (`scripts/deploy.sh`) runs the exact same gates as CI. It auto-detects whether `CLOUDFLARE_API_TOKEN` or a local `wrangler login` session is available.

### Environment configuration

| Setting | Where | Example |
|---|---|---|
| `SESSION_SECRET` | `.dev.vars` (local) / `wrangler secret put` (prod) | 32-byte random hex |
| `GOOGLE_CLIENT_ID` | same | from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | same | from Google Cloud Console |
| `database_id` | `wrangler.toml` → `[[d1_databases]]` | UUID from `wrangler d1 create` |

### CI/CD

See [docs/TESTING_AND_QUALITY_SPEC.md](docs/TESTING_AND_QUALITY_SPEC.md) §6 for the full
GitHub Actions workflow (quality gate → deploy).

### Mobile (Capacitor)

This app uses a **bundled Capacitor shell** (not a remote-URL wrapper — avoids App Store
Rejection 4.2). The shell ships local assets (splash, offline fallback, htmx/css) and
loads app content from the production origin after auth. OAuth uses the system browser
(Custom Tabs / ASWebAuthenticationSession), never an in-app WebView.

See [docs/SECURITY_AND_AUTH_RUNBOOK.md](docs/SECURITY_AND_AUTH_RUNBOOK.md) §3 for the
full mobile auth handoff.

---

## License

MIT
