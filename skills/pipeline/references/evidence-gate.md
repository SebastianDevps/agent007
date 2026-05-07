# Evidence Gate — Reference

Detailed pre-PR gates and verdict templates for `verify.md`.

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

## Verdict Templates

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

### FAIL 3/3

```
❌ Verify FAIL — 3/3 intentos agotados

No se pudo hacer pasar: <lista de tests fallando>
Escalando a humano. Contexto en: .sdlc/handoffs/<workflow-id>/<task-id>-handoff.md

<promise>FAIL</promise>
```

---

## Suite de Verificación — Fallback Standards

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

## Evidencia Mínima Requerida

- Número exacto de tests: `X passed, Y failed, Z total`
- Build status: `compiled successfully` o `N error(s)`
- Lint status: `0 problems` o lista de errores
- Si es e2e: screenshot path o response body

**Nunca resumir el output** — mostrar la línea de resultado exacta.
