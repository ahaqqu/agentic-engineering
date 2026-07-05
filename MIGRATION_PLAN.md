# Migration Plan: Hono/TypeScript → FastAPI/Python on Cloudflare Workers

> **Status:** Plan (ready for implementation session)
> **Slug:** `python-fastapi-migration`
> **Persona:** Hypermedia backend engineer
>
## Overview

Migrate the existing Hono 4 + TypeScript Cloudflare Worker to a native Python Worker using **FastAPI** (via the built-in ASGI adapter), **Jinja2** for HTML templating, while keeping D1, signed-cookie sessions, htmx, and static assets. The BDD suite moves from **cucumber-js to pytest-bdd**.

**Dropped:** Better Auth (incompatible with Python), Hyperdrive (not needed without Postgres), Node.js test harness.

### What stays

- D1 database (schema, queries, owner filters)
- HMAC-SHA256 signed-cookie sessions (ported to Python stdlib)
- htmx 2 + Alpine 3 + Tailwind CSS + daisyUI 5 (via self-hosted static files)
- All static assets (`public/`)
- Existing D1 migrations (`migrations/`)
- Gherkin `.feature` files (unchanged)
- `wrangler.toml` (updated for Python entry, python_workers flag)

### What goes

- `src/index.tsx`, `src/routes/*.tsx`, `src/lib/session.ts`
- `package.json`, `biome.json`, `tsconfig*.json`, `cucumber.cjs`
- `features/support/*.ts`, `features/steps/*.ts`
- `.dev.vars` kept but `SESSION_SECRET` repurposed

### What is added

- `pyproject.toml` with runtime deps (FastAPI, Jinja2, etc.) and dev deps (workers-py, pytest-bdd, ruff, pyright)
- `src/entry.py` — Worker entrypoint (WorkerEntrypoint → asgi.fetch)
- `src/app.py` — FastAPI app, middleware, routes
- `src/lib/session.py` — HMAC sign/verify, middleware, dependencies
- `src/lib/csrf.py` — CSRF origin-check dependency
- `src/db/items.py` — D1 query helpers
- `src/schemas/items.py` — Pydantic models
- `src/templates/` — Jinja2 templates (layout, item_list, item_row)
- `src/templates.py` — module-scoped Jinja2 environment
- `features/conftest.py` — pytest fixtures (server, db reset, browser, cookies)
- `features/steps/test_items_archive.py` — pytest-bdd step definitions
- `.opencode/skills/no-mistakes.md` — skill file
- `.venv/` — local workspace venv with uv + workers-py

---

## 1. File-by-file implementation guide

### 1.1 `pyproject.toml`

```toml
[project]
name = "agentic-engineering"
version = "0.2.0"
description = "AI-first application factory for FastAPI/Python + htmx on Cloudflare Workers."
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115.0",
    "jinja2>=3.1.0",
    "python-multipart>=0.0.9",
]

[dependency-groups]
dev = [
    "workers-py>=1.5.0",
    "workers-runtime-sdk>=1.5.0",
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-bdd>=8.0.0",
    "playwright>=1.50.0",
    "ruff>=0.7.0",
    "pyright>=1.1.380",
]

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.format]
quote-style = "double"

[tool.pyright]
include = ["src", "features"]
pythonVersion = "3.13"
typeCheckingMode = "strict"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["features"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 1.2 `wrangler.toml`

```toml
name = "agentic-engineering-template"
main = "src/entry.py"
compatibility_date = "2026-07-05"
compatibility_flags = ["python_workers"]

[assets]
directory = "public"

[[d1_databases]]
binding = "DB"
database_name = "app-db"
database_id = "00000000-0000-0000-0000-000000000000"
```

### 1.3 `src/entry.py` — Worker entrypoint

```python
from workers import WorkerEntrypoint
import asgi
from app import app


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request, self.env)
```

Pattern: The ASGI adapter from `workers` runtime SDK takes the FastAPI app, the JS Request, and the env. Keep this file minimal — no logic.

### 1.4 `src/app.py` — FastAPI application

```python
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from routes.items import router as items_router
from lib.session import SessionMiddleware, require_session
from lib.csrf import csrf_check
from templates import templates

