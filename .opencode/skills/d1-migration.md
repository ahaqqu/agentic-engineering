# Skill: d1-migration            (seed · from docs/ARCHITECTURE_DEEP_DIVE.md, PRODUCT_PLAYBOOK.md)

## Context
Any schema change. Additive = autonomous. ALTER/DROP of existing data = STOP, human gate.

## Pattern
```bash
# next number, descriptive slug
migrations/000X_<slug>.sql
uv run pywrangler d1 migrations apply DB --local  # apply before Phase 2 test run
# prod applied by CI: uv run pywrangler d1 migrations apply DB --remote
```
```sql
-- additive-safe shapes (no human gate needed):
ALTER TABLE items ADD COLUMN archived INTEGER NOT NULL DEFAULT 0;
CREATE TABLE IF NOT EXISTS … ;
CREATE INDEX IF NOT EXISTS idx_items_list ON items(list_id);
```

## Proof
```gherkin
@api Scenario: new column round-trips through endpoint + fragment
```

## Gotchas
- SQLite ALTER is limited (no DROP COLUMN pre-3.35 semantics; no ALTER of constraints)
  → column rebuilds require new-table-copy-rename = destructive = human gate.
- Every new user-data table needs owner/membership column + index in the SAME migration.
- Booleans are INTEGER 0/1; timestamps are INTEGER unixepoch or TEXT ISO — pick per PRD.
- Update PRD §2 Schema Map + CODEMAP.md in the same task.
