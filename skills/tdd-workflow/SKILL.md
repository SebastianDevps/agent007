---
name: tdd-workflow
description: "Red-Green-Refactor gate — forces a failing test BEFORE any implementation. No code is written until there is a failing test that proves the requirement exists."
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Write", "Edit"]
auto-activate: when implementing new behavior
version: 1.0.0
when:
  - task_type: feature
  - task_type: refactor
constraints:
  - write_failing_test_before_implementation
  - implementation_must_make_test_pass
  - refactor_must_not_break_test
---

# TDD Workflow — Red-Green-Refactor Gate

**Purpose**: Pre-implementation gate. Enforces the Red-Green-Refactor cycle so that tests define behavior before code exists. The `verify` skill validates after implementation — this skill gates the start.

**Hard rule**: If a test file for the target behavior does not exist and is not failing before implementation begins, STOP. Write the test first.

---

## The Iron Law

NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST

Write code before the test? **Delete it. Start over.**

No exceptions:
- Don't keep it as "reference"
- Don't "adapt" it while writing tests
- Don't look at it
- Delete means delete

Implement fresh from tests. Period.

---

## Phase 1 — RED: Write the Failing Test

Before touching any implementation file:

1. Identify the observable behavior being added (from the feature description or SDD spec).
2. Locate or create the test file for the module under test.
3. Write the minimum test that describes the expected behavior:
   - Test public API / behavior, never internal implementation details.
   - Use descriptive test names: `"given X, when Y, then Z"`.
   - One assertion cluster per test — do not combine multiple scenarios.
4. Run the test suite. **The new test MUST fail.**

**Required evidence before proceeding to GREEN:**
```
$ <test-runner> <test-file>
FAIL — <test name>
Expected: <what>
Received: <what>
```

If the test passes without implementation → the test is wrong. Rewrite it.

**Banned at this phase:**
- Writing any implementation code before the test fails.
- Modifying existing passing tests to accommodate new behavior (add new tests instead).

---

## Phase 2 — GREEN: Minimal Implementation

Goal: make the failing test pass with the least code possible.

1. Write only enough code to satisfy the failing test.
2. Do not over-engineer — no abstractions, no "future-proofing" at this phase.
3. Run the test suite. **The new test MUST pass. All pre-existing tests MUST still pass.**

**Required evidence before proceeding to REFACTOR:**
```
$ <test-runner> <test-file>
PASS — <test name>
Tests: X passed, 0 failed
```

If pre-existing tests break → fix the implementation, not the tests.

---

## Phase 3 — REFACTOR: Clean Without Breaking

Goal: improve code quality without changing behavior.

1. Remove duplication introduced during GREEN.
2. Apply naming conventions from `.claude/rules/coding-style.md`.
3. Extract helpers if function body exceeds 20 lines.
4. Run the full test suite after every refactor step.

**Required evidence at exit:**
```
$ <test-runner>
PASS — all tests
Coverage: >= prior coverage
```

**Refactor is complete when**: code reads cleanly AND test suite is green AND coverage has not decreased.

---

## Anti-Patterns — Reject Immediately

| Signal | Action |
|--------|--------|
| "I'll add tests later" | STOP — no implementation until test exists |
| Test written after code already passes | STOP — test proves nothing; delete and restart from RED |
| Test asserts on private methods or internal state | Rewrite to test public behavior only |
| Test modified to make code pass | STOP — scenarios are holdout sets; fix the implementation |
| Skipped test to unblock GREEN | STOP — a skipped test is not evidence |

---

## Common Rationalizations (and the Truth)

| Rationalization | Truth |
|---|---|
| "I'll just sketch it first, then test it" | You'll keep the sketch. Delete it. |
| "This is too simple to test" | Simple things break in surprising ways. Test it. |
| "I already know how it should work" | Then write the test first — it's faster. |
| "The test would just mirror the impl" | Then the test is wrong. Test behavior, not code. |
| "I'll backfill the tests later" | You won't. Or you'll write tests that match the bug. |
| "This is a prototype" | Prototypes ship. Test it. |
| "I'm just fixing one line" | One-line fixes have caused production outages. Reproduce first. |
| "The test framework doesn't support this" | Pick a framework that does, or refactor the code to be testable. |
| "It's just a quick spike" | Spikes become permanent. Test or delete. |
| "Mocking is too painful here" | Painful mocking signals coupling problems. Refactor. |
| "I'll use the type system instead of tests" | Types catch a subset. Test the rest. |
| "Tests are slow / I'll skip them this once" | Slow tests are technical debt. Fix or accept. |

---

## Exit Criteria

A TDD cycle is complete when ALL of the following are true:

- [ ] A failing test existed before any implementation was written (RED evidence on record).
- [ ] The implementation was written to satisfy that test (GREEN evidence on record).
- [ ] The test suite passes fully after refactor (REFACTOR evidence on record).
- [ ] Coverage is maintained or increased.
- [ ] No implementation detail is exposed through the test (tests call public API only).

Hand off to `Skill('verify')` only after all five boxes are checked.
