# PRODUCT_PLAYBOOK.md

> How a raw idea becomes a deterministic, AI-executable spec. Repeatable across every
> app in the suite. Output of this playbook = one Agentic PRD + one or more `.feature`
> files. Agents may not write code without both.

## 1. The "Vibe-to-Spec" Brainstorming Protocol

Run these five passes, in order, with the human. Each pass produces one PRD section.

**Pass 1 — The One-Loop Pitch.** "Who does what, and what changes in D1 when they do?"
If the core loop can't be stated as `actor → action → row mutation → visible fragment`,
the idea isn't ready.

**Pass 2 — Data Gravity (D1 schema implications).** Strategic questions:
- What are the nouns? (→ tables) What uniquely identifies each? (→ keys)
- What is owned by a user vs shared? (→ `user_id` columns, IDOR filters)
- What is derived/countable? (→ compute in SQL, never in JS loops)
- What is ephemeral? (→ KV cache candidate, TTL?) What is never stored? (say so)

**Pass 3 — Interaction Physics (htmx vs Alpine boundary).** For every interaction ask:
"If the user refreshes right now, must the result still be there?"
Yes → htmx endpoint. No → Alpine local state. Record every answer in the Boundary table.

**Pass 4 — Mobile Reality (Capacitor/PWA).** Which views need thumb-reach layout
(daisyUI `btm-nav`, drawer)? What happens offline (bundled fallback)? Any deep links?

**Pass 5 — The 10ms & Free-Tier Guardrail.** Run the checklist in §4 for every feature.
A feature that fails the checklist gets redesigned before it enters the PRD.

## 2. The Agentic PRD Template

Copy verbatim into `docs/prd/<feature-or-app>.md`. Every section is mandatory;
write `NONE` explicitly rather than omitting.

```markdown
# PRD: <name>            (status: draft | approved | shipped)

## 1. System Overview
One paragraph. Actor(s), core loop, success signal. Stack is fixed by
ARCHITECTURE_DEEP_DIVE.md — do not restate it; note deviations only (usually NONE).

## 2. D1 Schema Map
| Table | Column | Type | Constraints | Notes |
|---|---|---|---|---|
| items | id | INTEGER | PK AUTOINCREMENT | |
| items | user_id | TEXT | NOT NULL, IDX | session.sub owner filter |
Migration file: migrations/000X_<name>.sql   (breaking change? → human review gate)

## 3. KV Cache Map
| Key pattern | Value | TTL | Invalidation |
|---|---|---|---|
| frag:stats:global | rendered HTML | 300s | TTL only |
(NONE is a valid and common answer — KV writes are scarce on free tier.)

## 4. Endpoint Specification Matrix
| Route | Method | Triggering htmx attr | Input (Zod) | Output fragment | Auth |
|---|---|---|---|---|---|
| /items | GET | hx-get (load, pagination) | ListQuery{page} | fragments/itemList | session |
| /items/:id/archive | POST | hx-post on toggle btn | Param{id} | fragments/itemRow | session+owner |

## 5. Component Interactivity Boundaries
| Interaction | Owner | Mechanism |
|---|---|---|
| Archive toggle | htmx | hx-post, swap outerHTML of row |
| "New item" modal open/close | Alpine | x-data="{open:false}" |

## 6. Non-Goals
Explicit list of what NOT to build. Prevents agent scope drift.

## 7. Acceptance
Feature files: features/<name>.feature (the executable contract — see §3)
```

## 3. BDD-First Requirement Blueprinting

The `.feature` file is part of the requirement, not an artifact of development.
Rules for writing PRD-grade Gherkin:

1. One `Feature` per PRD §4 route group; scenarios map 1:1 to endpoint matrix rows.
2. Scenario titles state the observable outcome, not the mechanism
   ("row shows archived badge", not "endpoint returns 200").
