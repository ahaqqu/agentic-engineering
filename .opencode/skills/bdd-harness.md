# Skill: bdd-harness            (seed · from docs/TESTING_AND_QUALITY_SPEC.md)

## Context
Writing/fixing feature files, steps, hooks, or flaky runs. Tests run against
`wrangler dev` (workerd) only — never a Node shim. No unit tests exist.

## Pattern
```ts
// features/support/hooks.ts
BeforeAll: execSync("wrangler d1 migrations apply DB --local")
           devProc = spawn("wrangler", ["dev", "--port", "8787"])
           await pollUntil200(`${baseURL}/health`, 30_000)
Before:    await resetDb()   // delete+seed via wrangler d1 execute --local
AfterAll:  devProc.kill()

// auth bypass = cookie injection (NO mock routes):
// api steps → headers: { cookie: await signedInCookie(email), origin: baseURL }
// ui steps  → context.addCookies([…]) before page.goto()

// step layers: @api = fetch + fragment HTML asserts; @ui = Playwright clicks/DOM.
```

## Proof
Self-proving: the harness IS the gate (`npm test` green in CI job `quality`).

## Gotchas
- htmx POST steps must send `origin` header or global `csrf()` rejects with 403.
- Expected-failure check in Phase 2: assert the RED reason (404 route missing), not just red.
- Flaky UI step → prefer `page.waitForSelector` on the swapped fragment's stable DOM id
  over timeouts; htmx swaps have no navigation event.
- Port collisions in CI: derive port from worker index if parallelizing.