app = FastAPI()

# --- Global middleware ---
app.add_middleware(SessionMiddleware)

# --- CSRF applied selectively on mutation routes ---
# FastAPI routers handle this via dependencies; see csrf.py

# --- Routes ---

@app.get("/health", response_class=PlainTextResponse)
async def health():
    return "ok"


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, session=Depends(require_session)):
    items = await db.items.list_all(request.state.db, session["sub"])
    return templates.TemplateResponse(
        "layout.html",
        {"request": request, "items": items, "user": session},
    )


# Mount items routes
app.include_router(items_router, prefix="/items")
```

Notes:
- `SessionMiddleware` is a custom ASGI middleware (not FastAPI's `BaseHTTPMiddleware` because we need to set `request.state.session`). See 1.5.
- The `/` endpoint returns a full page. For htmx deep links (`HX-Request` header), branch: if `HX-Request` is present, return only the `item_list.html` fragment. Use a helper `hx_branch` to detect.
- All mutation routes use `Depends(require_session)` and `Depends(csrf_check)`.
- DB instance accessed via `request.state.db` which is injected by middleware.
- Templates are loaded at module scope from `templates.py`.

### 1.5 `src/lib/session.py` — Session handling

**Port from the existing TS implementation exactly:** HMAC-SHA256 with base64url encoding. The signature format must be identical so that existing session cookies remain valid (or for test cookie compatibility across sessions).

```python
import hmac
import hashlib
import base64
import json
import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse


COOKIE_NAME = "session"
SESSION_TTL = 7 * 86400  # 7 days


def to_b64(data: dict) -> str:
    """URL-safe base64 without padding."""
    payload = json.dumps(data, separators=(",", ":"))
    return base64.urlsafe_b64encode(payload.encode()).rstrip(b"=").decode()


def from_b64(raw: str) -> dict | None:
    """Decode URL-safe base64 with padding restored."""
    padded = raw + "=" * (4 - len(raw) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(padded))
    except Exception:
        return None


def sign_token(payload: dict, secret: str) -> str:
    """Create a signed token: base64(payload).hmac."""
    encoded = to_b64(payload)
    sig = hmac.new(
        secret.encode(), encoded.encode(), hashlib.sha256
    ).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    return f"{encoded}.{sig_b64}"


def verify_token(token: str, secret: str) -> dict | None:
    """Verify signed token and return payload or None."""
    parts = token.rsplit(".", 1)
    if len(parts) != 2:
        return None
    encoded, sig_b64 = parts
    sig = base64.urlsafe_b64decode(
        sig_b64 + "=" * (4 - len(sig_b64) % 4)
    )
    expected = hmac.new(
        secret.encode(), encoded.encode(), hashlib.sha256
    ).digest()
    if not hmac.compare_digest(sig, expected):
        return None
    payload = from_b64(encoded)
    if not payload or "sub" not in payload:
        return None
    # Check expiry
    if payload.get("exp", 0) < time.time():
        return None
    return payload


def make_payload(sub: str, email: str, name: str) -> dict:
    now = int(time.time())
    return {"sub": sub, "email": email, "name": name, "iat": now, "exp": now + SESSION_TTL}


def _get_secret(request: Request) -> str:
    """Read SESSION_SECRET from the worker env."""
    try:
        return request.scope["env"].SESSION_SECRET or "insecure-dev-default"
    except AttributeError:
        return "insecure-dev-default"


class SessionMiddleware(BaseHTTPMiddleware):
    """
    Starlette middleware that reads the session cookie and
    puts the payload in request.state.session.
    """

    async def dispatch(self, request: Request, call_next):
        raw = request.cookies.get(COOKIE_NAME)
        session = None
        if raw:
            secret = _get_secret(request)
            session = verify_token(raw, secret)
        request.state.session = session
        response = await call_next(request)
        return response


async def require_session(request: Request) -> dict:
    """FastAPI dependency: returns session or raises 401."""
    session = getattr(request.state, "session", None)
    if not session:
        if request.headers.get("HX-Request") == "true":
            from fastapi.responses import Response
            raise HTTPException(
                status_code=401,
                detail="Unauthorized",
                headers={"HX-Redirect": "/auth/login"},
            )
        raise HTTPException(status_code=302, headers={"Location": "/auth/login"})
    return session
