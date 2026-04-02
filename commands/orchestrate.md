---
name: orchestrate
description: "Multi-agent workflow orchestration with named workflow types and structured HANDOFF documents between agents."
invokable: true
accepts_args: true
version: 1.0
source: Agent007 v5.1 — GAP-005 (ECC multi-agent patterns)
---

# /orchestrate — Multi-Agent Workflow Orchestration

**Propósito**: Ejecuta workflows nombrados donde cada agente pasa un documento HANDOFF estructurado al siguiente. Garantiza trazabilidad completa de decisiones y hallazgos entre agentes.

**Invocación**: `/orchestrate <workflow-type> "<task description>"`

---

## Workflow Types

### `feature` — New Feature Development
```
brainstorm → plan → [wave execute: SDD] → code-reviewer → security-expert → branch-finish
```
Use for: implementing new capabilities with full quality gate chain.

### `bugfix` — Bug Investigation and Fix
```
systematic-debugging → plan → generate → code-reviewer → verify
```
Use for: fixing reported bugs with root cause analysis first.

### `refactor` — Safe Refactoring
```
sop-reverse → plan → [wave execute: SDD] → code-reviewer → verify
```
Use for: restructuring code without behavior change.

### `security` — Security Review and Remediation
```
security-expert → code-reviewer → [fix: SDD] → security-expert (re-verify)
```
Use for: security audits, vulnerability remediation, compliance checks.

### `cleanup` — Dead Code and Dependency Cleanup
```
refactor-cleaner → verify
```
Use for: removing unused code, cleaning dependencies.

---

## HANDOFF Document Protocol

Every agent in the chain **must produce** a HANDOFF.md at `.sdlc/handoffs/<workflow-id>/<agent-name>-handoff.md` upon completion before the next agent starts.

### HANDOFF Document Format

```markdown
## Handoff: [agent-name] → [next-agent-name]
**Workflow**: [workflow-type]
**Task**: [task description]
**Date**: YYYY-MM-DD
**Status**: COMPLETE | PARTIAL | BLOCKED

### Context
[What was done and why — 2-5 sentences explaining the decisions made]

### Findings
- [Key finding 1]
- [Key finding 2]
- [Any unexpected discoveries that affect next agent's work]

### Files Modified
- `path/to/file.ts` — [what changed and why]
- `path/to/other.ts` — [what changed and why]

### Open Questions
- [Question the next agent should resolve]
- [Ambiguity that was deferred]

### Recommendations for [next-agent-name]
- [Specific guidance for the next agent based on findings]
- [Files to focus on first]
- [Known risks to verify]
```

### Mini-Handoff (for subagent-driven-development tasks)

When SDD runs multiple subagents in parallel, each subagent produces a mini-handoff:

```markdown
## Mini-Handoff: [task-id] → [next-task-id-or-review]
**Agent**: [type]
**Status**: COMPLETE | FAIL
**Files**: [list]
**Notes**: [1-2 sentences on key decisions or surprises]
```

---

## Final Orchestration Report

After ALL agents in the chain complete, produce:

```markdown
## Orchestration Report
**Workflow**: [type]
**Task**: [description]
**Date**: YYYY-MM-DD
**Duration**: Xm
**Agents**: [chain: agent1 → agent2 → agent3]

### Verdict
SHIP / NEEDS WORK / BLOCKED

### Summary
[2-3 sentences on what was accomplished and current state]

### Handoff Chain
| Agent | Status | Key Finding |
|-------|--------|-------------|
| brainstorm | ✅ COMPLETE | Identified 3 design options, chose X because Y |
| plan | ✅ COMPLETE | 8 tasks across 3 waves |
| sdd-wave-1 | ✅ COMPLETE | 3 tasks, all passing |
| code-reviewer | ⚠️ NEEDS WORK | 1 HIGH finding at auth.service.ts:47 |

### Open Items (if verdict ≠ SHIP)
- [Blocking item 1]
- [Blocking item 2]
```

---

## Orchestration Protocol

### Step 1 — Initialize

```bash
mkdir -p .sdlc/handoffs/<workflow-id>
# workflow-id = <type>-<YYYYMMDD>-<short-desc>, e.g. feature-20260329-user-auth
```

### Step 2 — Execute Chain

For each agent in the workflow:
1. Read previous agent's HANDOFF (if any) before starting
2. Execute agent's task
3. Produce HANDOFF document at specified path
4. Verify HANDOFF exists before signaling next agent

### Step 3 — Human Gates

Insert human approval checkpoint BEFORE:
- Any merge to main/develop
- Any security-expert remediation that modifies auth/encryption
- Any SDD execution if risk is HIGH or CRITICAL

### Step 4 — Cleanup

After workflow completion (SHIP verdict):
```bash
rm -rf .sdlc/handoffs/<workflow-id>  # or archive: mv to .sdlc/handoffs/archive/
```

---

## Guardrails

- ❌ Never skip the HANDOFF step — it IS the coordination mechanism
- ❌ Never start agent N+1 before agent N produces its HANDOFF
- ❌ Never produce a SHIP verdict if any agent has BLOCKED status
- ✅ HANDOFF documents are the audit trail — preserve them until SHIP
- ✅ Open Questions in HANDOFF must be resolved before chain continues
