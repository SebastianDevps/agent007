---
name: systematic-debugging
description: "Reproduce-first debugging protocol — never claim fixed without reproducing the bug"
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Write", "Edit"]
auto-activate: bug-fixing (all levels)
required-before: Any bug fix implementation
version: 2.0.0
when:
  - task_type: bug
    risk_level: [low, medium, high, critical]
  - user_mentions: ["bug", "error", "fix", "broken", "not working", "fails"]
load_when:
  - debugging_production_issue
  - investigating_test_failure
  - diagnosing_unexpected_behavior
inputs:
  - name: bug_description
    type: string
    required: true
  - name: error_logs
    type: string
    required: false
  - name: reproduction_steps
    type: array
    required: false
outputs:
  - name: root_cause_analysis
    type: structured_report
    format: "Symptom | Root cause | Evidence | Fix | Verification"
  - name: reproduction_test
    type: string
    format: "Test that fails before fix, passes after"
constraints:
  - reproduce_bug_before_fixing
  - write_failing_test_before_implementing_fix
  - never_claim_fixed_without_verification_evidence
---

# Systematic Debugging — NO FIXES WITHOUT ROOT CAUSE

**REGLA FUNDAMENTAL**: NO BUG FIXES WITHOUT ROOT CAUSE ANALYSIS.

This skill enforces a 4-phase debugging process for any bug fix.

---

## When to Invoke

- Task classified as `bug` at any risk level
- User mentions: "bug", "error", "fix", "broken", "not working", "fails"
- Investigating a test failure or production issue
- Diagnosing unexpected behavior
- Auto-activated for bug-fixing workflows (mandatory at medium+ risk)

---

## The 4 Phases (Mandatory)

| Phase | Goal | Reference |
|-------|------|-----------|
| 1. Reproduce | Create a test that demonstrates the bug consistently (must fail) | `references/phase-1-reproduce.md` |
| 2. Root Cause | Identify the real cause via 5 Whys, stack trace, logs, diff | `references/phase-2-root-cause.md` |
| 3. Hypothesis | Propose fix and validate before implementing | `references/phase-3-hypothesis.md` |
| 4. Implementation | Implement fix + defense-in-depth + regression test | `references/phase-4-implementation.md` |

Each phase has a CHECKPOINT — cannot proceed to the next without completing the current.

---

### Phase 1.4 — Multi-Component Diagnostic Instrumentation

For EACH component boundary in the suspected path:
- Log entry: what's coming in
- Log exit: what's going out
- Log config: what's the current config state
- Log state: what's the current data state

Re-run the failing scenario. Compare boundary logs across components. The bug lives where expectations diverge from reality — usually at a boundary, not within a component.

---

## Phase 4.5 — If 3+ Fixes Failed, Question Architecture

Pattern indicating an architectural problem (not a failed hypothesis):
- Each fix reveals new shared state or coupling in a different place
- Fixes require "massive refactoring" to implement properly
- Each fix creates new symptoms elsewhere
- You're chasing the bug, not understanding it

STOP and question fundamentals:
- Is this pattern fundamentally sound for this use case?
- Are we sticking with it through sheer inertia or sunk cost?
- Should we refactor the architecture vs. continue patching symptoms?

Discuss with the user BEFORE attempting fix #4. This is NOT a failed hypothesis to retry — this is a wrong architecture to redesign.

---

## Anti-Patterns (Red Flags)

### "I Know What the Problem Is"
- WRONG: "I know it's a database issue, let me add an index"
- RIGHT: "Let me reproduce it first, then analyze root cause"
- Problem: assumptions without evidence lead to wrong fixes.

### "Quick Fix First, Investigate Later"
- WRONG: "Let me wrap it in try-catch for now, we'll debug later"
- RIGHT: "No fixes until root cause identified"
- Problem: "later" never comes; bug remains hidden.

### "It's Too Complex to Reproduce"
- WRONG: "The bug is intermittent, I'll just add more logging"
- RIGHT: "I'll create conditions that make it reproducible"
- Problem: can't fix what you can't reproduce.

### "The Fix Looks Good"
- WRONG: "This should fix it" (without running test)
- RIGHT: "Test passes, bug confirmed fixed: [output]"
- Problem: verification-enforcement should catch this.

---

## Need → Reference

| Need | Reference |
|------|-----------|
| How to write a reproducing test | `references/phase-1-reproduce.md` |
| 5 Whys, stack trace, logging techniques | `references/phase-2-root-cause.md` |
| Forming and validating a hypothesis | `references/phase-3-hypothesis.md` |
| Implementing fix with defense-in-depth | `references/phase-4-implementation.md` |
| Concrete examples by bug type (perf, security, logic, race) | `references/examples-by-bug-type.md` |
| Ralph Loop iterative debugging mode | `references/ralph-loop-integration.md` |

---

## Pre-claim Checklist (before "fixed")

**Phase 1: Reproduce**
- [ ] Test created that demonstrates bug
- [ ] Test fails reliably
- [ ] Failure is clear and specific

**Phase 2: Root Cause**
- [ ] Root cause identified (not symptom)
- [ ] 5 Whys completed
- [ ] Evidence documented
- [ ] Root cause is actionable

**Phase 3: Hypothesis**
- [ ] Solution proposed
- [ ] Expected outcome defined
- [ ] Hypothesis validated
- [ ] Alternatives considered

**Phase 4: Implementation**
- [ ] Fix implemented
- [ ] Test passes
- [ ] Defense-in-depth added (2+ safeguards)
- [ ] Regression test added
- [ ] Performance verified
- [ ] Knowledge base updated

---

## Summary

```
FOR every bug fix:
  PHASE 1: Create test that reproduces bug (must fail)
  PHASE 2: Identify root cause (not symptom)
  PHASE 3: Form hypothesis and validate
  PHASE 4: Implement + defense-in-depth + regression test

NO shortcuts. NO quick fixes. NO "I know what it is."
```

The most expensive bug is the one that comes back.

---

**Auto-Activated In**: All bug-fixing workflows (all risk levels)
**Ralph-Ready**: Yes (v2.0) — see `references/ralph-loop-integration.md`
**Can Be Skipped**: NO (mandatory for bugs medium+ risk)
**Integrates With**: test-driven-development, verification-enforcement, ralph-loop-wrapper
