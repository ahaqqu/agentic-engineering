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
     `pnpm run check` ✓ · `pnpm run typecheck` ✓
     `pnpm test` — {N}/{N} scenarios passed, {M}/{M} steps passed -->

## Security checklist
- [ ] Is every mutation route protected by session + owner filter?
- [ ] Are CSRF checks in place for POST routes?
- [ ] Are new secrets/cookies HttpOnly + Secure + SameSite?
- [ ] Are there any new environment variables that need wrangler secrets?
- [ ] Could this change introduce an IDOR? (every D1 query filters by session.sub?)

## Performance checklist
- [ ] Do any htmx fragments load unbounded datasets? (must paginate LIMIT 50)
- [ ] Is there any per-request construction of schemas/constants? (must be module scope)
- [ ] Any CPU-heavy transforms (markdown, image, big JSON)?
- [ ] Any KV writes added? (free tier: 1k/day)

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
5. Walk each checklist mentally (do not include unchecked items — only check what's verified).
6. Assemble the PR body from the template above.
7. Create PR: `gh-axi pr create` (or `gh pr create` fallback).

## PR rules (non-negotiable)
- ❌ Never create a PR while the full gate is red.
- ❌ Never merge your own PR — submit for human review only.
- ❌ Never create a PR with a dirty working tree (must be committed).
- ✅ Always create a PR even for trivial changes — every change needs a review trail.
- ✅ If a human-review gate was triggered (destructive migration, new dependency, auth
  change), state it prominently in Limitations & warnings.
