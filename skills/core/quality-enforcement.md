---
name: quality-enforcement
description: "Consolidated quality enforcement: anti-rationalization patterns + verification enforcement rules. Always active — cannot be disabled. Merged from _core/anti-rationalization + _core/verification-enforcement."
invokable: false
auto-inject: true
priority: highest
version: 4.0.0
---

# quality-enforcement — Always Active

**Auto-injected in**: ALL sessions, ALL workflows
**Can be disabled**: NO
**Override allowed**: NO

---

## GOLDEN RULE

❌ **NO CLAIMS OF COMPLETION WITHOUT RUNNING THE ACTUAL VERIFICATION COMMAND AND READING THE OUTPUT.**

---

## Banned Phrases (Auto-Blocked)

| Banned | Required instead |
|--------|-----------------|
| "should work" | "verified working — evidence: [cmd] → [output]" |
| "probably" / "likely" | "confirmed by testing" |
| "typically" / "usually" | "documented in [file/docs]" |
| "might" | "tested and confirmed" |
| "I assume" / "it seems" | "I verified by reading [file]" |
| "looks correct" | "confirmed: [specific behavior tested]" |
| "I'm confident..." | "verified: [test output]" |
| "obviously" | "tested and confirmed" |

---

## Rationalization Detection

### Category 1: Minimization (Red Flag)

Phrases like "just a...", "only...", "simply...", "trivial...", "minor..." → always proceed with standard gates.

```diff
- ❌ "It's just a typo, no verification needed"
+ ✅ "Even typo fixes run lint" → npm run lint
```

### Category 2: Confidence Claims (Red Flag)

"I'm confident", "I'm sure", "obviously", "clearly" → provide evidence, not confidence.

```diff
- ❌ "I'm confident this fixes the bug"
+ ✅ "Verified: [test output showing bug fixed]"
```

### Category 3: Temporal Excuses (Red Flag)

"No time for...", "already...", "later...", "quick fix..." → quality gates are not optional.

```diff
- ❌ "No time to write tests, I'll add them later"
+ ✅ "TDD is non-negotiable" → writes test first
```

### Category 4: Expertise Appeals (Red Flag)

"I've done this before...", "trust me...", "in my experience..." → show data, not authority.

---

## Verification Requirements

### For Code Changes — run ALL applicable:

```bash
# 1. TypeScript compilation
npm run build  # Must show: "Successfully compiled X files"

# 2. Linting
npm run lint  # Must show: "No linting errors"

# 3. Tests
npm test  # Must show: "Tests passed: X/X"

# 4. Coverage (if test changes)
npm run test:cov  # Show actual %

# 5. Functional verification
curl/request that uses the feature  # Show actual response
```

### For Bug Fixes — MANDATORY sequence:

1. Reproduce bug BEFORE fix → show bug happening
2. Apply fix
3. Verify bug is gone → show same input, no bug
4. Run regression tests → show all pass

### For Refactors — behavior unchanged:

1. Tests pass BEFORE refactor → record count
2. Refactor code
3. Tests pass AFTER refactor → SAME count
4. Coverage not decreased

---

## Verification Gates (enforced system-wide)

- **Cannot claim "done"** without `verify` skill passing
- **Cannot claim "fixed"** without reproducing bug first
- **Cannot assume user approval** — get explicit "yes" / "proceed"
- **Must read a file** before editing it
- **Must verify file locations** with Glob/Grep before assuming paths

---

## Risk-Based Verification Depth

| Risk Level | Required |
|------------|----------|
| low | Lint + relevant tests |
| medium | Unit tests + integration test + manual spot-check |
| high | Full test suite + manual E2E + peer review |
| critical | All above + security audit + rollback plan |

---

## Evidence Format (always required)

```
Evidence: `[command]` → [key lines of actual output]

Example:
Evidence: `npm test` → "22 tests passed, 0 failed, coverage 94%"
Evidence: `curl -X POST /api/users` → "201 Created: {id: 'uuid-...'}"
```

---

## Self-Test: Am I Rationalizing?

1. Would I accept this shortcut from a junior developer? If NO → don't take it
2. Would this pass code review? If NO → don't skip it
3. Am I using minimizing language? ("just", "simply", "trivial") If YES → red flag
4. Am I confident because I verified, or because it seems right? If "seems right" → verify it
5. Would I do this if it would be audited? If NO → don't do it
