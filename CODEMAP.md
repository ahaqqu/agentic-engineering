# CODEMAP.md — AI-Readable Repository Map

> Read this INSTEAD of crawling the tree (AGENTS.md lazy-loading rule). One line per
> file: path — purpose. Stale entries are defects; update in Phase 4 of every task.

## Repo type
Meta/template repository: ground-truth docs + OpenCode workspace memory for a suite of
Hono/htmx/Cloudflare apps. Contains no application source yet. App repos generated from
this template mirror the `app/` topology defined in docs/ARCHITECTURE_DEEP_DIVE.md §2.

## Files
| Path | Purpose |
|---|---|
| AGENTS.md | Core directives gate, loaded every session (<900 tokens) |
| CODEMAP.md | This map; replaces codebase crawling |
| README.md | Repo intro |
| prompts/*.md | Original meta-prompts that generated docs/ + workspace (historical input) |
| docs/ARCHITECTURE_DEEP_DIVE.md | Stack blueprint, topology, data flow, 10ms covenant, anti-patterns |
| docs/SECURITY_AND_AUTH_RUNBOOK.md | Signed-cookie sessions, CSRF, Google SSO web+mobile, secrets |
| docs/TESTING_AND_QUALITY_SPEC.md | BDD-only gate: cucumber-js+Playwright vs wrangler dev, CI/CD yml |
| docs/PRODUCT_PLAYBOOK.md | Vibe-to-Spec protocol, Agentic PRD template, 10ms checklist, ToDo example |
| docs/ENGINEERING_FLOW.md | 4-phase loop, self-correction (≤3), check-in thresholds, worked example |
| scripts/deploy.sh | Quality-gated e2e deploy (pnpm-only): gates → D1 remote migrations → wrangler deploy → health check |
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
