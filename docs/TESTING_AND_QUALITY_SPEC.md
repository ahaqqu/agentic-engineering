# TESTING_AND_QUALITY_SPEC.md

> The single quality gate. BDD acceptance tests are the ONLY tests (principle: AI does
> not write unit tests — verification is based on real value delivered). Formatting and
> types are enforced by tools, never by hand.

## 1. Toolchain

| Concern | Tool | Command |
|---|---|---|
| Lint + format | Biome | `pnpm run check` → `biome check --write .` |
| Types | TypeScript strict | `pnpm run typecheck` → `tsc --noEmit` |
| BDD runner | @cucumber/cucumber | `pnpm test` → `cucumber-js` |
| Browser | Playwright (chromium, headless) | driven from step definitions |
| System under test | `wrangler dev` (workerd — the real runtime) | started by test hooks |
| Deploy | `wrangler deploy` | CI only |

`package.json` scripts (canonical — **pnpm is the only supported package manager**;
pin it via the `packageManager` field + corepack):

```json
{
  "packageManager": "pnpm@10.13.1",
  "scripts": {
    "dev": "wrangler dev",
    "check": "biome check --write .",
    "typecheck": "tsc --noEmit",
    "test": "cucumber-js",
    "db:migrate:local": "wrangler d1 migrations apply DB --local",
    "db:migrate:prod": "wrangler d1 migrations apply DB --remote",
    "deploy": "wrangler deploy"
  }
}
```

## 2. Test Architecture

```
features/
├── items_archive.feature          # Gherkin — written BEFORE any code (BDD gate)
├── steps/
│   ├── api.steps.ts               # fetch()-level steps: status, fragment content
│   └── ui.steps.ts                # Playwright steps: real clicks, DOM assertions
└── support/
    ├── world.ts                   # custom World: baseURL, browser page, api client
    └── hooks.ts                   # BeforeAll: migrate local D1 + seed + start wrangler dev
                                   # Before: reset data; After: teardown
```

Two step layers, one feature file. `@api` scenarios assert over-the-wire HTML fragments
(fast); `@ui` scenarios assert real browser behavior through htmx swaps (truth).

## 3. Gherkin Boilerplate (reference shape)

```gherkin
Feature: Archive items
  Signed-in users archive items without losing them.

  Background:
    Given I am signed in as "ada@example.com"
    And an item "Buy milk" exists

  @api
  Scenario: Archive endpoint returns the updated row fragment
    When I POST to the archive endpoint for "Buy milk"
    Then the response status is 200
    And the response HTML contains an element "[data-archived='true']"

  @ui
  Scenario: Toggling archive updates the row without a page reload
    When I open the items page
    And I click the archive button on "Buy milk"
    Then the row for "Buy milk" shows the archived badge
    And the page did not perform a full navigation
```

## 4. SSO Bypass — Signed-Cookie Injection (no mock routes)

`.dev.vars` (local + CI): `SESSION_SECRET=test-secret-do-not-use-in-prod`

```ts
// features/support/auth.ts — signs a cookie EXACTLY like lib/session.ts does
import { makeSessionCookie } from "../../src/lib/session";

export async function signedInCookie(email: string): Promise<string> {
  return makeSessionCookie(
    { sub: `test-${email}`, email, name: "Test User" },
    "test-secret-do-not-use-in-prod",
  );
}
```

- API steps: send the cookie in the `Cookie` header.
- UI steps: `await context.addCookies([...])` before `page.goto()`.
- Production is unaffected: same code path, different secret, no test-only routes exist.

## 5. Local Runtime Hooks

```ts
// features/support/hooks.ts (essentials)
BeforeAll: 
  execSync("wrangler d1 migrations apply DB --local")
  devProc = spawn("wrangler", ["dev", "--port", "8787"]) // poll /health until 200
Before:
  await resetDb()          // delete+seed via a d1 execute against --local
After / AfterAll:
  await page?.close(); devProc.kill()
```

Rule: tests run against **workerd**, never a Node shim — runtime parity is the point.

## 6. CI/CD — `.github/workflows/ci-cd.yml`

```yaml
name: ci-cd
on:
  push: { branches: [main] }
  pull_request:

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec biome ci .
      - run: pnpm run typecheck
      - run: pnpm exec playwright install --with-deps chromium
      - run: echo "SESSION_SECRET=test-secret-do-not-use-in-prod" > .dev.vars
      - run: pnpm test

  deploy:
    needs: quality
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: pnpm }
      - run: pnpm install --frozen-lockfile
      - run: pnpm exec wrangler d1 migrations apply DB --remote
        env: { CLOUDFLARE_API_TOKEN: "${{ secrets.CLOUDFLARE_API_TOKEN }}" }
      - run: pnpm exec wrangler deploy
        env: { CLOUDFLARE_API_TOKEN: "${{ secrets.CLOUDFLARE_API_TOKEN }}" }
```

## 7. Definition of Done (agent self-check before declaring complete)

1. `pnpm run check` — zero diagnostics.
2. `pnpm run typecheck` — zero errors.
3. `pnpm test` — 100% scenarios green against `wrangler dev`.
4. Feature file exists and predates the implementation (BDD gate).
5. Docs updated: `CODEMAP.md` entry + PRD endpoint matrix row (principle #4).
6. If all green → extract skill per `.opencode/skills/memory_manager.md`.
