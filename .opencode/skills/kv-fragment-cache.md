# Skill: kv-fragment-cache            (seed · from docs/ARCHITECTURE_DEEP_DIVE.md §5)

## Context
Expensive fragment identical for many users (stats, public lists). NOT for personalized
fragments, sessions, or anything needing read-after-write. Free tier: 1k KV writes/day.

## Pattern
```python
# src/lib/cache.py
async def cached_fragment(
    kv: KVNamespace, key: str, ttl: int, render: Callable[[], Awaitable[str]],
) -> str:
    hit = await kv.get(key)
    if hit is not None:
        return hit
    html = await render()
    await kv.put(key, html, expiration_ttl=ttl)
    return html

# usage: return HTMLResponse(await cached_fragment(c.env.CACHE, "frag:stats:global", 300, render_stats))
```

## Proof
```gherkin
@api Scenario: second request returns identical fragment without D1 query (timing/log assert)
```

## Gotchas
- Key MUST encode every variable that changes output (`frag:<name>:<paramhash>`)
  or you ship cache poisoning.
- Invalidate by TTL only; delete-fanout burns the 1k write quota.
- Never cache fragments containing user names/emails unless key includes sub.
