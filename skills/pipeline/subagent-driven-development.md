---
name: subagent-driven-development
description: "Executes implementation plans by spawning fresh subagents per task with wave-based parallel execution and Yield Pattern. Eliminates context rot: orchestrator stays under 40% context; each subagent receives a minimal, targeted prompt."
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash(git status*)
  - Bash(git diff*)
  - Bash(git log*)
  - Bash(node*)
invokable: true
accepts_args: true
version: 3.0
source: Agent007 v5 — Yield Pattern upgrade (OpenClaw-inspired)
---

# Subagent-Driven Development (Yield Edition)

**Purpose**: Execute an implementation plan with fresh context per task, using parallel wave execution with the Yield Pattern for async fork-join coordination.

**When to activate**: After `plan`. File `docs/changes/<feature>/tasks.md` exists with `depends_on` per task.

---

## Core Concept: Yield Pattern

- **Sequential**: Dispatch A → wait → dispatch B → wait → dispatch C
- **Yield**: Identify independent tasks → spawn N agents in parallel → yield → receive all → advance

Orchestrator spawns multiple subagents simultaneously (`Agent` tool), then awaits all results before advancing. Async fork-join without blocking.

---

## Full Flow

### Phase 0 — Budget Check

Read `.sdlc/state/context-budget.json` (written by `context-engine.py` hook on every Agent spawn):

```json
{ "percent": 35, "status": "OK" }
```

If `percent > 40%`: **do not continue**. Run `/compact` then create a new clean session.

### Phase 1 — Wave Computation

Try automated wave computation first (uses topological sort):

```bash
node .claude/scripts/wave-scheduler.js --tasks docs/changes/<feature>/tasks.md --json
```

- **Exit 0** → parse JSON output as wave plan. Use these waves directly — do not re-group manually.
- **Exit 1** → fallback to manual grouping below.

Manual fallback (if wave-scheduler unavailable):
```
Wave 1: tasks with no depends_on (all independent)
Wave 2: tasks whose depends_on tasks are all in Wave 1
Wave N: tasks whose depends_on tasks are all in Wave N-1
```

**Rule**: Grouping is based ONLY on explicit `depends_on` field — not semantic judgment.

To preview the wave plan before executing:
```bash
node .claude/scripts/wave-scheduler.js --tasks docs/changes/<feature>/tasks.md --summary
```

### Phase 2 — Wave Execution with Yield Pattern

For each wave:

```
Wave N — Yield Pattern:
  ├── Identify tasks with no unmet dependencies → wave's task set
  ├── SPAWN (max 5 parallel) — multiple Agent() calls in ONE message:
  │     Agent(prompt: buildSubagentPrompt(task), subagent_type: domain_agent)
  ├── UPDATE session.json lifecycle → "wait"
  │     waitJson: { pendingSubagents: [ids], waveStartedAt: now }
  ├── YIELD — await all agent results (each emits <promise>COMPLETE/FAIL</promise>)
  ├── WAVE COMPLETE — Update session.json:
  │     lifecycle → "execute"; currentWave++; completedFiles += new; waitJson → {}; revision++
  ├── If ANY task FAIL: retry same task up to 3×; 4th → ESCALATE TO HUMAN
  ├── If spawn fails (rate-limit, overload, timeout): retry with lower model tier (opus→sonnet→haiku); log failure
  └── Advance to Wave N+1 ONLY when ALL tasks in Wave N are COMPLETE
```

### Phase 3 — Spec + Quality Review (Post-Wave)

After ALL waves complete:

```
1. Dispatch: Spec Compliance Reviewer
   → "Does code match spec exactly?"
   → Issues found → same implementer fixes → re-validate

2. Dispatch: Code Quality Reviewer
   → "No any, no N+1, no hardcoded secrets?"
   → Issues found → same implementer fixes → re-validate
```

### Phase 4 — Branch Finish

→ `finishing-a-development-branch`

---

## Subagent Prompt Format (Fork Window: LastNTurns)

Each subagent receives ONLY:
1. Identity + fixed constraints
2. `banned-phrases` (always)
3. `.sdlc/context/` snippets (max 40 lines per file)
4. Full task body (from tasks.md)
5. Verification command
6. Related file snippets (max 40 lines each, ~16k token budget total)

```
Fork mode: LastNTurns(3)
→ Last 3 relevant turns from parent context (recent decisions only)
→ Snippets of task-related files (max 40 lines each)
→ Full task body
→ Scope: "Use prior context as reference. Your primary task is below:"
```

**NEVER** pass the full plan or full unrelated files.

---

## Domain → Agent Type

| Domain | Agent type |
|--------|-----------|
| `backend` | backend-db-expert |
| `frontend` | frontend-ux-expert |
| `platform` | platform-expert |
| `security` | security-expert |
| `mixed` / no hint | platform-expert |

---

## TaskFlow Integration (session.json)

During wave (waiting for subagents):
```json
{ "lifecycle": "wait", "waitJson": { "pendingSubagents": ["TASK-042.1"], "waveStartedAt": "..." } }
```

After wave completes:
```json
{ "lifecycle": "execute", "revision": "{prev+1}", "stateJson": { "currentWave": 2, "completedFiles": [...] }, "waitJson": {} }
```

---

## Critical Guardrails

- ❌ Never > 5 subagents in parallel (Claude Code limit)
- ❌ Do not advance wave without ALL tasks in previous wave COMPLETE
- ❌ Do not start if orchestrator > 40% context
- ❌ Do not retry > 3× — escalate on 4th failure
- ❌ `max_depth: 2` — no recursive subagent spawning beyond 2 levels
- ✅ Multiple Agent() calls in ONE response = true parallelism (Yield Pattern)
- ✅ Update session.json revision after each wave
- ✅ Collect COMPLETE/FAIL + summary before advancing

---

## Ralph Integration

If `--ralph` is active, each subagent iterates autonomously until `<promise>COMPLETE</promise>`.
Wave reviewers run normally after all subagents complete.

---

## Prerequisites

- `using-git-worktrees` — isolated branch active
- `plan` — `docs/changes/<feature>/tasks.md` exists with `depends_on` per task
- Context budget < 40%
- `session.json` exists in `.sdlc/state/` (created by TaskFlow or session start)
