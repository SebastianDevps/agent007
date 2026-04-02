---
name: generate
description: "TDD code generation cycle: RED (failing test) → GREEN (minimal code) → REFACTOR. Executes one task at a time from tasks.md. Use when implementing a single planned task or a simple change with no prior plan."
invokable: true
accepts_args: true
version: 1.0.0
when:
  - task_type: [feature, bug, refactor]
    risk_level: [low, medium, high, critical]
  - after: plan
  - pipeline: [simple, medium, complex]
---

# Generate — TDD Code Generation

**Propósito**: Implementar una tarea concreta siguiendo el ciclo RED → GREEN → REFACTOR. Nunca escribe código de producción sin antes tener un test fallando.

**Cuándo activar**:
- Pipeline simple: directamente después de recibir la tarea
- Pipeline medium/complex: llamado por `subagent-driven-development` por tarea
- Bug fix: después de reproducir el bug con `systematic-debugging`

**Input esperado** (uno de los dos):
- ID de tarea + ruta a `tasks.md` (cuando viene de un plan)
- Descripción directa de la tarea (pipeline simple)

---

## Phase 0 — Leer Contexto de la Tarea

Si viene de `tasks.md`:
```
1. Leer el bloque TASK-NNN completo
2. Leer los archivos listados en `files` (Read tool)
3. Leer test existentes relacionados para entender patrones
4. NO leer archivos no relacionados con esta tarea
```

Si viene directo (pipeline simple):
```
1. Glob para encontrar archivos relevantes
2. Leer archivos que se van a modificar
3. Leer tests existentes para seguir el mismo patrón
```

---

## Phase 1 — RED: Escribir Test Fallando

**Iron Law**: el test DEBE fallar antes de escribir código de producción.

```typescript
// ✅ Correcto — test describe comportamiento observable
it('should return 404 when user does not exist', async () => {
  const response = await request(app).get('/users/non-existent-id');
  expect(response.status).toBe(404);
  expect(response.body).toMatchObject({ error: 'User not found' });
});

// ❌ Incorrecto — test de implementación, no comportamiento
it('should call userRepository.findById', () => { ... });
```

Ejecutar y verificar que FALLA:
```bash
<verify_cmd>
# Salida esperada: FAIL — X test(s) failed
```

Si el test ya pasa antes de implementar → el test no prueba nada nuevo. Revisar.

---

## Phase 2 — GREEN: Implementar Mínimo Necesario

**Regla**: escribir el código más simple que hace pasar el test. Nada más.

Aplicar obligatoriamente:
- **Coding style**: ver `@.claude/rules/coding-style.md`
  - Named exports only (no default exports)
  - Explicit return types en funciones públicas
  - No magic numbers — constantes nombradas
  - Max 20 líneas por función, max 200 líneas por archivo
- **Patterns**: ver `@.claude/rules/patterns.md`
  - Guard clauses sobre nested if/else
  - Repository pattern para acceso a datos
  - DTOs en boundaries de API
- **Security**: ver `@.claude/rules/security.md`
  - Validar input en boundaries
  - No exponer stack traces
  - Hash secrets antes de persistir

Ejecutar y verificar que PASA:
```bash
<verify_cmd>
# Salida esperada: PASS — X test(s) passed
```

---

## Phase 3 — REFACTOR: Mejorar sin Romper

Solo refactorizar si alguno de estos aplica:
- Función > 20 líneas → extraer helper
- Código duplicado con otro módulo → extraer utilidad
- Nombre no descriptivo → renombrar
- Magic number → nombrar constante

Regla: **no cambiar comportamiento**, solo estructura.

Después de cada cambio:
```bash
<verify_cmd>
# Debe seguir en PASS
```

---

## Phase 4 — Commit Atómico

Después de GREEN (o REFACTOR si aplica):

```
Skill('commit')
# Formato: tipo|TASK-ID|YYYYMMDD|descripción imperativa
# Ejemplo: feat|TASK-001|20260402|Add user existence validation in GET /users/:id
```

Un commit por tarea. No agrupar múltiples tareas en un commit.

---

## Output Esperado

Al completar emitir:
```
✅ TASK-NNN: <title>
   RED  → test falló correctamente
   GREEN → <verify_cmd> → X passed
   REFACTOR → [aplicado / no necesario]
   Commit: <hash> feat|TASK-NNN|...

<promise>COMPLETE</promise>
```

Si falla, aplicar **reflection retry** con forced-enumeration (patrón Aider + OpenHands):

```
# Intento 1 FAIL → reflection retry estándar
reflected_message = f"""
{output_literal_del_verify_cmd}

Intento 1/3 falló.
Root cause: {diagnosis}
Fix concreto: {fix_sugerido}
"""
→ volver a Phase 1 con reflected_message

# Intento 2 FAIL → forced-enumeration (OBLIGATORIO — no saltear)
#
# El retry 2 tiene la misma distribución de sampling que el retry 1 → mismo resultado probable.
# La enumeración forzada cambia el enfoque antes del tercer intento.
reflected_message = f"""
{output_literal_del_verify_cmd}

Intento 2/3 falló. El fix anterior no funcionó.

ANTES de intentar cualquier corrección, enumerar EXACTAMENTE 3 causas raíz candidatas
en orden de probabilidad:

1. [causa más probable] — probabilidad: X%
2. [segunda causa] — probabilidad: Y%
3. [tercera causa] — probabilidad: Z%

Causa elegida: [la #1]
Fix targeting esa causa específica: {fix_para_causa_1}
"""
→ volver a Phase 1 con reflected_message (fix debe apuntar a causa #1)

# Intento 3 FAIL → usar causa #2 (no la misma que intento 2)
reflected_message = f"""
{output_literal_del_verify_cmd}

Intento 3/3. La causa #1 ({causa_1}) fue descartada.
Implementando fix para causa #2: {fix_para_causa_2}
"""
```

Si falla después de 3 intentos:
```
❌ TASK-NNN: <title>
   Intentos: 3/3
   Último error: <output del verify_cmd>
   Archivos modificados: <lista>

<promise>FAIL</promise>
```

---

## Guardrails

- ❌ NUNCA escribir código sin test fallando primero (SDD Iron Law)
- ❌ No modificar el test para que pase — modificar el código
- ❌ No implementar más de lo que pide el test (YAGNI)
- ❌ No leer archivos no relacionados con la tarea actual
- ❌ No usar `any` en TypeScript
- ❌ No hardcodear secrets o magic numbers con significado de negocio
- ✅ Verificar con el comando exacto de la tarea, no `npm test` genérico

---

## Integración

```
plan → tasks.md → [subagent-driven-development invoca generate por tarea]
                    generate → commit → verify → siguiente tarea

pipeline simple: /dev → generate directamente → verify → done
pipeline bug: systematic-debugging → generate (reproduce + fix) → verify
```

**Siguiente skill**: `Skill('verify')` (gate antes de avanzar)
**Skill previo**: `Skill('plan')` (tasks.md) o invocación directa desde /dev
