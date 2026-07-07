import httpx
import pytest
from pytest_bdd import scenario, then, when, parsers

BASE_PORT = 8787
BASE_URL = f"http://localhost:{BASE_PORT}"


@scenario("../template_defects.feature", "Create item with valid title returns the row fragment")
def test_create_item_valid():
    pass


@scenario("../template_defects.feature", "Create item with empty title returns 422")
def test_create_item_empty():
    pass


@scenario("../template_defects.feature", "Create item with too-long title returns 422")
def test_create_item_too_long():
    pass


@scenario(
    "../template_defects.feature", "New items have archived default false after additive migration"
)
def test_migration_additive():
    pass


@when(parsers.re(r'I POST to create item with title "(?P<title>.*)"'))
def post_create_item(title, ctx):
    cookie = ctx.get("cookie", "") or ""
    headers = {
        "Origin": BASE_URL,
        "Content-Type": "application/json",
    }
    if cookie:
        headers["Cookie"] = f"session={cookie}"
    resp = httpx.post(
        f"{BASE_URL}/items",
        json={"title": title},
        headers=headers,
    )
    ctx["last_response"] = resp


@then(parsers.parse('the response HTML contains an element "{selector}"'))
def check_element_selector(selector, ctx):
    resp = ctx.get("last_response")
    if not resp:
        pytest.fail("no response to check")
    html = resp.text
    if selector.startswith("[") and selector.endswith("]") and "=" in selector:
        attr = selector[1:-1]
        name, _, raw_val = attr.partition("=")
        val = raw_val.strip("'\"")
        assert f'{name}="{val}"' in html or f"{name}='{val}'" in html, (
            f"expected attribute {name}={val!r} not found in response HTML"
        )
    else:
        assert selector in html, f"expected {selector!r} not found in response HTML"