```

Key points:
- `sign_token` / `verify_token` match the existing TS implementation exactly.
- `make_payload` generates the standard session payload.
- `SessionMiddleware` populates `request.state.session` on every request (no DB lookups).
- `require_session` returns the session dict or raises (htmx-aware).
- `_get_secret` reaches into the request scope's `env` binding. This requires the `asgi.fetch` call to pass `env` into the scope (which the workers ASGI adapter does — see examples).

### 1.6 `src/lib/csrf.py`

```python
from fastapi import Request, HTTPException, Depends


async def csrf_check(request: Request):
    """Reject state-changing requests without a matching Origin header."""
    if request.method in ("GET", "HEAD", "OPTIONS"):
        return
    origin = request.headers.get("Origin")
    if not origin:
        raise HTTPException(status_code=403, detail="CSRF: missing Origin")
    # Accept any origin in dev — in production, restrict to your domain
    # For tests, Origin is set to the base URL.
    host = request.headers.get("Host", "")
    if origin not in [f"http://{host}", f"https://{host}"]:
        raise HTTPException(status_code=403, detail="CSRF: Origin mismatch")
```

In production you may want to restrict to an explicit `BASE_URL` env var. The current Hono `csrf()` middleware accepts any Origin as long as it is present, so this is equivalent.

### 1.7 `src/db/items.py`

```python
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    title: str
    done: bool = False
    archived: bool = False


class ItemCreate(BaseModel):
    title: str


class DB:
    """Wrapper around the D1 binding for typed queries."""

    def __init__(self, d1):
        self._d1 = d1

    async def list_all(self, user_sub: str) -> list[Item]:
        stmt = self._d1.prepare(
            "SELECT id, title, done, archived FROM items "
            "WHERE user_id = ? ORDER BY created_at DESC LIMIT 50"
        ).bind(user_sub)
        result = await stmt.all()
        return [Item(**row) for row in (result.results or [])]

    async def create(self, user_sub: str, title: str) -> Item | None:
        stmt = self._d1.prepare(
            "INSERT INTO items (user_id, title) VALUES (?, ?) "
            "RETURNING id, title, done, archived"
        ).bind(user_sub, title)
        row = await stmt.first()
        return Item(**row) if row else None

    async def toggle_archive(self, item_id: int, user_sub: str) -> Item | None:
        stmt = self._d1.prepare(
            "UPDATE items SET archived = 1 - archived "
            "WHERE id = ? AND user_id = ? "
            "RETURNING id, title, done, archived"
        ).bind(item_id, user_sub)
        row = await stmt.first()
        return Item(**row) if row else None
```

**Note:** The DB instance should be created per-request from the environment binding. We can get the D1 binding from `request.scope["env"].DB`. A convenience function:

```python
async def get_db(request: Request) -> DB:
    env = request.scope["env"]
    return DB(env.DB)
```

Or inject the DB into request.state inside the SessionMiddleware (or a separate middleware). For simplicity, each route can get `DB` directly.

### 1.8 `src/schemas/items.py`

```python
from pydantic import BaseModel, Field


class ItemResponse(BaseModel):
    id: int
    title: str
    done: bool
    archived: bool


class ItemCreateBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
```

### 1.9 `src/templates.py` — Jinja2 environment

```python
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = Path(__file__).parent / "templates"

templates = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=True,
)

# Make it available for FastAPI TemplateResponse
from fastapi.templating import Jinja2Templates

# Re-export for use in routes
jinja_templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
```

We use FastAPI's `Jinja2Templates` for convenience with `request` context injection.

### 1.10 Templates

#### `src/templates/layout.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Items</title>
  <link href="/app.css" rel="stylesheet" />
  <script src="/htmx.min.js"></script>
</head>
<body class="p-4 max-w-lg mx-auto">
  <h1 class="text-xl font-bold mb-4">Items</h1>
  {% include "item_list.html" %}
</body>
</html>
```

#### `src/templates/item_list.html`

```html
<ul id="item-list" class="space-y-2">
  {% for item in items %}
    {% include "item_row.html" %}
  {% else %}
    <li class="text-gray-500">No items yet.</li>
  {% endfor %}
