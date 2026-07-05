# Skill: pr-creation            (proven: 2026-07-05 · template validation)

## Context
After Phase 4 gate passes green. Creates a standardized, reviewable PR from the
treehouse worktree branch to main. Every section is mandatory — write `NONE` explicitly
if not applicable. No "Files changed" section (redundant — reviewer sees the diff).

## PR Title format
```
<type>(<scope>): <short summary>     # max 72 chars
```
Types: `feat` · `fix` · `refactor` · `docs` · `chore`
Scope: the resource/route touched (e.g. `items`, `auth`, `d1`, `ci`)

## PR Body template
```markdown
## Summary
<!-- one sentence: what changed and why. not a list of files. -->

## Architecture changes
<!-- new tables, new routes, middleware changes, migration type (additive/destructive),
     new dependencies. if NONE, write NONE. -->

## Functionality & behavioural changes with BDD proof
<!-- what behavior changed from the user's perspective. then the proof:
     `uv run ruff check src/ features/` ✓ · `uv run ruff format --check src/ features/` ✓
     `uv run pyright` ✓
     `uv run pytest` — {N}/{N} scenarios passed, {M}/{M} steps passed -->

## Security review
<!-- Think about what this change means for security. Consider: session guards,
     CSRF, cookie properties, new env vars, IDOR potential, data exposure in
     fragments, auth bypass scenarios. Write relevant items — not a template. -->
- <!-- e.g. "POST /items/:id/archive is gated by requireSession + owner filter
        in the UPDATE WHERE clause → no IDOR" -->
- <!-- e.g. "No new cookies or secrets introduced" -->

## Performance review
<!-- Think about what this change means for performance. Consider: pagination,
     per-request allocation vs module scope, CPU-heavy transforms, KV cache
     opportunities, D1 query patterns, fragment size. Write relevant items. -->
- <!-- e.g. "Single-row UPDATE with RETURNING — no unbounded datasets" -->
- <!-- e.g. "No KV writes added (free tier: 1k/day)" -->

## Docs checklist
- [ ] CODEMAP.md updated?
- [ ] PRD endpoint matrix updated?
- [ ] Feature file written before implementation? (BDD gate)

## Manual test checklist
<!-- things that can't be verified by BDD alone, if any -->
- [ ] (e.g. real Google SSO flow on mobile, Capacitor deep link, production D1 migration)

## Engineering flow changes
- **Skill extraction:** {new skill name, or NONE}
- **Self-correction ledger entries:** {symptom} → {root cause & fix} (or NONE)

## Limitations & warnings
<!-- breaking changes, known edge cases, data migration steps, human gates triggered,
     anything the reviewer should watch for. if NONE, write NONE. -->
```

## PR body generation (agent sequence)
1. Re-read the task description from Phase 1.
2. Run `git log --oneline {base_branch}..HEAD` for commit context.
3. Run `git diff {base_branch}..HEAD --stat` for awareness (not included in PR body).
4. Read `lessons.md` for any new entries from this task.
5. Analyze security and performance implications of the actual changes — write
   specific items, not generic checklist boilerplate. Every item must be a
   statement about this specific change, not a question from a template.
6. Assemble the PR body from the template above.
7. Create PR: `gh-axi pr create` (or `gh pr create` fallback).

## PR rules (non-negotiable)
- ❌ Never create a PR while the full gate is red.
- ❌ Never merge your own PR — submit for human review only.
- ❌ Never create a PR with a dirty working tree (must be committed).
- ✅ Always create a PR even for trivial changes — every change needs a review trail.
- ✅ If a human-review gate was triggered (destructive migration, new dependency, auth
  change), state it prominently in Limitations & warnings.
