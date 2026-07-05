# Skill Template Blueprint

> Every extracted skill MUST use this exact structure. Hard cap: ~900 tokens/skill.
> A skill is a PROVEN pattern: it shipped, its BDD scenarios passed. No speculation.

---

# Skill: <archetype-name>            (proven: <date> · app: <repo> · feature: <slug>)

## Context (≤3 lines)
When to use. When NOT to use. Boundary-matrix side (htmx/Alpine/server-only).

## Contract (Pydantic)
```python
# exact input schema, module-scope
class Params(BaseModel):
    item_id: int
```

## Pattern (minimum viable slice: db → template → route)
```python
# db/: RETURNING-style single statement, owner-filtered via session.sub
# templates/: Jinja2 fragment w/ stable DOM id for hx-target
# routes/: Depends(validate) → db fn → TemplateResponse(fragment); HTTPException on null
```
(Compress: include ONLY the lines that carry the pattern; elide boilerplate with `…`.)

## Proof (Playwright/Gherkin that verified it)
```gherkin
Scenario: <observable outcome>          # tag @api or @ui
  When <trigger> Then <assertion that survives refresh>
```

## Gotchas (bullet list, hard-won only)
- e.g. htmx POST needs `origin` header in api-steps or csrf() rejects it.

---

Formatting rules: no prose paragraphs; code > words; every gotcha must have cost a
self-repair loop to earn its place. If a skill exceeds the cap → split or compress.
