---
name: generate
description: "TDD code generation cycle: RED (failing test) → GREEN (minimal code) → REFACTOR. Executes one task at a time from tasks.md. Use when implementing a single planned task or a simple change with no prior plan."
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash(npm test*)
  - Bash(pnpm test*)
  - Bash(yarn test*)
  - Bash(pytest*)
  - Bash(go test*)
  - Bash(cargo test*)
  - Bash(jest*)
  - Bash(vitest*)
invokable: true
accepts_args: true
version: 1.0.0
when:
  - task_type: [feature, bug, refactor]
    risk_level: [low, medium, high, critical]
  - after: plan
  - pipeline: [simple, medium, complex]
references:
  - references/tdd-task-execution.md
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

## Phase 4 — Commit Atómico + Reflection Retry

Después de GREEN (o REFACTOR si aplica):

```
Skill('commit')
# Formato: tipo|TASK-ID|YYYYMMDD|descripción imperativa
# Ejemplo: feat|TASK-001|20260402|Add user existence validation in GET /users/:id
```

Un commit por tarea. No agrupar múltiples tareas en un commit.

### Output PASS

```
✅ TASK-NNN: <title>
   RED  → test falló correctamente
   GREEN → <verify_cmd> → X passed
   REFACTOR → [aplicado / no necesario]
   Commit: <hash> feat|TASK-NNN|...

<promise>COMPLETE</promise>
```

### Output FAIL — Reflection Retry

Si falla en cualquier intento, aplicar **reflection retry con forced-enumeration**.
Protocolo completo (3 intentos, mensajes textuales para cada attempt) en:

→ `references/tdd-task-execution.md`

Resumen: attempt 1 = standard reflection · attempt 2 = forced enumeration de 3 causas raíz (OBLIGATORIO) · attempt 3 = pivot a causa #2 · 3/3 fail → escalar a humano con `<promise>FAIL</promise>`.

---

## Anti-patterns (NEVER)

- ❌ Escribir código sin test fallando primero (rompe SDD Iron Law)
- ❌ Modificar el test para que pase — modificar el código en su lugar
- ❌ Implementar más de lo que pide el test (YAGNI)
- ❌ Leer archivos no relacionados con la tarea actual (context bloat)
- ❌ Usar `any` en TypeScript
- ❌ Hardcodear secrets o magic numbers con significado de negocio
- ❌ Saltear forced-enumeration en attempt 2 (mismo sampling → mismo resultado)
- ❌ Reintentar más de 3 veces — escalar al humano

## Required (ALWAYS)

- ✅ Verificar con el comando exacto de la tarea, no `npm test` genérico
- ✅ El reflected_message incluye output literal + root cause + fix concreto

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