</ul>
```

#### `src/templates/item_row.html`

```html
<li id="item-{{ item.id }}" class="flex items-center gap-2 py-2" data-archived="{{ 'true' if item.archived else 'false' }}">
  <span class="flex-1 {{ 'line-through opacity-50' if item.archived else '' }}">{{ item.title }}</span>
  {% if item.archived %}
    <span class="badge">archived</span>
  {% endif %}
  <button type="button" class="btn btn-sm"
    hx-post="/items/{{ item.id }}/archive"
    hx-target="#item-{{ item.id }}"
    hx-swap="outerHTML">
    {{ "Unarchive" if item.archived else "Archive" }}
  </button>
</li>
```

### 1.11 Routes (`src/routes/items.py`)

```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from lib.session import require_session
from lib.csrf import csrf_check
from schemas.items import ItemCreateBody
from db.items import DB
from templates import jinja_templates

router = APIRouter(dependencies=[Depends(require_session), Depends(csrf_check)])


def _get_db(request: Request) -> DB:
    return DB(request.scope["env"].DB)


@router.post("", response_class=HTMLResponse, status_code=201)
async def create_item(
    request: Request,
    body: ItemCreateBody,
    session: dict = Depends(require_session),
    db: DB = Depends(_get_db),
):
    item = await db.create(session["sub"], body.title)
    if not item:
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse("create failed", status_code=500)
    return jinja_templates.TemplateResponse(
        "item_row.html", {"request": request, "item": item}
    )


@router.post("/{item_id}/archive", response_class=HTMLResponse)
async def archive_item(
    request: Request,
    item_id: int,
    session: dict = Depends(require_session),
    db: DB = Depends(_get_db),
):
    item = await db.toggle_archive(item_id, session["sub"])
    if not item:
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse("not found", status_code=404)
    return jinja_templates.TemplateResponse(
        "item_row.html", {"request": request, "item": item}
    )
```

### 1.12 Test harness: `features/conftest.py`

```python
import asyncio
import os
import subprocess
import time
from pathlib import Path

import pytest
import pytest_asyncio
from playwright.async_api import async_playwright

from lib.session import sign_token, make_payload

BASE_PORT = 8787
BASE_URL = f"http://localhost:{BASE_PORT}"
SESSION_SECRET = os.environ.get("SESSION_SECRET", "test-secret-do-not-use-in-prod")
PROJECT_ROOT = Path(__file__).parent.parent


def _signed_cookie(email: str) -> str:
    payload = make_payload(f"test-{email}", email, "Test User")
    return sign_token(payload, SESSION_SECRET)


