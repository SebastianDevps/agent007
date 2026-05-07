# SDD Review — Reference

Reflection retry protocol and mini-handoff format used by `verify.md`.

## Mini-Handoff (cuando viene de subagent-driven-development)

Si el workflow_id está disponible, escribir:
`.sdlc/handoffs/<workflow-id>/<task-id>-handoff.md`

```markdown
## Mini-Handoff
task_id: TASK-NNN
status: COMPLETE | FAIL
files_modified:
  - src/path/to/file.ts
evidence: "[npm test] → 42 passed, 0 failed"
notes: [cualquier decisión de implementación no obvia]
```

---

## Reflection Retry Protocol (patrón Aider)

El error no dispara un "retry genérico" — **el output literal del error se convierte en el siguiente input** al implementador. El modelo se corrige con contexto real.

### Attempt 1 FAIL

```
reflected_message = "[npm test output literal]\n\nRoot cause: <diagnosis>\nFix required: <acción concreta>"
→ pasar reflected_message como input a Skill('generate') intento 2
```

### Attempt 2 FAIL

```
reflected_message = "[nuevo output literal]\n\nPrevious approach failed because: <razón>\nTry instead: <enfoque alternativo>"
→ pasar reflected_message como input a Skill('generate') intento 3
```

### Attempt 3 FAIL → ESCALAR A HUMANO — no reintentar

---

## Regla Clave

El `reflected_message` siempre incluye:
1. Output del comando literal (líneas de error, no resumen)
2. Root cause diagnosticado (línea exacta, función, archivo)
3. Fix sugerido concreto (o enfoque alternativo si ya se intentó)

Si el mismo error se repite 2 veces seguidas → el fix no está funcionando, cambiar enfoque completamente antes del intento 3.

---

## Acceptance Criteria — Validación

Para cada criterio en el bloque `acceptance_criteria` de la tarea:

```
Criterio: "Returns 404 when user does not exist"
Evidencia: test "should return 404 when user does not exist" → PASSED ✅

Criterio: "Response includes error message"
Evidencia: test "should include error field in 404 response" → PASSED ✅
```

Si un criterio no tiene test que lo cubra → FLAG como gap (no FAIL automático, pero documentar).
