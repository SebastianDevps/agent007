---
name: prd-author
description: "Author a Product Requirements Document — stakeholder-facing, distinct from engineering spec. Drives the user through Problem / User / Value / Scope / Constraints / Non-goals / Hypothesis / Validation. Goes BEFORE /sdd-new, not instead of it. The PRD becomes the input that sdd-propose reads first."
allowed-tools: ["Read", "Write", "Bash"]
auto-activate: false
version: 1.0.0
when:
  - command: Skill('prd-author')
  - phase: pre-sdd-new
---

# prd-author — Product Requirements Document Author (v7.2 Ola 35)

**Purpose**: A PRD answers the "what and why for the user", an engineering spec answers the "how for the system". Mixing them produces vague requirements and over-scoped implementations. This skill produces the PRD so `sdd-propose` has a clean stakeholder anchor.

**Trigger keywords (manual)**: `prd`, `product requirements`, `product spec`, `feature brief`, `define feature`, `write prd`.
**Auto-trigger**: none. Always user-initiated, BEFORE `/sdd-new`.

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `idea` | string | yes | Feature idea or problem statement (1-2 sentences) |
| `slug` | string | no | Override auto-generated slug |

---

## Workflow

The skill drives a guided structured Q&A. Ask ONE section's questions at a time, wait for the user response, then proceed. Do NOT dump the template and ask the user to fill it.

### Phase 1 — Problem
Ask:
- Whose problem is this? (specific user / persona)
- What evidence do we have it's real? (data, complaints, interviews)
- Why now? What changes if we wait six months?

### Phase 2 — User
Ask:
- Primary user persona — name them. ("solo developer onboarding to project", "team lead approving PRs")
- Job-to-be-done — what are they trying to accomplish when this feature would be invoked?

### Phase 3 — Value
Ask:
- What does success look like? (state it as an outcome, not an output)
- How will we measure it? (one metric, even rough)

### Phase 4 — Scope
Ask:
- What's IN scope (3-5 bullets, concrete)
- What's explicitly OUT of scope (this is where most PRDs go wrong — push for ≥3 out-of-scope items)

### Phase 5 — Constraints
Ask:
- Technical constraints (stack, dependencies, existing systems we must respect)
- Business constraints (budget, time, team capacity)
- Ethical / compliance constraints (data, privacy, regulatory)

### Phase 6 — Non-goals
Ask:
- What anti-features must we NOT add? (the "we will not solve X" list)

This is distinct from out-of-scope: out-of-scope is "not now", non-goals are "not ever, by design".

### Phase 7 — Hypothesis
Ask:
- State it as "If we build X, then Y will happen, because Z."
- Probe for falsifiability — if the user can't describe what would prove the hypothesis wrong, push back: "How would we know this was the wrong bet?"

### Phase 8 — Validation plan
Ask:
- How will we know within N weeks of shipping whether the hypothesis held?
- What signal would tell us to roll back / pivot?

### Phase 9 — Write the PRD

Path: `.sdlc/prds/<YYYY-MM>-<slug>.md`

Template (fill from Q&A answers):
```markdown
# PRD — <title>

**Date:** YYYY-MM-DD
**Status:** draft
**Author:** <user>

## Problem
<answers from Phase 1>

## User
**Persona:** <name>
**Job-to-be-done:** <description>

## Value
**Success looks like:** <outcome>
**Metric:** <how measured>

## Scope
**In:**
- ...

**Out:**
- ...

## Constraints
**Technical:** ...
**Business:** ...
**Ethical:** ...

## Non-goals
- ...

## Hypothesis
If we build **<X>**, then **<Y>**, because **<Z>**.

## Validation plan
**Within N weeks of ship:**
- Signal of success: ...
- Signal to pivot/rollback: ...
```

### Phase 10 — Confirm file persisted

PRD is persisted to `.sdlc/prds/<YYYY-MM>-<slug>.md`. The markdown file is the source of truth — no external backend required. Tracked in git.

### Phase 11 — Emit envelope

Return `SubagentResponseV1`:
- `status`: `success`
- `executive_summary`: "PRD created: <title>. Path: <path>. Hypothesis: <one-line>."
- `artifacts`: `[{ path }]`
- `next_recommended`: "Run `/sdd-new <slug>` — `sdd-propose` will read this PRD as its primary input."
- `risks`: `[]`
- `skill_resolution`: `injected | fallback-*`

---

## Example invocations

```
Skill('prd-author')
  idea: "Allow users to recover deleted notes within 30 days"

Skill('prd-author')
  idea: "Single-sign-on for enterprise tier"
  slug: "enterprise-sso"
```

---

## Why a PRD is not a spec

| PRD | Engineering spec |
|---|---|
| For stakeholders / product / users | For engineers |
| "What and why" | "How" |
| Hypothesis-driven | Implementation-driven |
| Non-goals make scope explicit | Tasks make implementation explicit |
| Validation plan (after ship) | Test plan (before ship) |

If your PRD reads like "use PostgreSQL with this schema", you're writing a spec. Push it back up to the value/scope level. Concrete details belong in `sdd-design`.

---

## Honest limits

- The skill cannot validate that hypotheses are falsifiable. If the user writes "If we build it, users will love it" — the skill accepts it. Falsifiability requires user discipline.
- Measurement plans default to one metric — over-instrumentation kills PRDs. If you need 12 metrics, you have 12 PRDs.
- The PRD does NOT enforce that `sdd-propose` actually reads it. The user must invoke `/sdd-new <slug>` next; the integration is recommendation-based, not mechanical.

---

## See also

- `.sdlc/prds/README.md` — directory purpose
- `/sdd-new` — next step; PRD becomes proposal input
