---
name: sop-reviewer
description: "SDD compliance review: validates scenarios preceded code, tests have integrity, and implementation matches spec."
invokable: true
version: 1.0.0
---

# sop-reviewer

> SDD compliance review. Validates that scenarios preceded code, tests have integrity, and implementation matches spec. Ported from ai-framework (Dario-Arcos).

---

## When to invoke

- After `sop-code-assist` completes a task
- Within `subagent-driven-development` review stage
- Mode: `interactive` (default) or `autonomous` (subagent context)

---

## What gates CANNOT catch (why this reviewer exists)

Automated quality gates verify:
- Tests pass ✓
- Types compile ✓
- Lint clean ✓
- Build succeeds ✓

But gates CANNOT verify:
- Were scenarios written BEFORE or AFTER production code?
- Were tests weakened to pass instead of fixing code?
- Does implementation actually match the scenario intent?
- Is test coverage real or theater?

This reviewer catches what gates miss.

---

## Review Protocol

### Stage 1 — Process Compliance (SDD verification)

```bash
# Check git history: scenarios before production code?
git log --follow --format="%H %s %aI" -- docs/scenarios/*.md
git log --follow --format="%H %s %aI" -- src/[feature]/*.ts

# Scenario commit timestamp must be EARLIER than implementation
```

If production code was committed before scenario: **FAIL — reward hacking detected**.

```bash
# Check if scenarios were modified after implementation
git diff HEAD~5..HEAD -- docs/scenarios/
# If scenario was weakened: FAIL
```

### Stage 2 — Test Integrity

For each test file related to the task:

```bash
# Count assertions
grep -c "expect\|assert\|toBe\|toEqual\|toHaveLength" test-file.test.ts
```

Check:
- [ ] Assertions use concrete values (`toBe(42)`) not existence checks (`toBeDefined()`)
- [ ] Negative cases tested (what happens when input is wrong?)
- [ ] Edge cases from scenario are actually tested
- [ ] No mocked core logic (mocks only external dependencies)

### Stage 3 — Specification Compliance

Compare task requirements against implementation:

| Requirement | Implemented | Evidence |
|-------------|-------------|----------|
| [req from task] | yes/no | [file:line] |

All requirements must be `yes`. Partial implementation = FAIL.

### Stage 4 — Security Spot-Check

- [ ] No secrets hardcoded
- [ ] Input validated before use (no direct user input to DB queries)
- [ ] Authentication checked for protected routes
- [ ] Sensitive data not logged

---

## Output

### PASS format:
```
REVIEW: PASS
Task: [TASK-ID]
SDD Compliance: scenarios committed [timestamp] before code [timestamp]
Test Integrity: [N] assertions, concrete values, edge cases covered
Spec Compliance: all [N] requirements implemented
Security: no issues found
```

### FAIL format:
```
REVIEW: FAIL
Task: [TASK-ID]

Critical Issues (must fix before merge):
1. [Issue description with file:line evidence]
2. [Issue description]

Required Actions:
1. [Specific fix required]
2. [Specific fix required]
```

---

## Autonomous Mode (subagent context)

When `mode="autonomous"`:
- Complete all 4 stages without pausing
- Write full review to `.claude/reviews/task-[id]-review.md`
- Send 8-word summary to lead (via TaskUpdate or SendMessage)
  - PASS: "Task [N]: [feature] implemented, tests passing, committed"
  - FAIL: "Task [N]: FAIL — [specific issue in 4 words]"

---

## Integration

```
sop-code-assist → [sop-reviewer] → lead sees 8-word summary
                       └─ full review saved to disk
```
