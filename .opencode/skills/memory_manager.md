# memory_manager.md — The Hermes Compression Loop

> Operational directive for workspace self-improvement. Runs at defined triggers, not
> continuously. Objective: get smarter every task while total memory stays cheap.

## Trigger 1 — BDD Skill Extraction (fires on every 100% green `npm test` in Phase 4)

1. Ask: does this feature embody a REUSABLE archetype (not app-specific business logic)?
   - No → stop. Do not hoard.
   - Yes → continue.
2. Check `index.json`. Existing skill covers it?
   - Fully → stop (optionally add one Gotcha line if a self-repair loop taught one).
   - Partially → UPDATE that skill in place. Never create near-duplicates.
   - No → create `.opencode/skills/<archetype>.md` from `template_blueprint.md`,
     add an `index.json` entry with ≤6 keyword triggers, `status: "proven"`.
3. Every skill must cite its proof (feature slug + date). Unproven content is forbidden.

## Trigger 2 — Compaction (fires when any memory file > ~900 tokens / 3600 chars,
## or index.json > 300 tokens, or >12 skills; check sizes whenever you touch a skill)

1. Merge: skills sharing >50% content → one skill with a variant note.
2. Compress: prose → bullets; code → pattern-carrying lines only (`…` elisions).
3. Prune: `status: seed` skills never opened after 5 tasks → delete. Superseded
   patterns (old library API, replaced approach) → delete, note 1 line in lessons.md.
4. Re-verify index: every file listed exists; every file on disk is indexed; triggers
   are disjoint enough that one task maps to ≤2 skills.
5. Report the compaction in the task summary (files touched, tokens saved).

## Trigger 3 — Self-Correction Ledger (fires on EVERY self-repair loop in Phase 4,
## pass or fail)

Append one row to `.opencode/skills/lessons.md`:

```
| date | app | symptom (error snippet) | root cause | rule to never repeat |
```

Rules of the ledger:
- The "rule" column must be actionable ("always send Origin header in api steps"),
  never descriptive ("test failed").
- On the 2nd occurrence of the same root cause across apps → PROMOTE the rule:
  move it into the matching skill's Gotchas (or AGENTS.md if global and tiny),
  then delete the ledger rows. The ledger is a staging area, not an archive.
- Ledger itself obeys the ~900-token cap via Trigger 2.

## Trigger 4 — CODEMAP maintenance (fires in Phase 4 of every task)

`CODEMAP.md` mirrors the source tree: one line per file — path, purpose, exported
symbols, routes served. It exists so future sessions NEVER crawl the codebase
(principle #3). Stale CODEMAP = defect, same severity as a failing test.

## Prime Directive
Memory exists to save tokens and prevent repeated mistakes. If a memory operation
would cost more tokens than it saves over ~3 future tasks, don't do it.
