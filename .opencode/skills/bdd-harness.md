# Skill: bdd-harness            (seed · from docs/TESTING_AND_QUALITY_SPEC.md)

## Context
Writing/fixing feature files, steps, hooks, or flaky runs. Tests run against
`pywrangler dev` (workerd) only — no Node shim. No unit tests exist.

## Pattern
```python
# features/conftest.py
@pytest.fixture(scope="session", autouse=True)
def pywrangler_dev():
    subprocess.run(["uv", "run", "pywrangler", "d1", "migrations", "apply", "DB", "--local"])
    proc = subprocess.Popen(["uv", "run", "pywrangler", "dev", "--port", "8787"])
    poll_until_200("http://localhost:8787/health", timeout=30)
    yield
    proc.kill()

@pytest.fixture(autouse=True)
async def reset_db():
    await db_execute("DELETE FROM items")  # via pywrangler d1 execute --local

// auth bypass = cookie injection (NO mock routes):
// api steps → headers: { cookie: await signedInCookie(email), origin: baseURL }
// ui steps  → context.addCookies([…]) before page.goto()

// step layers: @api = fetch + fragment HTML asserts; @ui = Playwright clicks/DOM.
```

## Proof
Self-proving: the harness IS the gate (`uv run pytest` green in CI job `quality`).

## Gotchas
- htmx POST steps must send `origin` header or global `csrf()` rejects with 403.
- Expected-failure check in Phase 2: assert the RED reason (404 route missing), not just red.
- Flaky UI step → prefer `page.waitForSelector` on the swapped fragment's stable DOM id
  over timeouts; htmx swaps have no navigation event.
- Port collisions in CI: derive port from worker index if parallelizing.
