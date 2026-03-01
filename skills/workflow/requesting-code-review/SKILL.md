---
name: requesting-code-review
description: "Dispatches code review subagent after each task in subagent-driven-development. Two-stage: spec compliance first, then code quality. Use after each task implementation."
invokable: true
accepts_args: true
version: 1.0
source: superpowers (obra/superpowers) — adapted for Agent007
---

# Requesting Code Review

**Propósito**: Review automatizado de cada tarea implementada. Dos etapas en secuencia estricta: spec compliance primero, code quality después.

**Filosofía**: "Review early, review often." Un issue detectado en tarea 2 es infinitamente más barato que detectarlo en tarea 8.

---

## Stage 1 — Spec Compliance Review

**Pregunta central**: ¿El código implementado cumple EXACTAMENTE la especificación de la tarea?

**Dispatch al agente correcto** (mismo que implementó):

```
Agente: [mismo experto que implementó la tarea]

Contexto a proporcionar:
- Texto completo de la tarea del plan
- git diff desde el base commit: `git diff <base-sha> HEAD`
- Acceptance criteria de la tarea

Instrucción:
"Review if the implementation matches the spec exactly.
Report: COMPLIANT or issues by severity (critical/important/minor)."
```

**Resultados**:
- `COMPLIANT` → pasar a Stage 2
- Issues encontrados → mismo implementer los corrige → mismo reviewer re-valida
- ❌ NUNCA pasar a Stage 2 con issues críticos o importantes pendientes

---

## Stage 2 — Code Quality Review

**Pregunta central**: ¿El código sigue los estándares de calidad?

**Checklist automático**:

```
□ No `any` types (TypeScript)
□ No N+1 queries (TypeORM: usar relations[] o QueryBuilder)
□ No hardcoded secrets o magic strings
□ No TODOs/FIXMEs dejados en el código nuevo
□ Error handling apropiado en boundaries
□ Tests cubren happy path + al menos 2 edge cases
□ No linting errors
□ Funciones < 50 líneas (complejidad manejable)
```

**Severity**:
| Nivel | Acción |
|-------|--------|
| Critical | Bloquea — implementer corrige, reviewer re-valida |
| Important | Bloquea — implementer corrige, reviewer re-valida |
| Minor | Documenta — puede deferirse si el usuario aprueba |

---

## Obtener SHAs

```bash
# Base SHA (antes de empezar la tarea)
git log --oneline -1 HEAD~1 --format="%H"

# Head SHA (después de implementar)
git log --oneline -1 HEAD --format="%H"

# Diff completo
git diff <base-sha> <head-sha>
```

---

## Output esperado del review

```
## Code Review — Task: [nombre de tarea]

### Stage 1: Spec Compliance
Status: COMPLIANT | ISSUES FOUND
Issues:
- [critical] Description
- [important] Description

### Stage 2: Code Quality
Status: APPROVED | ISSUES FOUND
Issues:
- [critical] Description
- [minor] Description (deferred)

### Verdict: APPROVED | NEEDS FIXES
```

---

## Integración

- **Llamado por**: `subagent-driven-development` (después de cada tarea)
- **Prerrequisito**: La tarea fue implementada y commiteada
- **Después de aprobación**: marcar tarea como completed, avanzar a la siguiente