def _wait_for_health(url: str, timeout: int = 60) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(url, timeout=5)
            if resp.ok:
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise TimeoutError(f"Health check timed out after {timeout}s")


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def server():
    """Start pywrangler dev before the test session."""
    # Apply migrations
    subprocess.run(
        ["uv", "run", "pywrangler", "d1", "migrations", "apply", "DB", "--local"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    # Start dev server
    proc = subprocess.Popen(
        ["uv", "run", "pywrangler", "dev", "--port", str(BASE_PORT)],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _wait_for_health(f"{BASE_URL}/health")
    yield
    proc.terminate()
    proc.wait()


@pytest.fixture(autouse=True)
def reset_db():
    """Delete all items before each scenario."""
    subprocess.run(
        [
            "uv", "run", "pywrangler", "d1", "execute", "DB", "--local",
            "--command", "DELETE FROM items;",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def session():
    return {}


@pytest.fixture
def signed_cookie():
    def _cookie(email: str) -> str:
        return _signed_cookie(email)
    return _cookie


@pytest_asyncio.fixture
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        yield browser
        await browser.close()


@pytest_asyncio.fixture
async def page(browser, signed_cookie):
    context = await browser.new_context(ignore_https_errors=True, base_url=BASE_URL)
    page = await context.new_page()
    yield page
    await context.close()
```

### 1.13 Test steps: `features/steps/test_items_archive.py`

```python
import pytest
from pytest_bdd import given, when, then, scenario, parsers
import httpx


@scenario("../items_archive.feature", "Archive endpoint returns the updated row fragment")
def test_archive_api():
    pass


@scenario("../items_archive.feature", "A non-member cannot archive the item")
def test_archive_non_member():
    pass


@scenario("../items_archive.feature", "Unauthenticated archive attempt is rejected")
def test_archive_unauth():
    pass


@scenario("../items_archive.feature", "Toggling archive updates the row without a page reload")
def test_archive_ui():
    pass


@scenario("../items_archive.feature", "Archived state survives a refresh")
def test_archive_persists():
    pass


# -- Shared state ---

_ctx = {}


@given(parsers.parse('I am signed in as "{email}"'))
def signed_in(email, signed_cookie):
    _ctx["email"] = email
    _ctx["cookie"] = signed_cookie(email)


@given("I have no session")
def no_session():
    _ctx["email"] = None
    _ctx["cookie"] = None


@given(parsers.parse('an item "{title}" exists'))
def create_item(title):
    if not _ctx.get("cookie"):
        pytest.fail("no session cookie available")
    resp = httpx.post(
        f"{BASE_URL}/items",
        json={"title": title},
        headers={
            "Cookie": f"session={_ctx['cookie']}",
            "Origin": BASE_URL,
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 201, f"create item failed: {resp.status_code} {resp.text}"
    import re
    match = re.search(r'id="item-(\d+)"', resp.text)
    if match:
        _ctx["item_ids"] = _ctx.get("item_ids", {})
        _ctx["item_ids"][title] = int(match.group(1))
```

... (further steps follow same pattern as original TS steps)

**Full step definitions must reimplement all existing steps from api.steps.ts and ui.steps.ts, 1:1.**

### 1.14 no-mistakes skill: `.opencode/skills/no-mistakes.md`

```markdown
---
name: no-mistakes
description: Gate committed changes through the no-mistakes pipeline (review, test, lint, docs, PR, CI).
user-invocable: true
---

# Skill: no-mistakes

## Context
Use when the user asks to validate, gate, ship, or runs `/no-mistakes`.
Do not run by default — high token consumption.

## Usage
1. Ensure work is committed on a feature branch (not main).
2. Run `no-mistakes axi run --intent "<task objective>"`.
3. Follow prompts: `respond --action approve|fix|skip`.
4. On `checks-passed`, summarize outcome and ask user to review/merge.
```

### 1.15 Update `.opencode/skills/index.json`

Add entry:
```json
"no-mistakes": {
  "triggers": ["validate", "gate", "ship", "no-mistakes", "pipeline"],
  "file": ".opencode/skills/no-mistakes.md",
  "status": "seed"
}
```

---

## 2. Implementation order

| Phase | Step | What to do |
|---|---|---|
| BLUEPRINT | 1 | Read this plan, update `.feature` files if needed, update PRD endpoint matrix. |
| RED | 2 | Write `features/steps/test_items_archive.py` and `features/conftest.py`. Run `uv run pytest` — confirm all scenarios FAIL with expected errors (route missing, etc.). |
| GREEN | 3 | Create `pyproject.toml`, `wrangler.toml` updates. |
| GREEN | 4 | Implement `src/lib/session.py`, `src/lib/csrf.py`. |
| GREEN | 5 | Implement `src/db/items.py`, `src/schemas/items.py`. |
| GREEN | 6 | Create `src/templates/` (layout, item_list, item_row) and `src/templates.py`. |
| GREEN | 7 | Implement `src/routes/items.py`. |
| GREEN | 8 | Implement `src/app.py`. |
| GREEN | 9 | Implement `src/entry.py`. |
| GREEN | 10 | Run scenario 1 (`@api` archive endpoint) — get it green. |
| GREEN | 11 | Run remaining scenarios one by one. |
| VERIFY | 12 | Run full gate: `ruff`, `pyright`, `pytest`. |
| VERIFY | 13 | Update docs: CODEMAP.md, ARCHITECTURE_DEEP_DIVE.md, TESTING_AND_QUALITY_SPEC.md, SECURITY_AND_AUTH_RUNBOOK.md, AGENTS.md, README.md. |
| VERIFY | 14 | Add no-mistakes skill file + index entry. |
| VERIFY | 15 | Remove old TS files (src/index.tsx, src/routes/*, features/support/*.ts, features/steps/*.ts, package.json, etc.) |
| VERIFY | 16 | Create PR per `.opencode/skills/pr-creation.md`. |

---

## 3. Commands reference

After setting up the workspace venv:

```bash
# Setup
uv sync                               # install deps from pyproject.toml

# Dev
uv run pywrangler dev --port 8787     # local server

# DB migrations
uv run pywrangler d1 migrations apply DB --local   # apply to local D1

# Quality
uv run ruff check src/ features/      # lint
uv run ruff format --check src/ features/  # format check
uv run pyright                         # type checker

# Tests
uv run pytest                          # BDD suite (starts pywrangler dev automatically)

# Deploy
uv run pywrangler deploy               # to Cloudflare
```

---

## 4. Docs changes required

| File | Key change |
|---|---|
| `CODEMAP.md` | Replace TS file entries with Python files; update descriptions. |
| `docs/ARCHITECTURE_DEEP_DIVE.md` | Stack blueprint: Hono → FastAPI/Python; JSX → Jinja2; remove Python Workers rationale section. |
| `docs/TESTING_AND_QUALITY_SPEC.md` | Toolchain: cucumber-js → pytest-bdd, `pnpm test` → `uv run pytest`, Biome → ruff, tsc → pyright. |
| `docs/SECURITY_AND_AUTH_RUNBOOK.md` | Session middleware now in Python stdlib; code examples updated. |
| `AGENTS.md` | Update commands table: `pnpm` → `uv` scripts. Add Python lint/typecheck commands. |
| `README.md` | Update quick-start and deploy commands. |

---

## 5. Human check-in gates

Before proceeding, the implementing session **must** ask the human:
- [ ] Before removing existing TS source and Node config (destructive).
- [ ] Before installing uv and workers-py (new local toolchain).

---

## 6. Key decisions made

| Decision | Choice | Rationale |
|---|---|---|
| Better Auth | Dropped | TypeScript-only, incompatible with Python Workers |
| Hyperdrive | Dropped | Would require Postgres; not needed |
| Python framework | FastAPI + ASGI | Familiar, Pydantic validation, works with workers ASGI adapter |
| Templating | Jinja2 via FastAPI Jinja2Templates | Standard, auto-escaping, request context support |
| Auth | Signed-cookie sessions ported to Python stdlib | Same HMAC-SHA256 scheme, same tests, no new deps |
| Test harness | pytest-bdd + Playwright (Python) | Replaces cucumber-js; all Gherkin scenarios preserved |
| Testing browser | Playwright Python async API | Same browser, same headless Chromium |
| Lint/format | Ruff | Modern Python linter/formatter |
| Type checking | Pyright | Best Workers runtime type support |
| Package manager | uv + pyproject.toml | Official tool for Python Workers |
| no-mistakes skill | Added as optional skill | High token consumption; skill file + index entry only |
| Database | D1 (unchanged) | No schema changes needed |
| Static assets | Public/ (unchanged) | Works with Workers Assets binding |

---

## 7. Potential pitfalls

- **Env access in ASGI:** The `env` object must be available in `request.scope["env"]`. The workers ASGI adapter in `asgi.fetch` passes it. Verify with a test: `request.scope["env"].DB` should work.
- **Jinja2 FileSystemLoader path:** In the Workers runtime, `__file__` resolves correctly. If not, fallback to `PackageLoader` or embed templates as strings using `DictLoader`.
- **pywrangler and D1 commands:** `pywrangler d1 migrations apply` and `pywrangler d1 execute` may or may not work. If they fail, fall back to `wrangler d1 ...` via npm (install wrangler globally or in a temporary Node setup). Or use `uv run pywrangler -- d1 ...` — test early.
- **Playwright install:** The implementing session must run `playwright install chromium` (in Python context: `uv run playwright install chromium`) before the first test run.
- **Cookie signing format match:** The Python `sign_token` function must produce exactly the same token format as the original TS implementation, or the BDD harness's `signed_cookie` fixture (which generates tokens independently) will produce tokens the server rejects. Both use the same secret — verify with a unit test in the first GREEN step.
