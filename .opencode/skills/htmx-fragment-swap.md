# Skill: htmx-fragment-swap            (seed · from docs/ENGINEERING_FLOW.md §4)

## Context
Any state change that must survive refresh: toggle/edit/delete on a row or card.
NOT for ephemeral UI (modals, tabs → Alpine).

## Contract (Zod)
```ts
const Params = z.object({ id: z.coerce.number() }); // module scope
```

## Pattern
```tsx
// views/fragments/itemRow.tsx — stable DOM id = swap anchor
<li id={`item-${item.id}`} data-archived={String(!!item.archived)}>
  …
  <button class="btn btn-ghost btn-xs" hx-post={`/items/${item.id}/archive`}
          hx-target={`#item-${item.id}`} hx-swap="outerHTML">…</button>
</li>

// db/items.ts — single UPDATE, owner-filtered, RETURNING *
UPDATE items SET archived = 1 - archived
 WHERE id = ?1 AND list_id IN (SELECT list_id FROM list_members WHERE member_sub = ?2)
 RETURNING *

// routes/items.ts
items.post("/:id/archive", zValidator("param", Params), async (c) => {
  const item = await toggleArchive(c.env.DB, c.req.valid("param").id, c.get("session").sub);
  if (!item) return c.notFound();          // covers foreign-owner IDOR too
  return c.html(<ItemRow item={item} />);  // fragment, never JSON
});
```

## Proof
```gherkin
@ui Scenario: toggle updates row without navigation; state survives reload
```

## Gotchas
- `1 - archived` UPDATE is idempotent-per-state → double-click race is safe.
- Owner filter inside the UPDATE (not a prior SELECT) = 1 statement, IDOR-safe.
- GET list endpoints must branch on `HX-Request` (fragment vs full layout) for deep links.
