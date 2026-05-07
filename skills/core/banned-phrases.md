---
name: banned-phrases
description: "SINGLE SOURCE — Banned phrases and required replacements. Auto-injected in all sessions. quality-enforcement.md references this table."
invokable: false
auto-inject: true
priority: highest
version: 2.0.0
---

# banned-phrases — Single Source of Truth

**Auto-injected in**: ALL sessions
**Can be disabled**: NO
**Referenced by**: `quality-enforcement.md` (do NOT duplicate this table elsewhere)

---

## Banned → Required (canonical table)

| Banned phrase | Mandatory replacement |
|---|---|
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
| "obviously" / "clearly" | "tested and confirmed — evidence: `[cmd]` → `[output]`" |
| "this is done" | "VERIFIED COMPLETE — evidence: `[cmd]` → `[output]`" |
| "just a..." / "only..." / "simply..." / "trivial..." / "minor..." | "even minor changes run through standard gates — evidence: `[cmd]` → `[output]`" |

---

## Enforcement protocol

When any banned phrase is detected:
1. Stop immediately
2. Replace with the required format
3. Run the actual verification command
4. Report actual output as evidence

---

## Why this matters

"Should work" claims without evidence are the #1 source of undetected bugs in AI-assisted development. The most rationalizing phrases sound the smartest — that's why they're dangerous.
