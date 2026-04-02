---
name: brainstorming
description: "Socratic exploration of requirements before implementation. Refines spec through targeted questions. Use when user asks to 'explore options', 'refine requirements', or mentions 'unclear requirements'."
invokable: true
accepts_args: true
allowed-tools: ["Read", "Grep", "Glob"]
auto-activate: feature-development (medium+), refactor (high+)
required-sub-skill: writing-plans
version: 2.1.0
when:
  - task_type: feature
    risk_level: [medium, high, critical]
  - task_type: refactor
    risk_level: [high, critical]
  - user_mentions: ["unclear requirements", "explore options", "not sure how"]
---

# Brainstorming — Socratic Requirements Refinement

**Propósito**: Explorar y refinar requisitos ANTES de escribir código mediante preguntas socráticas que descubran edge cases, trade-offs, y decisiones de diseño.

**Cuándo se activa**: Feature development (medium risk+), architectural refactors (high risk+), spec unclear.

**References**:
- Domain-specific question templates → `references/brainstorming-templates.md`
- Examples and best practices → `references/brainstorming-examples.md`

---

## Core Principle: One Question at a Time

Never ask 20 questions at once. Ask one, wait for the answer, then ask the next.

```diff
- ❌ "I have 20 questions about this feature..."
+ ✅ "Question 1: What should happen when email verification fails?"
     [User responds]
     "Question 2: Should unverified users have limited access?"
```

---

## Phase 1 — Clarify the Problem

Ask one at a time until all 3 are answered:

```
Q1 (Scope): What specific problem does this solve for users?
Q2 (Success): How will we know this feature is successful?
Q3 (Constraints): Performance, cost, or time constraints?
```

---

## Phase 2 — Explore Edge Cases

```
Q4 (Error): What should happen when [error X] occurs?
     Options: A) Fail silently  B) Return error  C) Retry
Q5 (Concurrency): What if two users do this simultaneously?
Q6 (Scale): How many entities expected? (<100 / 1K-10K / >100K)
```

See `references/brainstorming-templates.md` for domain-specific question templates (Auth, Payment, File Upload, Bounded Context).

---

## Phase 3 — Evaluate Alternatives

```
Q7: I see two approaches:

Option A: [name]  ✅ [pro]  ❌ [con]
Option B: [name]  ✅ [pro]  ❌ [con]

Which aligns better with your goals?
```

---

## Phase 4 — Validate Understanding

Summarize before proceeding:

```
Based on your answers:
- [Decision 1]: [summary]
- [Decision 2]: [summary]
- Flow: Step 1 → Step 2 → Step 3

Does this capture your vision? [S]í / [E]ditar / [N]o
```

---

## Phase 5 — Generate DECISIONS.md (Discuss-Lock Gate)

After user confirms in Phase 4:

1. Derive `<feature-slug>` from feature name (lowercase, hyphens)
2. `mkdir -p .sdlc/specs/<feature-slug>/`
3. Copy `.sdlc/specs/DECISIONS_TEMPLATE.md` → `.sdlc/specs/<feature-slug>/DECISIONS.md`
4. Fill from brainstorming session: Problem Statement, Key Decisions (with rationale + trade-offs), Acceptance Criteria, Edge Cases, Out of Scope
5. Set `Approved: no` (user must change to `yes`)
6. Present:

```
DECISIONS.md created: .sdlc/specs/<feature-slug>/DECISIONS.md

Review it, then set `Approved: yes` to unlock Skill('plan').
¿Apruebas el documento de decisiones? [S]í / [E]ditar primero / [N]o
```

> `Skill('plan')` refuses without `Approved: yes`.
> Emergency bypass: `Skill('plan') --force` — logs to `.sdlc/knowledge/force-bypass.log`.

---

## Completion Checklist

Before transitioning to `Skill('plan')`:

- [ ] Problem understood: can articulate the "why"
- [ ] Success criteria defined: know what "done" looks like
- [ ] At least 3 edge cases explored
- [ ] Performance/cost/time constraints clarified
- [ ] At least 2 design options evaluated
- [ ] User confirmed understanding in Phase 4
- [ ] DECISIONS.md created with `Approved: yes`

---

## Integration

After brainstorming completes with approved DECISIONS.md → auto-transition to `Skill('plan')` with:
- Design document path
- Acceptance criteria
- Edge cases
- Design decisions

---

## Summary

```
IF task is unclear OR risk is medium+ OR user says "explore options"
THEN run brainstorming:
  1. Clarify problem → 2. Edge cases → 3. Alternatives
  4. Validate → 5. DECISIONS.md → Skill('plan')
```

**Remember**: 30 minutes of brainstorming saves hours of rework.

---

## See Also

| | **brainstorming** | **sop-discovery** |
|---|---|---|
| **Style** | Socratic, interactive | Autonomous research |
| **Output** | Refined requirements + DECISIONS.md | Discovery report with world-class patterns |
| **Use when** | Requirements unclear, risk medium+ | Need "how do industry leaders solve this?" |
| **Leads to** | `Skill('plan')` | `Skill('plan')` |

**Rule**: Use **brainstorming** to clarify *what to build*. Use **sop-discovery** to learn *how to build it well*.

---

**Required Sub-Skill**: `Skill('plan')` (auto-invoked after completion)
**References**: `references/brainstorming-templates.md` · `references/brainstorming-examples.md`
