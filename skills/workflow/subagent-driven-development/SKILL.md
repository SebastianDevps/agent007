---
name: subagent-driven-development
description: "Executes implementation plans by dispatching a fresh expert subagent per task with two-stage review (spec compliance → code quality). Use when executing a written plan autonomously."
invokable: true
accepts_args: true
version: 1.0
source: superpowers (obra/superpowers) — adapted for Agent007
---

# Subagent-Driven Development

**Propósito**: Ejecutar un plan de implementación despachando un subagente experto fresco por tarea, con doble review automático antes de avanzar.

**Cuándo activar**: Después de `/writing-plans`. El plan existe, hay tareas independientes, todo corre en la sesión actual.

---

## Flujo de Ejecución

### Setup
1. Leer el plan de `docs/plans/YYYY-MM-DD-<feature>.md`
2. Extraer todas las tareas con texto completo + contexto
3. Crear lista de seguimiento (TaskCreate por tarea)

### Por Cada Tarea

```
TaskUpdate → in_progress
     ↓
Dispatch: Implementer Subagent
  - Agente experto según dominio (backend/frontend/platform/security)
  - Recibe: texto completo de la tarea + contexto del plan
  - Aplica TDD: test failing → implementar → test passing
  - Commit al terminar
     ↓
Dispatch: Spec Compliance Reviewer
  - Pregunta: "¿El código cumple exactamente la especificación?"
  - Si hay issues: mismo implementer los corrige → mismo reviewer re-valida
  - No avanzar hasta: spec OK
     ↓
Dispatch: Code Quality Reviewer
  - Pregunta: "¿El código sigue los estándares? (no any, no N+1, no hardcoded secrets)"
  - Si hay issues: mismo implementer los corrige → mismo reviewer re-valida
  - No avanzar hasta: quality OK
     ↓
TaskUpdate → completed
```

### Finalización
- Después de todas las tareas → dispatch final code review
- → `/finishing-a-development-branch`

---

## Guardrails Críticos (NUNCA violar)

- ❌ No despachar múltiples implementers en paralelo
- ❌ No avanzar sin que ambos reviews estén OK
- ❌ No pasar el plan como archivo — dar el texto directamente al subagente
- ❌ No empezar quality review antes de que spec review esté limpio
- ✅ Si el subagente hace preguntas: responder COMPLETAMENTE antes de que proceda
- ✅ Si un reviewer encuentra issues: el mismo implementer los corrige (continuidad)

---

## Agente a Usar por Dominio

| Dominio detectado | Agente |
|-------------------|--------|
| API, DB, NestJS, backend | backend-db-expert |
| React, Next.js, UI/UX | frontend-ux-expert |
| CI/CD, tests, infra | platform-expert |
| Auth, permisos, seguridad | security-expert |
| Mixed / general | platform-expert |

---

## Integración con Ralph

Cuando `--ralph` está activo (o auto-detectado), cada tarea se ejecuta dentro de un ralph loop:
- El implementer subagent trabaja hasta output `<promise>COMPLETE</promise>`
- El Stop hook ralph-check intercepta si la tarea no está completa
- Luego pasa a los reviewers normalmente

---

## Prerrequisitos

- `using-git-worktrees` (rama aislada activa)
- `writing-plans` (plan guardado en docs/plans/)
- `requesting-code-review` (templates de review disponibles)
