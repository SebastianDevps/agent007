---
name: agent-self-diagnosis
description: "4-phase loop-detection and recovery protocol. Fires when an agent detects it is stuck or repeating the same tool call with no progress — before tool-loop-detection circuit-breaks at 30 calls."
allowed-tools:
  - Read
  - Grep
  - Glob
invokable: true
auto-activate: "when same tool called 3+ times with no progress, or when agent is stuck"
version: 1.0.0
constraints:
  - diagnose_before_retry
  - ban_retry_with_different_wording
  - report_root_cause
---

# Agent Self-Diagnosis

## When to Activate

Activate this skill when ANY of the following is true:
- The same tool has been called 3+ times with no observable progress
- The last 3 actions all failed with the same or similar error
- You have rephrased the same action twice and it still did not work
- You are about to retry something for the third time

Do NOT wait for `tool-loop-detection` to circuit-break at 30 calls. Self-diagnose early.

---

## Phase 1 — Capture

Stop all retries immediately. Do not attempt anything new until Phase 4 completes.

Record the following:
1. Last 3 tool calls: tool name, inputs, and outputs (verbatim error messages if any)
2. What was expected to happen
3. What actually happened
4. How many times this action (or a variation of it) has been attempted

---

## Phase 2 — Diagnose

Match the captured failure against the known failure patterns below. Pick the single best match.

| Pattern | Signal |
|---|---|
| `WRONG_TOOL` | Used a tool but a different tool would have worked (e.g. Bash instead of Edit) |
| `MISSING_CONTEXT` | The action required information that was never provided or read |
| `WRONG_ASSUMPTION` | The premise of the action was false (file doesn't exist, API is different, etc.) |
| `PERMISSION_BLOCKED` | A hook, permission gate, or OS restriction blocked the action |
| `EXTERNAL_DEPENDENCY` | Waiting on something outside agent control (network, service, user input) |
| `SCOPE_CREEP` | The task grew beyond what was originally defined and the agent lost track of the goal |

---

## Phase 3 — Recover

Apply exactly one corrective action based on the diagnosed pattern. Do not retry the original action.

| Pattern | Corrective Action |
|---|---|
| `WRONG_TOOL` | Switch to the correct tool. Document which tool and why it is the right one. |
| `MISSING_CONTEXT` | Stop. Ask the user one specific question to obtain the missing context. Do not proceed until answered. |
| `WRONG_ASSUMPTION` | State the false assumption explicitly. Ask the user to confirm or correct it before proceeding. |
| `PERMISSION_BLOCKED` | Surface the exact block to the user (copy the error verbatim). Do not attempt workarounds. |
| `EXTERNAL_DEPENDENCY` | Pause. Notify the user of the specific blocker and what is needed to unblock. |
| `SCOPE_CREEP` | Return to the original task scope. Document what was deferred so it is not lost. |

**Banned recovery strategies:**
- Retrying with different wording
- Trying the same approach with slightly different parameters
- Silently switching strategies without reporting the diagnosis

---

## Phase 4 — Report

Output this block before taking any further action:

```
LOOP_DIAGNOSIS:
  pattern: [WRONG_TOOL|MISSING_CONTEXT|WRONG_ASSUMPTION|PERMISSION_BLOCKED|EXTERNAL_DEPENDENCY|SCOPE_CREEP]
  attempts: [N]
  last_action: [what was tried — one sentence]
  root_cause: [why it failed — one sentence]
  corrective_action: [what is being done instead — one sentence]
  escalate_to_human: [yes|no]
```

Set `escalate_to_human: yes` when:
- The pattern is `PERMISSION_BLOCKED` or `EXTERNAL_DEPENDENCY`
- More than 5 total attempts were made before diagnosis
- The corrective action requires information only the user can provide
