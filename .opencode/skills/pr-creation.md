# Skill: pr-creation            (proven: 2026-07-05 · template validation)

## Context
After Phase 4 gate passes green. Creates a standardized, reviewable PR from the
treehouse worktree branch to main. The PR must be self-contained enough that a human
can review it in <5 minutes — all context (BDD proof, schema changes, skill extraction)
must be in the PR body, not scattered across commits.

## PR Title format
```
<type>(<scope>): <short summary>     # max 72 chars
```
Types: `feat` · `fix` · `refactor` · `docs` · `chore`
Scope: the resource/route touched (e.g. `items`, `auth`, `d1`, `ci`)
Examples:
- `feat(items): add archive toggle with htmx fragment swap`
- `fix(auth): HMAC base64url portability between Worker and Node`
- `chore(d1): remove FK constraint from items table`

## PR Body template
```markdown
## Summary
<!-- one sentence: what changed and why -->

## BDD proof
- `pnpm run check`  ✓
- `pnpm run typecheck`  ✓
- `pnpm test` — `{N}/{N}` scenarios passed, `{M}/{M}` steps passed

## Files changed
<!-- key files only, 1 line each with purpose -->
- `{file path}` — {brief reason for change}

## Check-in notes
<!-- mandatory: list any human-review gates triggered, or "None triggered" -->

## Self-correction ledger
<!-- any bugs found and fixed during self-repair loops (from lessons.md) -->
- {symptom} → {root cause & fix}

## Skill extraction
- New skill: `{archetype}` (or "None")

## Breaking changes?
<!-- yes/no — if yes, detail migration steps needed -->
```

## PR body generation (agent sequence)
1. Re-read the task description from Phase 1.
2. Run `git log --oneline {base_branch}..HEAD` to list all commits in the worktree.
3. Run `git diff {base_branch}..HEAD --stat` for file-change summary.
4. Read the latest CODEMAP.md additions for the changed files.
5. Read `lessons.md` for any new entries from this task.
6. Assemble the PR body from the template above.
7. Create PR with `gh-axi pr create` (or `gh pr create` fallback).

## PR rules (non-negotiable)
- ❌ Never create a PR while the full gate is red.
- ❌ Never merge your own PR — submit for human review only.
- ❌ Never create a PR with a dirty working tree (must be committed).
- ✅ If the worktree has 0 commits (trivial config-only change), still create
  a PR — every change needs a review trail.
- ✅ If a human-review gate was triggered (schema-breaking migration, new
  dependency), state it prominently in the Check-in notes section.
