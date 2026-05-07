---
name: verify
description: "Verification gate: runs tests, build, and lint then validates output against acceptance criteria. Must pass before any 'done' claim. Use after generate or at end of any task. Returns PASS with evidence or FAIL with diagnosis."
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(npm test*)
  - Bash(npm run*)
  - Bash(pnpm test*)
  - Bash(pnpm run*)
  - Bash(yarn test*)
  - Bash(pytest*)
  - Bash(go test*)
  - Bash(cargo test*)
  - Bash(jest*)
  - Bash(vitest*)
  - Bash(tsc*)
  - Bash(eslint*)
  - Bash(git status*)
  - Bash(git diff*)
invokable: true
accepts_args: true
version: 1.0.0
when:
  - task_type: [feature, bug, refactor]
    risk_level: [low, medium, high, critical]
  - after: generate
  - pipeline: [simple, medium, complex]
references:
  - references/evidence-gate.md
  - references/sdd-review.md
---

# Verify — Evidence-Based Verification Gate

**Propósito**: Gate de verificación que impide reclamar "done" sin evidencia real. Ejecuta la suite de verificación y valida contra los acceptance criteria del plan.

**Cuándo activar**:
- Después de cada `Skill('generate')` — siempre, sin excepción
- Al final del pipeline antes de `finishing-a-development-branch`
- Cuando alguien afirma que algo "está listo" — verificar antes de aceptar

**Banned phrase enforcement**: si el output contiene "should work", "probably", "likely" → FAIL automático. El código o pasa los tests o no pasa.

---

## 6-Gate Pre-PR Checklist (resumen)

Todos los gates deben pasar antes de declarar listo:

```
Gate 1: BUILD     Gate 4: TESTS (≥80% coverage)
Gate 2: TYPES     Gate 5: SECURITY
Gate 3: LINT      Gate 6: DIFF review
```

Detalle completo (criterios por gate, plantillas) → `references/evidence-gate.md`.

Un gate bloqueado = FAIL. No avanzar hasta resolver.

---

## Phase 1 — Determinar Suite de Verificación

Leer en orden de prioridad:

1. `verify_cmd` de la tarea actual en `tasks.md` → usar este
2. Scripts disponibles en `package.json` → inferir el correcto
3. Fallback estándar (TypeScript / Python / sin framework) → `references/evidence-gate.md`

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

Para cada criterio en `acceptance_criteria` de la tarea, mapear test → evidencia.
Si un criterio no tiene test que lo cubra → FLAG como gap (documentar, no FAIL automático).
Plantilla detallada → `references/sdd-review.md`.

---

## Phase 4 — Emitir Veredicto

### PASS — resumen

```
✅ Verify PASS — TASK-NNN: <title>
Evidence: [npm test] → 42 passed, 0 failed | [build] → ok | [lint] → 0 problems
Acceptance: ✅ <criterio> cubierto por <test>
Ready for: [next task | code-reviewer | finishing-a-development-branch]
```

### FAIL — resumen

```
❌ Verify FAIL — TASK-NNN [Intento X/3]
Evidence: [npm test] → 38 passed, 4 FAILED — output literal
Root cause: <file:line:function — qué falló>
Fix required: <acción concreta>
→ Retornando a Skill('generate') con feedback [intento X/3]
```

### FAIL 3/3 → escalar a humano con mini-handoff

Plantillas completas (PASS, FAIL, FAIL 3/3) → `references/evidence-gate.md`.

---

## Phase 5 — Mini-Handoff (si viene de subagent-driven-development)

Escribir `.sdlc/handoffs/<workflow-id>/<task-id>-handoff.md` con `task_id`, `status`, `files_modified`, `evidence`, `notes`.

Formato exacto → `references/sdd-review.md`.

---

## Reflection Retry Protocol (patrón Aider)

El error no dispara un retry genérico — **el output literal se convierte en input** al siguiente intento. Hasta 3 intentos con escalación creciente:

- Intento 1 FAIL → standard reflection (output literal + root cause + fix concreto)
- Intento 2 FAIL → cambiar enfoque (previous approach failed because…)
- Intento 3 FAIL → ESCALAR A HUMANO — no reintentar

Detalle completo (mensajes textuales por attempt) → `references/sdd-review.md`.

---

## Anti-patterns (NEVER)

- ❌ Afirmar PASS sin ejecutar el comando y mostrar output real
- ❌ Aceptar "debería funcionar" / "probably" / "should work" como evidencia (FAIL automático)
- ❌ PASS con tests skip/pending no justificados
- ❌ Ignorar errores de TypeScript (`tsc --noEmit` debe pasar)
- ❌ Loop más de 3 veces fixing linter errors en el mismo archivo (linter loop guard) — escalar al usuario
- ❌ Resumir el output del comando — usar la línea exacta

## Required (ALWAYS)

- ✅ El output del comando es la única fuente de verdad
- ✅ Si el verify_cmd no existe en el proyecto → reportar y pedir al usuario que lo defina
- ✅ Mostrar evidencia citable: `[cmd] → [output literal]`

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
