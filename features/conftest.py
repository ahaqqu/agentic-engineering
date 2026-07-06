import os
import re
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from playwright.async_api import async_playwright

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from lib.session import sign_token, make_payload  # noqa: E402
from pytest_bdd import given, when, then, parsers  # noqa: E402

BASE_PORT = 8787
BASE_URL = f"http://localhost:{BASE_PORT}"
SESSION_SECRET = os.environ.get("SESSION_SECRET", "test-secret-do-not-use-in-prod")


def signed_cookie(email: str) -> str:
    payload = make_payload(f"test-{email}", email, "Test User")
    return sign_token(payload, SESSION_SECRET)


def wait_for_health(url: str, timeout: int = 90):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = httpx.get(url, timeout=5)
            if resp.is_success:
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise TimeoutError(f"Health check timed out after {timeout}s")


@pytest.fixture(scope="session")
def event_loop():
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def server():
    subprocess.run(
        ["uv", "run", "pywrangler", "d1", "migrations", "apply", "DB", "--local"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )
    proc = subprocess.Popen(
        ["uv", "run", "pywrangler", "dev", "--port", str(BASE_PORT)],
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    wait_for_health(f"{BASE_URL}/health")
    yield
    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture(autouse=True)
def reset_db():
    subprocess.run(
        [
            "uv",
            "run",
            "pywrangler",
            "d1",
            "execute",
            "DB",
            "--local",
            "--command",
            "DELETE FROM items;",
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )


@pytest.fixture
def ctx():
    return {}


@pytest_asyncio.fixture
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        yield browser
        await browser.close()


@pytest_asyncio.fixture
async def page(browser):
    context = await browser.new_context(ignore_https_errors=True)
    page = await context.new_page()
    yield page
    await context.close()


# --- Step definitions ---


@given(parsers.parse('I am signed in as "{email}"'))
def signed_in(email, ctx):
    ctx["email"] = email
    ctx["cookie"] = signed_cookie(email)


@given("I have no session")
def no_session(ctx):
    ctx["email"] = None
    ctx["cookie"] = None


@given(parsers.parse('an item "{title}" exists'))
def create_item(title, ctx):
    if not ctx.get("cookie"):
        pytest.fail("no session cookie available")
    resp = httpx.post(
        f"{BASE_URL}/items",
        json={"title": title},
        headers={
            "Cookie": f"session={ctx['cookie']}",
            "Origin": BASE_URL,
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 201, f"create item failed: {resp.status_code} {resp.text}"
    match = re.search(r'id="item-(\d+)"', resp.text)
    if match:
        ctx.setdefault("item_ids", {})
        ctx["item_ids"][title] = int(match.group(1))


@when(parsers.parse('I POST to the archive endpoint for "{title}"'))
def post_archive(title, ctx):
    item_id = ctx.get("item_ids", {}).get(title)
    if not item_id:
        pytest.fail(f"no item id found for {title!r}")
    cookie = ctx.get("cookie", "") or ""
    headers = {"Origin": BASE_URL}
    if cookie:
        headers["Cookie"] = f"session={cookie}"
    else:
        headers["HX-Request"] = "true"
    resp = httpx.post(f"{BASE_URL}/items/{item_id}/archive", headers=headers)
    ctx["last_response"] = resp


@then(parsers.parse("the response status is {status:d}"))
def check_status(status, ctx):
    resp = ctx.get("last_response")
    if not resp:
        pytest.fail("no response to check")
    assert resp.status_code == status, (
        f"expected status {status}, got {resp.status_code}: {resp.text}"
    )


@then(parsers.parse('the response HTML contains an element "{selector}"'))
def check_element(selector, ctx):
    resp = ctx.get("last_response")
    if not resp:
        pytest.fail("no response to check")
    html = resp.text
    if selector.startswith("[") and "'" in selector:
        attr = selector[1:-2]
        name, _, raw_val = attr.partition("=")
        val = raw_val.strip("'\"")
        assert f'{name}="{val}"' in html or f"{name}='{val}'" in html
    else:
        assert selector in html, f"expected {selector} not found in:\n{html}"


@when("I open the items page")
async def open_items_page(ctx, browser, page):
    _ = browser
    cookie_val = ctx.get("cookie")
    if cookie_val:
        await page.context.add_cookies(
            [
                {
                    "name": "session",
                    "value": cookie_val,
                    "domain": "localhost",
                    "path": "/",
                }
            ]
        )
    await page.goto(BASE_URL)


@when(parsers.parse('I click the archive button on "{title}"'))
async def click_archive(title, page):
    btn = page.locator("li").filter(has_text=title).locator("button")
    await btn.click()


@then(parsers.parse('the row for "{title}" shows the archived badge'))
async def check_badge(title, page):
    row = page.locator("li").filter(has_text=title)
    await row.wait_for(state="visible", timeout=10_000)
    badge = row.locator("span.badge")
    await badge.wait_for(state="visible", timeout=10_000)
    text = await badge.text_content()
    assert text and "archived" in text, f'expected archived badge for "{title}", got "{text}"'


@then("the page did not perform a full navigation")
async def check_no_nav(page):
    url = page.url
    assert BASE_URL in url, f"unexpected navigation to {url}"


@when("I reload the page")
async def reload_page(page):
    await page.reload()
