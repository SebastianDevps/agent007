---
name: ralph-loop
description: "Activates the Ralph Loop — autonomous iteration until the completion promise is detected. Can be invoked manually or auto-routed by the orchestrator."
accepts_args: true
version: 1.0
---

# /ralph-loop — Ralph Loop

**Arguments**: `$ARGUMENTS`

---

## Step 1 — Parse Arguments

From `$ARGUMENTS` extract:

| Field | Source | Default |
|-------|--------|---------|
| **task** | Quoted string at the start | Required |
| **requirements** | Lines after `Requisitos:` or `Requirements:` | [] |
| **successCriteria** | Lines after `Criterios de éxito:` or `Success Criteria:` | [] |
| **completionPromise** | `--completion-promise "TEXT"` | `"COMPLETE"` |
| **maxIterations** | `--max-iterations N` | `20` (max: 50) |
| **verificationCommand** | `--verify "command"` | `null` |

---

## Step 2 — Safety Check

If the task mentions: `auth`, `payment`, `migration`, `encryption`, `.env`, `secret` → stop and ask:
```
⚠️ Ralph Loop + sensitive domain detected.
This task touches [auth/payment/migration]. Ralph loops modify code autonomously.
Are you sure you want to proceed? [yes/no]
```
Only continue if user confirms.

---

## Step 3 — Initialize Ralph State

**3a.** Generate a unique loopId: use `crypto.randomUUID()` via a Bash call or timestamp-based ID.

**3b.** Write `.claude/ralph-state.json`:

```json
{
  "active": true,
  "loopId": "<uuid>",
  "task": "<parsed task>",
  "completionPromise": "<parsed or default>",
  "maxIterations": <N>,
  "currentIteration": 0,
  "startTime": "<current ISO timestamp>",
  "requirements": ["<req1>", "<req2>"],
  "successCriteria": ["<criterion1>", "<criterion2>"],
  "verificationCommand": "<command or null>"
}
```

**3c.** Delete `.claude/ralph-complete.txt` if it exists:
```bash
rm -f .claude/ralph-complete.txt
```

---

## Step 4 — Show Banner

Output this banner exactly:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 RALPH LOOP ACTIVATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task:        <task>
Iterations:  0 / <maxIterations>
Completion:  <promise><completionPromise></promise>
Verify:      <verificationCommand or "none">
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Step 5 — Route by Complexity

Before executing, classify the task:

| Condition | Mode |
|-----------|------|
| ≥ 3 requirements **OR** multiple technologies/frameworks mentioned | **ORCHESTRATED** |
| < 3 requirements, single technology, single file scope | **DIRECT** |

---

### DIRECT Mode

Implement the task immediately:
1. Read relevant files (Glob + Grep before editing)
2. Implement following all requirements
3. Run verificationCommand if set (after each significant change)
4. Show actual output — no claims without evidence
5. Output `<promise>COMPLETE</promise>` + write signal file when ALL success criteria confirmed

---

### ORCHESTRATED Mode

For complex tasks, apply the full superpowers pipeline **within the ralph loop**:

> Note: Skip brainstorming — the requirements block already provides the spec.
> Note: Skip interactive finishing — commit to worktree branch and report status.

**5a — Worktree** (skill: `using-git-worktrees`):
- Create isolated branch: `feat/<task-slug>` in `.worktrees/`
- Skip baseline tests if no test suite exists

**5b — Plan** (skill: `writing-plans`):
- Use the parsed `requirements` and `successCriteria` as the spec
- Decompose into 2-5 min tasks with exact file paths + complete code
- Save to `docs/plans/YYYY-MM-DD-<task-slug>.md`

**5c — Subagent Execution** (skill: `subagent-driven-development`):
- Dispatch expert subagent per task (auto-routed by domain)
- Each task: implement → spec review → quality review → commit
- No task advances without both reviews passing

**5d — Final Verification**:
- Run `verificationCommand` if set, OR `npm run build && npm run lint` as fallback
- Confirm all `successCriteria` are met
- Report the worktree branch name so user can review/merge

**CRITICAL — When ALL pipeline steps complete and all criteria verified:**
1. Output `<promise>COMPLETE</promise>` in your response
2. Run this exact command:
   ```bash
   echo "COMPLETE" > .claude/ralph-complete.txt
   ```

---

### Both Modes — Continuation Signal

If the Stop hook blocks and injects a new iteration: re-assess what's missing from `successCriteria` and continue from where you left off. Do NOT restart from scratch.

---

## Auto-Activation Signals

This command is auto-routed by the orchestrator when the user's message contains:

| Signal | Examples |
|--------|---------|
| Loop keywords | "loop until", "ralph", "--persist", "iterate until done" |
| Autonomous intent | "run overnight", "autonomous", "until tests pass" |
| Explicit | "use ralph", "ralph loop", "loop mode" |

---

## Examples

**ORCHESTRATED — Full format (≥ 3 requirements → pipeline completo):**
```
/ralph-loop "Implementar herramienta de gestión de proyectos"

Requisitos:
- Aplicación completa en Next.js + Tailwind con localStorage
- Tablero Kanban funcional (columnas: Todo / In Progress / Done)
- Lista de tareas integrada con CRUD completo
- Sin errores de linter

Criterios de éxito:
- Todos los requisitos implementados
- Sin errores de linter
- Documentación actualizada

Output <promise>COMPLETE</promise> al finalizar. --max-iterations 30 --completion-promise "COMPLETE"
```
→ Modo activado: **ORCHESTRATED** (4 requisitos detectados)
→ Pipeline interno: worktree → writing-plans → subagents → verify → COMPLETE

---

**DIRECT — Compact (< 3 requisitos → implementación directa):**
```
/ralph-loop "Fix all failing tests" --max-iterations 10 --completion-promise "COMPLETE"
```
→ Modo activado: **DIRECT**

---

**Auto-activated** (orchestrator detecta intención):
```
User: "Implement the kanban board and loop until all tests pass"
→ 🎯 ralph → /ralph-loop (ORCHESTRATED)
```

---

## Relación con /dev

```
/ralph-loop "task"    ←→    /dev "task" --ralph

Ambos activan ralph. La diferencia:
- /ralph-loop: punto de entrada explícito (comando directo)
- /dev --ralph: orquestador maestro que activa ralph internamente por tarea

Para tareas complejas, ambos convergen al mismo pipeline:
  worktree → plan → subagents (con ralph por tarea) → verify → COMPLETE
```