3. Always include: the happy path, one authorization failure (other user's data),
   and one validation failure per input schema.
4. Tag `@api` (fragment contract) and `@ui` (browser truth) as in TESTING_AND_QUALITY_SPEC.
5. The agent's definition of "correct code" = these scenarios pass. Nothing else counts.

## 4. The 10ms Guardrail Checklist (run per feature, before codegen)

- [ ] Does any fragment load an unbounded dataset? → add pagination (`LIMIT 50`) to the PRD.
- [ ] Is any layout element identical for all users? → KV fragment cache candidate (mind 1k writes/day).
- [ ] Multi-statement write? → specify `db.batch()` in the endpoint matrix notes.
- [ ] Any per-request construction of schemas/regex/constants? → forbid; module scope.
- [ ] Any CPU-heavy transform (markdown, image, big JSON)? → redesign or defer to paid Queues.
- [ ] Request count math: does the feature's chattiest screen stay well under 100k req/day at target usage?
- [ ] KV write frequency ≤ 1k/day? D1 writes ≤ 100k rows/day?
- [ ] Every user-data query filters by `session.sub`?

## 5. Worked Example — "Collaborative, Mobile-First ToDo with Google SSO"

### PRD: todo-core (approved)

**1. System Overview.** Signed-in users manage shared todo lists. Core loop: member adds/
completes/archives items; all members see changes on next interaction (no realtime —
Non-Goal). Success: a two-person household runs groceries on it for a week.

**2. D1 Schema Map**

| Table | Column | Type | Constraints |
|---|---|---|---|
| users | sub | TEXT | PK (Google sub) |
| users | email, name | TEXT | NOT NULL |
| lists | id | INTEGER | PK AUTOINCREMENT |
| lists | title | TEXT | NOT NULL |
| lists | owner_sub | TEXT | NOT NULL REFERENCES users |
| list_members | list_id, member_sub | — | composite PK; IDX(member_sub) |
| items | id | INTEGER | PK AUTOINCREMENT |
| items | list_id | INTEGER | NOT NULL, IDX |
| items | title | TEXT | NOT NULL, len ≤ 200 (Zod) |
| items | done | INTEGER | NOT NULL DEFAULT 0 |
| items | archived | INTEGER | NOT NULL DEFAULT 0 |
| items | created_by | TEXT | NOT NULL |

Migration: `migrations/0001_init.sql`

**3. KV Cache Map:** NONE (all views personalized; KV write quota reserved).

**4. Endpoint Specification Matrix**

| Route | Method | htmx trigger | Input (Zod) | Output | Auth |
|---|---|---|---|---|---|
| / | GET | — (full page) | — | pages/lists | session |
| /lists | POST | hx-post form | `{title: string.min(1).max(80)}` | fragments/listCard | session |
| /lists/:id | GET | hx-get nav | `{id: coerce.number}` | fragments/itemList (page ≤50) | member |
| /lists/:id/items | POST | hx-post form | `{title: string.min(1).max(200)}` | fragments/itemRow (prepend) | member |
| /items/:id/toggle | POST | hx-post checkbox | `{id}` | fragments/itemRow (outerHTML) | member |
| /items/:id/archive | POST | hx-post button | `{id}` | fragments/itemRow (outerHTML) | member |
| /lists/:id/members | POST | hx-post email form | `{email: email()}` | fragments/memberList | owner |

**5. Boundaries:** add-item input focus/clear = Alpine; "add member" modal = Alpine;
everything touching rows = htmx. Mobile: daisyUI `btm-nav` (Lists / Active / Archived),
44px touch targets, `navbar` collapses to drawer.

**6. Non-Goals:** realtime sync, offline mutation queue, item reordering, push notifications.

**7. Acceptance** — `features/todo_items.feature` (excerpt):

```gherkin
Feature: Shared todo items
  Background:
    Given I am signed in as "ada@example.com"
    And a list "Groceries" shared with "grace@example.com" exists

  @ui
  Scenario: Completing an item survives refresh
    When I open the list "Groceries" and add item "Milk"
    And I toggle the checkbox on "Milk"
    And I reload the page
    Then the item "Milk" is shown as done

  @api
  Scenario: A non-member cannot toggle items
    Given I am signed in as "mallory@example.com"
    When I POST to the toggle endpoint for "Milk"
    Then the response status is 404
```

**Guardrail run:** item lists paginated at 50 ✓ · no KV ✓ · toggle = single UPDATE +
single-row render, ≈1ms CPU ✓ · all queries membership-filtered ✓ → approved.
