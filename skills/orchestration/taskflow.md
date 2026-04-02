---
name: taskflow
description: "State machine for multi-step tasks with optimistic locking. Provides session.json as authoritative machine-readable state with revision-checked mutations and crash recovery."
invokable: true
accepts_args: false
version: 1.0
source: Agent007 v5 — OpenClaw TaskFlow adaptation
---

# TaskFlow — Multi-Step State Machine

**Purpose**: Maintain durable, recoverable state for complex tasks spanning multiple iterations.
Prevents state corruption in long sessions via optimistic locking (revision field).

**Activated by**: `plan` skill, `subagent-driven-development` skill, `ralph-loop`.
**State files**: `.sdlc/state/session.json` (machine) + `.sdlc/state/session.md` (human display).

---

## Schema (session.json)

```json
{
  "taskId": "TASK-042",
  "revision": 7,
  "lifecycle": "execute",
  "stateJson": {
    "currentPhase": "generate",
    "completedFiles": ["src/user.service.ts"],
    "pendingTests": ["src/user.service.spec.ts"],
    "currentWave": 2
  },
  "waitJson": {
    "pendingSubagents": ["TASK-042.1", "TASK-042.2"],
    "waveStartedAt": "2026-04-02T20:00:00Z"
  },
  "activeTask": "TASK-042 — Implement user authentication",
  "completedTasks": [
    {"id": "TASK-041", "completedAt": "2026-04-02T19:45:00Z", "summary": "Setup DB schema"}
  ],
  "decisions": [
    "Using bcrypt for password hashing (security-expert recommendation)"
  ],
  "updatedAt": "2026-04-02T20:00:00Z"
}
```

### Lifecycle States

```
idle    → No active task. Initial state.
execute → Task in progress. stateJson has current phase details.
wait    → Paused for subagents. waitJson has pending agent IDs.
resume  → Recovering from crash or explicit resume.
finish  → Task completed successfully.
fail    → Task failed — stateJson has error details.
cancel  → Explicitly cancelled by user.
```

---

## Mutation Protocol (Optimistic Locking)

Every state mutation MUST follow this protocol to prevent revision conflicts:

### Read-Modify-Write Pattern

```python
# 1. Read current state
state = read_session_json()
current_revision = state["revision"]

# 2. Validate revision matches expectation
if current_revision != expected_revision:
    raise RevisionConflict(f"Expected {expected_revision}, got {current_revision}")

# 3. Apply mutation
state["stateJson"]["currentPhase"] = "verify"
state["revision"] = current_revision + 1
state["updatedAt"] = now_iso()

# 4. Write atomically
write_session_json(state)
```

### Revision Rules

- **Never skip revisions** — always increment by exactly 1
- **Never mutate without reading first** — always load current revision
- **On conflict**: reload state, check if mutation is still needed, retry or escalate
- **On crash recovery**: revision integrity is preserved — resume from last committed state

---

## Crash Recovery Protocol

When a session starts and `session.json` shows `lifecycle: "execute"` or `lifecycle: "wait"`:

```
📋 RECOVERY DETECTED
TaskFlow state shows in-progress work:
  Task:      {taskId}
  Phase:     {stateJson.currentPhase}
  Revision:  {revision}
  Updated:   {updatedAt}

Resume options:
  [S] Continue from {stateJson.currentPhase}
  [R] Restart task from beginning
  [A] Abandon — mark as failed
```

The recovery banner is shown by `session_protocol` in CLAUDE.md on session start.

---

## Wave Advancement (Yield Pattern Integration)

After a wave of subagents completes (see `subagent-driven-development`):

```python
# After all subagents in wave N complete:
state = read_session_json()
state["stateJson"]["currentWave"] += 1
state["stateJson"]["completedFiles"].extend(new_files)
state["waitJson"] = {}           # Clear wait state
state["lifecycle"] = "execute"   # Back to active
state["revision"] += 1
state["updatedAt"] = now_iso()
write_session_json(state)
```

---

## Integration with session.md

`state-sync.py` Stop hook reads `session.json` and renders it to `session.md` for human display.
`session.md` is the human-readable view; `session.json` is the authoritative machine state.

If `session.json` doesn't exist, `state-sync.py` falls back to legacy `session.md`-only behavior.

---

## Quick Reference

| Operation | Python snippet |
|-----------|---------------|
| Start task | `set_lifecycle("execute"); set_state({"currentPhase": "plan"})` |
| Advance phase | `set_state({"currentPhase": "generate"}); increment_revision()` |
| Start wave wait | `set_lifecycle("wait"); set_wait({"pendingSubagents": [...]})` |
| Complete wave | `set_lifecycle("execute"); clear_wait(); increment_revision()` |
| Finish task | `set_lifecycle("finish"); append_completed(taskId)` |
| Mark failed | `set_lifecycle("fail"); set_state({"error": "..."})` |

---

## Guardrails

- ❌ Never write `session.json` without incrementing `revision`
- ❌ Never read `session.md` as source of truth for machine operations — use `session.json`
- ❌ Never set `lifecycle: "execute"` without populating `stateJson.currentPhase`
- ✅ Always write `updatedAt` on every mutation
- ✅ On crash recovery, show banner before any automatic action
- ✅ `session.md` is always derived from `session.json`, never the other way around
