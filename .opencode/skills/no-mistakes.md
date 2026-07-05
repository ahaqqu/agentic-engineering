# Skill: no-mistakes

## Context
Use only when the user explicitly invokes `/no-mistakes`. Do NOT run by
default — high token consumption. Validates committed changes on a feature
branch through a review/test/lint/docs/CI pipeline.

## Pattern
1. Ensure work is committed on a non-default branch.
2. Run `no-mistakes axi run --intent "<task objective>"`.
3. Follow gate prompts: `respond --action approve|fix|skip`.
4. On `checks-passed`, report outcome; ask user to review/merge.
5. Escalate `ask-user` findings to the human — never approve them unilaterally.

## Gotchas
- Never edit code yourself while a run is active — the pipeline owns fixes.
- `checks-passed` means the PR is ready but not yet merged. Do not poll for merge.
