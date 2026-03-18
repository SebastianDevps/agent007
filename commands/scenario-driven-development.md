---
name: scenario-driven-development
version: 1.0
description: "Anti-reward-hacking development methodology. Scenarios are external holdout sets that cannot be modified to pass code."
accepts_args: true
---

# scenario-driven-development

> Anti-reward-hacking development methodology. Scenarios are external holdout sets that Claude cannot modify. Ported from ai-framework (Dario-Arcos).

---

## Iron Law

**NO PRODUCTION CODE WITHOUT A DEFINED SCENARIO FIRST.**

Scenarios live in spec files (external). Tests live in the codebase (internal).
Claude can modify tests. Claude cannot modify scenarios.
This is the fundamental anti-reward-hacking guarantee.

---

## Scenario vs Test

| | Scenario | Test |
|---|---|---|
| Lives in | `docs/scenarios/` or spec file | `src/` or `test/` |
| Written by | Developer / Product / Claude (with approval) | Claude |
| Can Claude modify? | **NO** | Yes |
| Purpose | Define expected behavior | Verify implementation |
| Format | Concrete inputs + expected outputs | Executable code |
| Timing | BEFORE production code | BEFORE production code (TDD) |

---

## The SCENARIO → SATISFY → REFACTOR Cycle

```
┌─────────────────────────────────────────────┐
│  PHASE 1: SCENARIO                          │
│  Define observable behavior with:           │
│  - Concrete inputs (not "a user")           │
│  - Concrete expected outputs (not "works")  │
│  - Edge cases included                      │
│  Scenario must FAIL before Phase 2 starts   │
└────────────────┬────────────────────────────┘
                 │ ↓
┌────────────────▼────────────────────────────┐
│  PHASE 2: SATISFY                           │
│  Write minimum code to satisfy scenarios.   │
│  Convergence: probabilistic, not boolean.   │
│  Run scenarios repeatedly.                  │
│  Code converges toward scenarios.           │
│  NEVER modify scenarios to pass code.       │
└────────────────┬────────────────────────────┘
                 │ ↓
┌────────────────▼────────────────────────────┐
│  PHASE 3: REFACTOR                          │
│  Improve code quality.                      │
│  Scenarios must still pass.                 │
│  If refactor breaks scenario: fix code.     │
└─────────────────────────────────────────────┘
```

---

## Good vs Bad Scenarios

### Bad scenario (vague, unverifiable):
```
Scenario: Bill splitting works correctly
When a user splits a bill
Then each person pays their share
```

### Good scenario (concrete, verifiable):
```
Scenario: Equal 3-way split with remainder cent
Given a bill of $10.00
And 3 people splitting equally
When split is calculated
Then person 1 pays $3.34
And person 2 pays $3.33
And person 3 pays $3.33
And total equals $10.00 exactly
```

### Key requirements for a valid scenario:
- [ ] Concrete numeric/string values (no "a user", "some data")
- [ ] Verifiable without reading source code
- [ ] Fails before implementation exists
- [ ] Unambiguous expected output
- [ ] Edge cases modeled with real values

---

## Workflow

### Step 1 — Define Scenario
```bash
# Create scenario file
mkdir -p docs/scenarios
cat > docs/scenarios/[feature].md << 'EOF'
# Scenario: [Feature Name]

## Scenario 1: Happy path
Given: [concrete input]
When: [concrete action]
Then: [concrete expected output]

## Scenario 2: Edge case
...
EOF
```

### Step 2 — Confirm Scenario Fails
```bash
# Run test that corresponds to scenario
npm test -- --testNamePattern="[scenario name]"
# MUST see: FAIL
```

If scenario passes without implementation: the scenario is wrong (too vague) or already implemented.

### Step 3 — Implement Minimum Satisfying Code
Write only what is needed to satisfy the scenario.
No gold-plating. No extra features.

### Step 4 — Verify Convergence
```bash
npm test
# All scenarios: PASS
# 0 scenarios: modified
```

### Step 5 — Anti-Reward-Hacking Checklist
- [ ] Were scenarios written BEFORE implementation? (git log confirms)
- [ ] Were any scenarios modified to match implementation? (git diff scenarios/ — must be empty)
- [ ] Do assertions count the same or more than before? (no precision degradation)
- [ ] Do scenarios test BEHAVIOR, not implementation details?
- [ ] Would a different correct implementation also pass all scenarios?

### Step 6 — Invoke `verification-before-completion`

---

## Integration with existing Agent007 workflow

```
feature task
  └── /scenario-driven-development
        ├── Phase 1: Scenarios defined, reviewed by user
        ├── Phase 2: TDD implementation (RED → GREEN → REFACTOR, internal to SDD)
        ├── Phase 3: Anti-reward-hacking checklist
        └── /verification-before-completion
```

---

## Anti-patterns (reward hacking signals)

| Pattern | What it means |
|---------|---------------|
| Scenarios written AFTER implementation | Code-first scenario — worthless as holdout |
| Assertion count decreased | Tests weakened to pass |
| `expect(x).toBeDefined()` replacing `expect(x).toBe(42)` | Precision evasion |
| Scenarios modified after implementation started | Reward hacking |
| All scenarios passing on first implementation attempt | Scenarios were too easy/vague |
| Mock replacing real assertion | Coverage theater |

---

## See Also

- **TDD cycle** (RED → GREEN → REFACTOR) is embedded in Phase 2 of this skill. The standalone `tdd` skill was deprecated — SDD supersedes it by adding the scenario/holdout-set layer before implementation begins.
- **verification-before-completion**: always invoke after Phase 3 to produce evidence of convergence.
- **sop-discovery**: when the task requires referent research (existing world-class implementations) before writing scenarios.
