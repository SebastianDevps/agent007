---
name: requesting-code-review
version: 1.0
description: "Two-stage code review: stage 1 checks spec compliance, stage 2 checks code quality. Use after each task in subagent-driven-development."
accepts_args: true
---

# /requesting-code-review — Two-Stage Review

**When**: After every implementation task in `/subagent-driven-development`.

---

## Stage 1 — Spec Compliance

Ask: **"Does this code match the task specification exactly?"**

Check:
- Every acceptance criterion implemented
- Every edge case handled
- Verification command actually passes
- No missing functionality

Severity:
- **Critical/Important** → block. Same implementer fixes before Stage 2.
- **Minor** → can defer with user approval.

---

## Stage 2 — Code Quality

Ask: **"Does this code meet quality standards?"**

Check:
- No `any` types (TypeScript) / no implicit globals (JS)
- No N+1 queries
- No hardcoded secrets or credentials
- Tests cover happy path + at least 2 edge cases
- No TODO comments left in implementation
- Error handling at boundaries (user input, external calls)

Severity:
- **Critical/Important** → block. Same implementer fixes.
- **Minor** → note for future, don't block.

---

## Output Format

```
## Review: <task name>

### Stage 1 — Spec Compliance: [PASS|FAIL]
[Issues found, or "All criteria met"]

### Stage 2 — Code Quality: [PASS|FAIL]
[Issues found, or "No quality issues"]

### Verdict: [APPROVED|NEEDS FIXES]
```

---

## Rules

- ❌ Never advance to next task if Stage 1 or Stage 2 is FAIL
- ✅ Same implementer always does the fixes (continuity of context)
- ✅ After fixes → re-run both stages from scratch
