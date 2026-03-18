---
name: sop-planning
description: "Structured decomposition of a feature into phases, tasks, and atomic task file. Runs after sop-discovery. Combines planning + task generation into one step. Ported from ai-framework (Dario-Arcos)."
invokable: true
accepts_args: false
version: 2.0.0
---

# sop-planning

> Structured decomposition of a feature into executable phases and atomic tasks. Runs after sop-discovery. Generates the task file used by sop-code-assist and subagent-driven-development.

---

## When to invoke

- After `sop-discovery` has been completed
- Before `sop-code-assist` or `subagent-driven-development`
- When building complex features requiring careful sequencing

---

## Pre-conditions (must be met before planning)

- [ ] `sop-discovery` output available
- [ ] Requirements clearly stated
- [ ] Tech stack confirmed
- [ ] Constraints documented (auth, performance, security)

---

## Phase 1 — Goal Restatement

Write the goal in your own words, then confirm with the user:
```
GOAL: [restate in concrete terms]
SUCCESS LOOKS LIKE: [observable behavior, not implementation]
OUT OF SCOPE: [explicit exclusions]
```

---

## Phase 2 — Unknown Identification

List what is unknown BEFORE writing any plan:
- Unknown architecture decisions: [list]
- Unknown data requirements: [list]
- Unknown integration points: [list]
- Unknown edge cases: [list]

Resolve unknowns via:
1. `sop-discovery` references
2. Reading existing codebase (Glob + Grep + Read)
3. Asking the user (1 question at a time)

Do NOT proceed to Phase 3 with unresolved unknowns.

---

## Phase 3 — Dependency Mapping

Draw the task dependency graph:
```
[Task A] ──→ [Task B] ──→ [Task D]
              └──→ [Task C] ──→ [Task D]
```

Tasks with no incoming arrows: can start immediately.
Tasks with incoming arrows: must wait for dependencies.

---

## Phase 4 — Risk Assessment

| Task | Risk | Mitigation |
|------|------|-----------|
| [task] | high/medium/low | [specific action] |

High-risk tasks (auth, payments, migrations, breaking changes):
- Must be isolated in their own worktree
- Require explicit user approval before execution
- Require rollback plan documented before starting

---

## Phase 5 — Execution Plan

For each phase, define:

```markdown
## Phase 1: [Name]
Goal: [what this phase achieves]
Tasks: [count]
Dependencies: [none / Phase X]

### Task 1.1: [Name]
File: [exact path]
Action: [create/edit/delete]
Implementation: [3-5 bullet points, not pseudocode]
Test: [what command verifies this works]
Duration: [2-5 minutes]
```

---

## Mandatory Checkpoint

Present the full plan to the user and get explicit "proceed" before any implementation.

```
Plan ready. [N] phases, [M] tasks estimated.
Proceed? [Y/n]
```

On approval: proceed to Phase 6 (task file generation).

---

## Phase 6 — Task File Generation

After user approval, generate the atomic task list.

### Task Requirements

Each task MUST have:
1. **Unique ID** (e.g., `TASK-001`)
2. **Exact file path** (no "somewhere in the auth module")
3. **Concrete implementation steps** (not "implement the service")
4. **Scenario/test** (what proves it works)
5. **Verification command** (runnable command, not "check manually")
6. **Dependencies** (other task IDs, or "none")
7. **Duration estimate** (2-5 minutes ideal, max 15 minutes)

### Task File Format

Save tasks to `docs/changes/<feature>/tasks.md`:

```markdown
# Task List: [Feature Name]
Generated: YYYY-MM-DD
Total tasks: N

---

## TASK-001: [Short imperative description]
**Status**: pending
**File**: src/auth/auth.service.ts
**Dependencies**: none

### Scenario
Given: [concrete input]
When: [action]
Then: [concrete expected output]

### Implementation Steps
1. Add `refreshToken(token: string): Promise<TokenPair>` method
2. Validate token signature and expiry
3. Invalidate old token in Redis (key: `refresh:{userId}`)
4. Issue new access token (15min) and refresh token (7d)
5. Return `{ accessToken, refreshToken }` pair

### Verification
\`\`\`bash
npm test -- --testNamePattern="refreshToken"
# Expected: 3 tests passing
\`\`\`

**Duration**: 5min

---

## TASK-002: [Next task]
**Status**: pending
**Dependencies**: TASK-001
...
```

### Task Sizing Rules

| Duration | Action |
|----------|--------|
| < 2 min | Merge with adjacent task |
| 2-5 min | Ideal — keep as is |
| 5-10 min | Acceptable for complex logic |
| > 15 min | Split into subtasks |

A task that touches more than 3 files is probably too large. Split it.

### Parallelism Annotation

Mark tasks that can run in parallel:

```markdown
## TASK-003 [parallel: TASK-004]
```

Tasks annotated with `parallel` can be dispatched simultaneously via `dispatching-parallel-agents`.
Tasks without parallel annotation run sequentially via `subagent-driven-development`.

---

## After Generation

1. Show task list summary to user (task IDs, descriptions, total count)
2. Get user approval: "Proceed with these [N] tasks? [Y/n]"
3. On approval: invoke `subagent-driven-development` or `sop-code-assist` per task

---

## Integration

```
sop-discovery → [sop-planning] → sop-code-assist (per task)
                              → subagent-driven-development (orchestrated)
```
