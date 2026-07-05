# TESTING_AND_QUALITY_SPEC.md

> The single quality gate. BDD acceptance tests are the ONLY tests. Formatting and
> types are enforced by tools, never by hand.

## 1. Toolchain

| Concern | Tool | Command |
|---|---|---|
| Lint | Ruff | `uv run ruff check src/ features/` |
| Format | Ruff | `uv run ruff format --check src/ features/` |
| Autofix | Ruff | `uv run ruff check --fix src/ features/` |
| Types | Pyright | `uv run pyright` |
| BDD runner | pytest-bdd | `uv run pytest` |
| Browser | Playwright (chromium, headless) | driven from step definitions |
| System under test | `pywrangler dev` (workerd — the real runtime) | started by conftest.py |
| Deploy | `pywrangler deploy` | CI only |

uv is the canonical package manager. Run everything through `uv run`.

```toml
# pyproject.toml scripts (canonical)
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["features"]
```

## 2. Test Architecture

```
features/
├── items_archive.feature          # Gherkin — written BEFORE any code (BDD gate)
├── steps/
│   └── test_items_archive.py      # pytest-bdd step definitions: API + UI steps
└── conftest.py                    # fixtures: pywrangler dev lifecycle, browser, cookies
```

All scenarios use either `@api` (assert HTML fragments over HTTP) or `@ui` (assert real
browser behaviour through htmx swaps). pytest-bdd supports these as module-level markers.

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

```python
# features/conftest.py — signs a cookie EXACTLY like src/lib/session.py does
from src.lib.session import sign_token, make_payload


def signed_cookie(email: str) -> str:
    payload = make_payload(f"test-{email}", email, "Test User")
    return sign_token(payload, "test-secret-do-not-use-in-prod")
```

- API steps: send the cookie in the `Cookie` header.
- UI steps: `await context.add_cookies([...])` before `page.goto()`.
- Production is unaffected: same code path, different secret, no test-only routes exist.

## 5. Local Runtime Hooks

```python
# features/conftest.py (essentials)
@pytest.fixture(scope="session", autouse=True)
def server():
    # Apply migrations
    subprocess.run(["uv", "run", "pywrangler", "d1", "migrations", "apply", "DB", "--local"])
    # Start dev server
    proc = subprocess.Popen(["uv", "run", "pywrangler", "dev", "--port", "8787"])
    _wait_for_health("http://localhost:8787/health")
    yield
    proc.terminate()
```

Before each scenario:
```python
@pytest.fixture(autouse=True)
def reset_db():
    subprocess.run(
        ["uv", "run", "pywrangler", "d1", "execute", "DB", "--local",
         "--command", "DELETE FROM items;"]
    )
```

Rule: tests run against **workerd**, never a Python shim — runtime parity is the point.

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
      - uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          enable-cache: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: "pip"
      - run: uv sync
      - run: uv run ruff check src/ features/
      - run: uv run pyright
      - run: uv run playwright install --with-deps chromium
      - run: echo "SESSION_SECRET=test-secret-do-not-use-in-prod" > .dev.vars
      - run: uv run pytest

  deploy:
    needs: quality
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          version: "latest"
          enable-cache: true
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: "pip"
      - run: uv sync
      - run: uv run pywrangler d1 migrations apply DB --remote
        env: { CLOUDFLARE_API_TOKEN: "${{ secrets.CLOUDFLARE_API_TOKEN }}" }
      - run: uv run pywrangler deploy
        env: { CLOUDFLARE_API_TOKEN: "${{ secrets.CLOUDFLARE_API_TOKEN }}" }
```

## 7. Definition of Done (agent self-check before declaring complete)

1. `uv run ruff check src/ features/` — zero diagnostics.
2. `uv run ruff format --check src/ features/` — zero formatting issues.
3. `uv run pyright` — zero errors.
4. `uv run pytest` — 100% scenarios green against `pywrangler dev`.
5. Feature file exists and predates the implementation (BDD gate).
6. Docs updated: `CODEMAP.md` entry + PRD endpoint matrix row.
7. If all green → extract skill per `.opencode/skills/memory_manager.md`.
8. **PR created** per `.opencode/skills/pr-creation.md` — PR body includes all BDD
   proof, check-in notes, and self-correction ledger entries.
