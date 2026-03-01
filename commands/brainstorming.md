---
name: brainstorming
version: 1.0
description: "Socratic exploration of requirements before implementation. Ask one targeted question at a time to clarify spec, discover edge cases, and validate design before writing any code."
accepts_args: true
---

# /brainstorming — Socratic Requirements Refinement

**Activation**: Before implementing any medium/complex feature or unclear spec.

---

## Process

### Phase 1 — Clarify the problem (1-2 questions)

Ask ONE question at a time. Wait for answer before proceeding.

```
Q1: What specific problem does this solve? What is success?
Q2: Are there performance, cost, or time constraints?
```

### Phase 2 — Edge cases (2-3 questions)

```
Q3: What happens when [most likely error scenario]?
Q4: What if the user does [action] twice / concurrently?
Q5: What happens at scale? (< 100 / 1K-10K / > 100K entities)
```

### Phase 3 — Design alternatives (1 question)

Present exactly 2 options with pros/cons:

```
Option A: [approach] — ✅ [pro] ❌ [con]
Option B: [approach] — ✅ [pro] ❌ [con]
Which fits better?
```

### Phase 4 — Validate understanding

```
Let me confirm: [summary of all answers]
Flow: [step 1] → [step 2] → [step 3]
Correct? [Y/N]
```

---

## Rules

- ❌ Never ask more than 1 question at once
- ❌ Never start implementing until Phase 4 is confirmed
- ✅ Document all decisions in the design doc output
- ✅ Output: design doc with decisions + acceptance criteria + edge cases table

**Next step after completion**: `/writing-plans`
