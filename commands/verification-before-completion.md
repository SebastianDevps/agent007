---
name: verification-before-completion
version: 1.0
description: "Mandatory gate before any completion claim: 6-step verification protocol with evidence of working state."
accepts_args: true
---

# verification-before-completion

> **MANDATORY gate before any completion claim.** Ported from ai-framework (Dario-Arcos).

## Trigger Phrases (auto-invoke this skill when detected)

- "I've completed..."
- "The task is done..."
- "Everything is working..."
- "I've implemented..."
- "This should work" ← blocked phrase
- "Probably passes" ← blocked phrase
- "Looks correct" ← blocked phrase

---

## The 6-Step Verification Protocol

### Step 1 — IDENTIFY
State exactly what was implemented:
```
Implemented: [feature/fix name]
Files changed: [list]
Expected behavior: [concrete description]
```

### Step 2 — RUN
Execute the relevant verification command. No skipping.
```bash
# Run tests
npm test / pytest / go test ./... / cargo test

# Or run the specific verification
[user-provided verification command]
```

If no test suite exists: describe the manual verification steps and execute them.

### Step 3 — READ
Read the actual output completely. Do NOT skim.
- Note passing count
- Note failing count
- Note any warnings
- Note coverage if available

### Step 4 — VERIFY
Cross-check output against requirements:

| Requirement | Evidence | Status |
|-------------|----------|--------|
| [req 1] | [actual output line] | ✓/✗ |
| [req 2] | [actual output line] | ✓/✗ |

### Step 5 — SATISFY
If all checks pass: proceed to Step 6.
If ANY check fails:
- Document the failure
- Root cause the failure
- Fix the issue
- Return to Step 2 (never skip back to Step 5)

### Step 6 — CLAIM
Only now make a completion claim, using evidence format:

```
VERIFIED COMPLETE
Evidence: `[command]` → [actual output summary]
Tests: [N passing, 0 failing]
Behavior: [concrete confirmation of what was verified]
```

---

## Prohibited Completion Phrases

Never use these without evidence:

| Prohibited | Required instead |
|------------|-----------------|
| "should work" | `[command] → [output]` |
| "probably passes" | "verified: N tests passing" |
| "looks correct" | "confirmed: [specific behavior tested]" |
| "I believe" | "I ran [command] and observed [output]" |
| "seems to work" | "tested with [input], got [output]" |
| "typically" | "confirmed in [file/test/docs]" |

---

## Risk-Based Verification Depth

| Risk Level | Required Verification |
|------------|----------------------|
| low | Run relevant unit tests |
| medium | Unit tests + integration test + manual spot-check |
| high | Full test suite + manual E2E + peer review checklist |
| critical | All of above + security audit + rollback plan |

---

## Evidence Format (required)

```
[command run] → [key lines of actual output]

Example:
npm test → "22 tests passed, 0 failed, coverage 94%"
curl -X POST /api/users → "201 Created: {id: 'uuid-...'}"
```

---

## Integration with ralph-loop

When used in ralph context, emit completion promise ONLY after verification passes:

```
<promise>COMPLETE</promise>
Evidence: [command] → [output]
```

Never emit `<promise>COMPLETE</promise>` speculatively.
