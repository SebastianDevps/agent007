---
name: session-manager
description: "Auto-injected routing and state protocol. Handles classification → routing, session start/end state read/write. Not directly invokable — activated by CLAUDE.md session protocol."
invokable: false
auto_inject: true
version: 1.0.0
---

# Session Manager — Routing & State Protocol

**Mode**: Auto-injected. Do not invoke directly.

This skill codifies the session orchestration logic defined in CLAUDE.md:

## Classification → Routing

Every user message is classified and routed per the table in CLAUDE.md:

```
consult   → /consult
feature   → /dev (complexity check)
bug       → systematic-debugging → SDD
refactor  → Skill('reverse-engineer') → Skill('plan')
review    → code-reviewer
research  → deep-research
product   → /consult → product-expert
design    → /consult → frontend-ux-expert
ralph     → loop-operator → /ralph-loop
cleanup   → refactor-cleaner
unknown   → ask user
```

Always show routing decision: `🎯 [TYPE] → [ROUTE] | Risk: [low|medium|high|critical]`

## State Read/Write Protocol

### On session start
1. Read `.sdlc/state/session.md`
2. If "Tarea Activa" ≠ "ninguna" → show resume banner
3. If file missing → create it silently

### After every task completion
Silently update `.sdlc/state/session.md`:
- Branch: current branch
- Tarea Activa: next task or "ninguna"
- Tareas Completadas: prepend with timestamp
- Decisiones Tomadas: significant design decisions

### On session end
Write 2–3 bullets to Resumen in `.sdlc/state/session.md`. No output to user.

## Risk Escalation

`auth / payment / encryption / migration / breaking-change` → always high or critical.
High/critical → require explicit human approval before proceeding.
