# Skill: kv-fragment-cache            (seed · from docs/ARCHITECTURE_DEEP_DIVE.md §5)

## Context
Expensive fragment identical for many users (stats, public lists). NOT for personalized
fragments, sessions, or anything needing read-after-write. Free tier: 1k KV writes/day.

## Pattern
```ts
// lib/cache.ts
export async function cachedFragment(
  kv: KVNamespace, key: string, ttl: number, render: () => Promise<string>,
): Promise<string> {
  const hit = await kv.get(key);
  if (hit !== null) return hit;
  const html = await render();
  await kv.put(key, html, { expirationTtl: ttl });
  return html;
}
// usage: c.html(await cachedFragment(c.env.CACHE, `frag:stats:global`, 300, renderStats))
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
