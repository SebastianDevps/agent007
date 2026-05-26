---
name: quality-enforcement
description: "Anti-rationalization patterns + verification enforcement. Always active. Banned phrases live in banned-phrases.md (single source) — this file references it."
invokable: false
auto-inject: true
priority: highest
version: 5.0.0
references:
  - banned-phrases.md
---

# quality-enforcement — Always Active

**Auto-injected in**: ALL sessions, ALL workflows
**Can be disabled**: NO

---

## GOLDEN RULE

❌ **NO CLAIMS OF COMPLETION WITHOUT RUNNING THE ACTUAL VERIFICATION COMMAND AND READING THE OUTPUT.**

---

## Banned phrases

See `banned-phrases.md` (single source of truth). Do NOT duplicate the table here.

---

## Rationalization detection

### Category 1: Minimization (red flag)

"just a...", "only...", "simply...", "trivial...", "minor..." → always proceed with standard gates.

```diff
- ❌ "It's just a typo, no verification needed"
+ ✅ "Even typo fixes run lint" → npm run lint
```

### Category 2: Confidence claims (red flag)

"I'm confident", "I'm sure", "obviously", "clearly" → provide evidence, not confidence.

```diff
- ❌ "I'm confident this fixes the bug"
+ ✅ "Verified: [test output showing bug fixed]"
```

### Category 3: Temporal excuses (red flag)

"No time for...", "already...", "later...", "quick fix..." → quality gates are not optional.

```diff
- ❌ "No time to write tests, I'll add them later"
+ ✅ "TDD is non-negotiable" → writes test first
```

### Category 4: Expertise appeals (red flag)

"I've done this before...", "trust me...", "in my experience..." → show data, not authority.

---

## Verification requirements

### Code changes — run all applicable

```bash
npm run build  # "Successfully compiled X files"
npm run lint   # "No linting errors"
npm test       # "Tests passed: X/X"
npm run test:cov  # show actual %
# Functional: curl/request → show actual response
```

### Bug fixes — mandatory sequence

1. Reproduce bug BEFORE fix → show bug happening
2. Apply fix
3. Verify bug gone → same input, no bug
4. Run regression tests → all pass

### Refactors — behavior unchanged

1. Tests pass BEFORE → record count
2. Refactor
3. Tests pass AFTER → SAME count
4. Coverage not decreased

---

## Verification gates (system-wide)

- Cannot claim "done" without `Skill('verify')` passing
- Cannot claim "fixed" without reproducing bug first
- Cannot assume user approval — get explicit "yes" / "proceed"
- Must read a file before editing it
- Must verify file locations with Glob/Grep before assuming paths

---

## Risk-based verification depth

| Risk level | Required |
|---|---|
| low | Lint + relevant tests |
| medium | Unit + integration + manual spot-check |
| high | Full suite + manual E2E + peer review |
| critical | All above + security audit + rollback plan |

---

## Evidence format (always required)

```
Evidence: `[command]` → [key lines of actual output]

Examples:
Evidence: `npm test` → "22 tests passed, 0 failed, coverage 94%"
Evidence: `curl -X POST /api/users` → "201 Created: {id: 'uuid-...'}"
```

---

## Self-test: am I rationalizing?

1. Would I accept this shortcut from a junior? If NO → don't take it
2. Would this pass code review? If NO → don't skip it
3. Am I using minimizing language? If YES → red flag
4. Confident because I verified, or because it seems right? "Seems right" → verify
5. Would I do this if audited? If NO → don't do it
