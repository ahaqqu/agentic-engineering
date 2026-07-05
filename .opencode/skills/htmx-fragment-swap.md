# Skill: htmx-fragment-swap            (seed · from docs/ENGINEERING_FLOW.md §4)

## Context
Any state change that must survive refresh: toggle/edit/delete on a row or card.
NOT for ephemeral UI (modals, tabs → Alpine).

## Contract (Pydantic)
```python
# module scope
class ArchiveParams(BaseModel):
    item_id: int
```

## Pattern
```html
{# templates/item_row.html — stable DOM id = swap anchor #}
<li id="item-{{ item.id }}" data-archived="{{ 'true' if item.archived else 'false' }}">
  …
  <button class="btn btn-sm" hx-post="/items/{{ item.id }}/archive"
          hx-target="#item-{{ item.id }}" hx-swap="outerHTML">…</button>
</li>
```

```python
# db/items.py — single UPDATE, owner-filtered, RETURNING *
UPDATE items SET archived = 1 - archived
 WHERE id = ? AND sub = ?
 RETURNING *

# routes/items.py
@router.post("/items/{item_id:int}/archive")
async def archive_item(
    item_id: int,
    session: Session = Depends(require_session),
    db: D1Database = Depends(get_db),
):
    item = await toggle_archive(db, item_id, session.sub)
    if not item:
        raise HTTPException(status_code=404)  # covers foreign-owner IDOR too
    return templates.TemplateResponse("item_row.html", {"item": item})  # fragment, never JSON
```

## Proof
```gherkin
@ui Scenario: toggle updates row without navigation; state survives reload
```

## Gotchas
- `1 - archived` UPDATE is idempotent-per-state → double-click race is safe.
- Owner filter inside the UPDATE (not a prior SELECT) = 1 statement, IDOR-safe.
- GET list endpoints must branch on `HX-Request` (fragment vs full layout) for deep links.
