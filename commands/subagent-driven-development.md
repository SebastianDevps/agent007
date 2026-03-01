---
name: subagent-driven-development
version: 1.0
description: "Executes an implementation plan by dispatching a fresh expert subagent per task with two-stage review (spec compliance → code quality). Use after /writing-plans."
accepts_args: true
---

# /subagent-driven-development — Plan Execution Engine

**Input**: Written plan at `docs/plans/YYYY-MM-DD-<feature>.md`
**When**: After `/writing-plans`, all tasks clearly defined.

---

## Setup

1. Read the plan file — extract all tasks with full text
2. Create one TaskCreate entry per task
3. Show task list to user before starting

---

## Per-Task Loop

```
TaskUpdate → in_progress
     ↓
Agent tool: Implementer Subagent
  - Select expert by domain (see routing table below)
  - Pass: full task text + file context (NOT the plan file path — give text directly)
  - Apply TDD: failing test → implement → passing test
     ↓
Spec Compliance Review (inline or Agent tool: same expert)
  - "Does this code match the task spec exactly?"
  - If issues → same implementer fixes → re-review
  - Block until PASS
     ↓
Code Quality Review (inline)
  - No `any` types | No N+1 queries | No hardcoded secrets | Tests cover edge cases
  - If issues → same implementer fixes → re-review
  - Block until PASS
     ↓
TaskUpdate → completed
```

---

## Expert Routing

| Domain signals | Agent |
|---------------|-------|
| API, DB, NestJS, SQL, TypeORM | backend-db-expert |
| React, Next.js, UI, components | frontend-ux-expert |
| Tests, CI/CD, scripts, infra, Node.js | platform-expert |
| Auth, permissions, encryption | security-expert |
| Mixed / unclear | platform-expert |

---

## Ralph Integration

When `--ralph` is active, wrap each task:
- Write `.claude/ralph-state.json` with task as the goal
- Task is complete when verification command passes
- Claude must output `echo "COMPLETE" > .claude/ralph-complete.txt` when done

---

## Guardrails (NEVER violate)

- ❌ No parallel implementers — one task at a time
- ❌ No skipping reviews — both stages required
- ❌ No passing plan as file — give task text directly to subagent
- ✅ If subagent asks questions → answer completely before it proceeds

**Next step**: `/finishing-a-development-branch`
