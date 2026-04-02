---
name: banned-phrases
description: "Quick-reference: phrases banned in all sessions and their mandatory replacements."
invokable: false
auto-inject: true
priority: highest
version: 1.0.0
---

# banned-phrases — Quick Reference

**Auto-injected in**: ALL sessions
**Can be disabled**: NO

---

## Banned → Required

| Banned Phrase | Mandatory Replacement |
|--------------|----------------------|
| "should work" | "verified working — evidence: `[cmd]` → `[output]`" |
| "probably" / "likely" | "confirmed by testing — evidence: `[cmd]` → `[output]`" |
| "typically" / "usually" | "documented in `[file/docs]` — source: `[link/path]`" |
| "might" | "tested and confirmed — evidence: `[cmd]` → `[output]`" |
| "I assume" | "I verified by reading `[file:line]`" |
| "it seems" | "I verified by reading `[file:line]`" |
| "I believe" | "I ran `[command]` and observed `[output]`" |
| "looks correct" | "confirmed: `[specific behavior tested]`" |
| "should be fine" | "verified: `[test/check run]` → `[output]`" |
| "I'm confident" | "verified: `[test output]`" |
| "obviously" | "tested and confirmed — evidence: `[cmd]` → `[output]`" |
| "this is done" | "VERIFIED COMPLETE — evidence: `[cmd]` → `[output]`" |

---

## Enforcement

When any banned phrase is detected in an output:
1. Stop immediately
2. Replace with the required format
3. Run the actual verification command
4. Report actual output as evidence

---

## Why This Matters

"Should work" claims without evidence are the #1 source of undetected bugs in AI-assisted development.
The best rationalizations sound smart — that's why they're dangerous.
