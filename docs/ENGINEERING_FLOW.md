# ENGINEERING_FLOW.md

> The agent's operating system. Every task — no exceptions — runs this deterministic
> loop. The human designs and reviews; the agent plans, implements, and verifies itself.

## 0. Task Entry Conditions

Before Phase 1 the agent must:
1. **Adopt the persona** for the task (e.g., "Hypermedia backend engineer", "BDD test
   engineer") and state it in one line.
2. **Create an isolated worktree** via treehouse (`kunchenguid/treehouse`) — one task,
   one worktree, one branch: `tree <task-slug>` (or documented fallback
   `git worktree add ../<repo>-<task-slug> -b <task-slug>` if treehouse is unavailable).
3. **Load context lazily**: read `CODEMAP.md` (never crawl the codebase) and consult
   `.opencode/skills/index.json` for a matching skill. Guessing historical patterns is
   forbidden.

## 1. The 4-Phase Chronological Loop

```
Phase 1: BLUEPRINT  → plan printed, PRD mapped, no files touched
Phase 2: RED        → .feature + failing steps, watch them fail
Phase 3: GREEN      → minimum code to pass, one scenario at a time
Phase 4: VERIFY     → full gate, self-repair ≤3, refactor, docs, skill extraction
```

### Phase 1 — Blueprint Ingestion & Gherkin Writing
**System instruction (paste into agent rules):**
> Before editing ANY file: print a technical implementation plan containing
> (a) affected D1 tables + exact migration SQL if any, (b) each new/changed route as a
> PRD §4 endpoint-matrix row, (c) fragment names and their hx-target/hx-swap strategy,
> (d) the htmx-vs-Alpine ownership for each interaction, (e) points of failure and their
> error handling. Then write or update the `.feature` file. You may not
> create or modify any `.py`/`.sql` file in this phase.

**Gate:** plan printed + `.feature` committed. Schema-breaking change detected here →
human check-in (see §3) before proceeding.

### Phase 2 — Stub & Fail Step Generation
**System instruction:**
> Write the step definitions for every new scenario (`features/steps/*.py`).
> Implement steps fully; leave application code untouched. Run `uv run pytest` and confirm
> the new scenarios FAIL for the expected reason (missing route/fragment — assert the
> failure message matches your plan). A scenario failing for an unexpected reason means
> your plan is wrong: revise the plan, not the assertion.

**Gate:** new scenarios red with expected diagnostics; pre-existing scenarios still green.

### Phase 3 — Incremental Implementation
**System instruction:**
> Implement the MINIMUM code to turn one scenario green at a time, in this order:
> migration → `src/schemas/` (Pydantic) → `src/db/` (query fn) → `src/templates/` →
> `src/routes/`. Re-run `uv run pytest` after each scenario turns green. Prefer vetted
> existing libraries over hand-rolled code, but adding ANY new dependency requires
> human approval first. Never edit test assertions to make them pass.

**Gate:** all scenarios green locally against `pywrangler dev`.

### Phase 4 — Verification & Autonomous Refactoring
**System instruction:**
> Run the full gate: `uv run ruff check src/ features/` && `uv run ruff format --check src/ features/` && `uv run pyright` && `uv run pytest`.
> On ANY failure run the Self-Correction Loop (§2). When green: refactor for pattern
> quality (no logic in routes, module-scope hoisting, boundary matrix respected) and
> re-run the gate. Then update `CODEMAP.md` and the PRD, and execute the skill-extraction
> trigger in `.opencode/skills/memory_manager.md`.
>
> **Final step: create a pull request.** Load the `pr-creation` skill
> (`.opencode/skills/pr-creation.md`) and follow its PR template exactly. The PR title
> must follow `type(scope): summary` (72 char max). The PR body must include BDD proof
> (scenario counts), check-in notes (any gates triggered), and self-correction entries.
> Use `gh-axi pr create` when available, or `gh pr create` as fallback.
>
> **Gate:** PR is created, full-gate evidence is in the PR body. Only then declare the
> task complete.

## 2. The Self-Correction Loop (max 3 attempts)

```
attempt = 0
while gate fails and attempt < 3:
    1. READ the full failure output (stack trace / diff / diagnostic). No skimming.
    2. HYPOTHESIZE one root cause; state it in one sentence.
    3. FIX locally — smallest change that addresses the root cause. Never delete or
       weaken a test. Never broaden types to `any`. Never suppress lints.
    4. RE-RUN the failing command only; if it passes, re-run the full gate.
    attempt += 1
if still failing:
    STOP. Report: what failed, the 3 hypotheses tried, current diff. Ask the human.
Also: append the failure→fix pair to .opencode/skills/lessons.md (Self-Correction Ledger).
```

## 3. Check-in Thresholds (when to interrupt the human)

**MUST ask before proceeding:**
- Migration that alters/drops existing tables or columns, or any data-loss risk.
- CPU-time errors (exceeded 10ms) or any Cloudflare limit breach.
- Adding a dependency, external service, or new binding (D1/KV/queue).
- Anything uncertain, seemingly wrong, or with a clearly better alternative.
- Auth/session/cookie semantics changes.

**MUST NOT ask (handle autonomously):**
- Syntax errors, missing imports, type errors, lint violations.
- CSS/daisyUI class fixes, fragment markup tweaks.
- Flaky-test retries and test-harness plumbing.
- Formatting — never hand-formatted at all; `ruff check --fix` owns it.

## 4. Complete Execution Example
### Task: "Add an archive toggle button to items using daisyUI buttons and an htmx POST"

**Phase 1 output (agent prints):**
> Persona: hypermedia backend engineer. Worktree: `tree item-archive-toggle`.
> Plan: (a) D1: `items` gains `archived INTEGER NOT NULL DEFAULT 0` — additive, no
> review gate → `migrations/0002_items_archived.sql`. (b) Route: `POST
> /items/{id}/archive` | hx-post | Pydantic `{id: int}` | returns
> `item_row.html` fragment | auth: session+owner. (c) Fragment: `item_row.html` swapped via
> `hx-swap="outerHTML"` targeting `#item-{id}`. (d) Boundary: toggle = htmx (survives
> refresh); no Alpine state. (e) Failure points: nonexistent/foreign id → 404;
> double-toggle race → last-write-wins UPDATE is idempotent per state; unauth → 401
> HX-Redirect.

**Phase 1 feature file** — `features/items_archive.feature`: (see
TESTING_AND_QUALITY_SPEC §3 — that boilerplate IS this feature).

**Phase 2 failing steps** — `features/steps/test_items_archive.py` (excerpt):

```python
@when(parsers.parse('I POST to the archive endpoint for "{title}"'))
async def post_archive(context, title: str):
    item_id = await context.item_id_by_title(title)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{context.base_url}/items/{item_id}/archive",
            cookies={"session": context.signed_cookie("ada@example.com")},
            headers={"Origin": context.base_url},
        )
        context.response = resp

@then(parsers.parse("the response HTML contains an element {selector}"))
async def assert_selector(context, selector: str):
    html = context.response.text
    page = await context.browser.new_page()
    await page.set_content(html)
    assert await page.query_selector(selector) is not None
    await page.close()
```

`uv run pytest` → `404 Not Found` on the two new scenarios (expected: route missing). Red ✓

**Phase 3 implementation:**

`migrations/0002_items_archived.sql`
```sql
ALTER TABLE items ADD COLUMN archived INTEGER NOT NULL DEFAULT 0;
```

`src/db/items.py` (addition)
```python
async def toggle_archive(db: D1Database, item_id: int, sub: str) -> dict | None:
    row = await db.execute(
        "UPDATE items SET archived = 1 - archived "
        "WHERE id = ? AND sub = ? "
        "RETURNING *",
        [item_id, sub],
    )
    return row.first()
```

`src/templates/item_row.html` (addition)
```html
<li id="item-{{ item.id }}" class="flex items-center gap-2 py-2"
    data-archived="{{ 'true' if item.archived else 'false' }}">
  <span class="flex-1 {{ 'line-through opacity-50' if item.archived else '' }}">
    {{ item.title }}
  </span>
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

`src/routes/items.py` (addition)
```python
@router.post("/items/{item_id:int}/archive")
async def archive_item(
    item_id: int,
    session: Session = Depends(require_session),
    db: D1Database = Depends(get_db),
):
    item = await toggle_archive(db, item_id, session.sub)
    if not item:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("item_row.html", {"item": item})
```

**Phase 4 terminal transcript (agent runs internally):**
```
$ uv run ruff check src/ features/   # ruff: clean
$ uv run ruff format --check src/ features/  # ruff: format clean
$ uv run pyright         # 0 errors
$ uv run pytest          # 6 scenarios (6 passed), 24 steps (24 passed)
$ # CODEMAP.md + PRD endpoint matrix updated; skill 'htmx-row-toggle' extracted
$ gh pr create --base main --head item-archive-toggle \
  --title 'feat(items): add archive toggle with htmx fragment swap' \
  --body '## Summary
Add archive/unarchive toggle on items so users can hide completed items without deleting them.

## Architecture changes
- `migrations/0002_items_archived.sql`: additive ALTER TABLE adding `archived INTEGER DEFAULT 0`
- `src/routes/items.py`: new POST route /items/{id}/archive
- `src/templates/item_row.html`: new htmx fragment for row swap

## Functionality & behavioural changes with BDD proof
Users see an Archive button on each item row. Clicking it toggles archived state
via htmx POST; the row swaps in place with no page reload. Archived items show
strikethrough text and a badge.
- `uv run ruff check src/ features/` ✓ · `uv run ruff format --check src/ features/` ✓ · `uv run pyright` ✓
- `uv run pytest` — 6/6 scenarios passed, 24/24 steps passed

## Security review
- POST /items/{id}/archive is gated by require_session + owner filter inside the
  UPDATE WHERE clause (WHERE id = ? AND sub = ?) — no IDOR possible
- CSRF covered by global csrf_check() middleware checking Origin header
- No new cookies, secrets, or env vars introduced

## Performance review
- Single-row UPDATE with RETURNING — always O(1), no unbounded datasets
- No per-request schema/constant construction (module-scoped Pydantic schemas)
- No CPU-heavy transforms (toggle is simple integer arithmetic)
- No KV writes added

## Docs review
- CODEMAP.md updated with new route and fragment entries
- PRD endpoint matrix updated
- Feature file written before implementation (BDD gate satisfied)

## Manual test needed
NONE — all paths covered by BDD @api + @ui scenarios (create, archive,
unauthenticated rejection, non-member rejection, refresh survival)

## Engineering flow changes
- **Skill extraction:** htmx-row-toggle
- **Self-correction ledger entries:** NONE

## Limitations & warnings
- NONE (additive schema, no new deps, no auth changes)
'
→ https://github.com/org/repo/pull/42
→ Task complete.
