---
name: verify
description: "Verification gate: runs tests, build, and lint then validates output against acceptance criteria. Must pass before any 'done' claim. Use after generate or at end of any task. Returns PASS with evidence or FAIL with diagnosis."
invokable: true
accepts_args: true
version: 1.0.0
when:
  - task_type: [feature, bug, refactor]
    risk_level: [low, medium, high, critical]
  - after: generate
  - pipeline: [simple, medium, complex]
---

# Verify — Evidence-Based Verification Gate

**Propósito**: Gate de verificación que impide reclamar "done" sin evidencia real. Ejecuta la suite de verificación y valida contra los acceptance criteria del plan.

**Cuándo activar**:
- Después de cada `Skill('generate')` — siempre, sin excepción
- Al final del pipeline antes de `finishing-a-development-branch`
- Cuando alguien afirma que algo "está listo" — verificar antes de aceptar

**Banned phrase enforcement**: si el output contiene "should work", "probably", "likely" → FAIL automático. El código o pasa los tests o no pasa.

---

## 6-Gate Pre-PR Checklist

Antes de reclamar que un cambio está listo, todos los gates deben pasar:

```
Gate 1: BUILD     → npm run build / tsc --noEmit → 0 errors
Gate 2: TYPES     → TypeScript strict, 0 type errors
Gate 3: LINT      → eslint/prettier → 0 errors (warnings documentados)
Gate 4: TESTS     → suite completa → ≥80% coverage, 0 failed
Gate 5: SECURITY  → no secrets en diff, no console.log, no vulnerabilidades OWASP obvias
Gate 6: DIFF      → revisar diff completo buscando cambios no intencionales o missing error handling
```

**Cadencia recomendada**: ejecutar los 6 gates al final de cada tarea completada, no solo al final del feature completo.

Un gate bloqueado = FAIL. No avanzar hasta resolver.

---

## Phase 1 — Determinar Suite de Verificación

Leer en orden de prioridad:

1. `verify_cmd` de la tarea actual en `tasks.md` → usar este
2. Scripts disponibles en `package.json` → inferir el correcto
3. Fallback estándar:

```bash
# TypeScript / Node.js
npm run build && npm test && npm run lint

# Si hay test específico de la tarea
npm test -- --testPathPattern="<archivo-relevante>"

# Python
python -m pytest tests/ -v

# Sin framework de tests
node <archivo> && echo "EXIT: $?"
```

---

## Phase 2 — Ejecutar y Capturar Evidencia

Ejecutar el comando completo y capturar output **literal**:

```bash
<verify_cmd>
```

**Requerimientos de evidencia mínima**:
- Número exacto de tests: `X passed, Y failed, Z total`
- Build status: `compiled successfully` o `N error(s)`
- Lint status: `0 problems` o lista de errores
- Si es e2e: screenshot path o response body

**Nunca resumir el output** — mostrar la línea de resultado exacta.

---

## Phase 3 — Validar Acceptance Criteria

Para cada criterio en el bloque `acceptance_criteria` de la tarea:

```
Criterio: "Returns 404 when user does not exist"
Evidencia: test "should return 404 when user does not exist" → PASSED ✅

Criterio: "Response includes error message"
Evidencia: test "should include error field in 404 response" → PASSED ✅
```

Si un criterio no tiene test que lo cubra → FLAG como gap (no FAIL automático, pero documentar).

---

## Phase 4 — Emitir Veredicto

### PASS

```
✅ Verify PASS — TASK-NNN: <title>

Evidence:
  [npm test] → 42 passed, 0 failed (2.3s)
  [npm run build] → Compiled successfully
  [npm run lint] → 0 problems

Acceptance Criteria:
  ✅ <criterio 1> → cubierto por test "<nombre del test>"
  ✅ <criterio 2> → cubierto por test "<nombre del test>"

Ready for: [next task | code-reviewer | finishing-a-development-branch]
```

### FAIL

```
❌ Verify FAIL — TASK-NNN: <title>  [Intento X/3]

Evidence:
  [npm test] → 38 passed, 4 FAILED (3.1s)
  
  FAILED: UserService > findById > should return null when not found
    Expected: null
    Received: undefined
    at src/users/user.service.spec.ts:47

Root cause: [diagnosis directo — qué línea, qué función, qué falló]
Fix required: [acción concreta para resolver]

→ Retornando a Skill('generate') con este feedback [intento X/3]
```

Si 3 intentos fallaron:
```
❌ Verify FAIL — 3/3 intentos agotados

No se pudo hacer pasar: <lista de tests fallando>
Escalando a humano. Contexto en: .sdlc/handoffs/<workflow-id>/<task-id>-handoff.md

<promise>FAIL</promise>
```

---

## Phase 5 — Generar Mini-Handoff (si viene de subagent-driven-development)

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

## Guardrails

- ❌ NUNCA afirmar PASS sin ejecutar el comando y mostrar output real
- ❌ NUNCA aceptar "debería funcionar" como evidencia
- ❌ No hacer PASS si hay tests en skip/pending no justificados
- ❌ No ignorar errores de TypeScript (`tsc --noEmit` debe pasar)
- ❌ **Linter loop guard**: Do NOT loop more than 3 times fixing linter errors on the same file. On the third attempt, stop and escalate to the user — do not keep iterating.
- ✅ El output del comando es la única fuente de verdad
- ✅ Si el verify_cmd no existe en el proyecto → reportar y pedir al usuario que lo defina

---

## Reflection Retry Protocol (patrón Aider)

El error no dispara un "retry genérico" — **el output literal del error se convierte en el siguiente input** al implementador. El modelo se corrige con contexto real.

```
Intento 1 FAIL:
  reflected_message = "[npm test output literal]\n\nRoot cause: <diagnosis>\nFix required: <acción concreta>"
  → pasar reflected_message como input a Skill('generate') intento 2

Intento 2 FAIL:
  reflected_message = "[nuevo output literal]\n\nPrevious approach failed because: <razón>\nTry instead: <enfoque alternativo>"
  → pasar reflected_message como input a Skill('generate') intento 3

Intento 3 FAIL → ESCALAR A HUMANO — no reintentar
```

**Regla clave**: el `reflected_message` siempre incluye:
1. Output del comando literal (líneas de error, no resumen)
2. Root cause diagnosticado (línea exacta, función, archivo)
3. Fix sugerido concreto (o enfoque alternativo si ya se intentó)

Si el mismo error se repite 2 veces seguidas → el fix no está funcionando, cambiar enfoque completamente antes del intento 3.

---

## Integración

```
generate → verify
  ├── PASS → siguiente tarea (en subagent-driven-development)
  │         → code-reviewer (si risk medium+)
  │         → finishing-a-development-branch (si última tarea)
  └── FAIL (x3) → escalar a humano con mini-handoff

pipeline simple: generate → verify → done (si PASS)
```

**Skill previo**: `Skill('generate')`
**Siguiente skill**: próxima tarea, `code-reviewer`, o `finishing-a-development-branch`
