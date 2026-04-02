---
name: plan
description: "Decomposes an approved DECISIONS.md into atomic 2-5 minute tasks with TDD steps, file paths, and dependencies. Produces docs/changes/<feature>/tasks.md consumed by subagent-driven-development. Use when user asks to 'plan', 'break down', or after brainstorming approves a spec."
invokable: true
accepts_args: true
version: 1.0.0
when:
  - task_type: [feature, refactor, bug]
    risk_level: [medium, high, critical]
  - after: brainstorming
---

# Plan — Feature Decomposition

**Propósito**: Convertir un spec aprobado en tareas atómicas de 2-5 min con TDD, rutas exactas de archivos y dependencias explícitas — listo para `subagent-driven-development`.

**Cuándo activar**:
- Después de `Skill('brainstorming')` con `DECISIONS.md` aprobado
- En /dev medium/complex después de determinar la ruta
- Refactors: después de `Skill('reverse-engineer')`

**Guard**: Busca `DECISIONS.md` con `Approved: yes`. Sin él, detener y mostrar:
```
⛔ Plan bloqueado: no hay DECISIONS.md aprobado.
Ejecuta Skill('brainstorming') primero o crea .sdlc/specs/<feature>/DECISIONS.md con `Approved: yes`.
Bypass: Skill('plan') --force  (registra en .sdlc/knowledge/force-bypass.log)
```

---

## Phase 1 — Leer el Contexto

1. Leer `.sdlc/specs/<feature>/DECISIONS.md` (acceptance criteria, edge cases, decisiones)
2. Leer `MASTER_GUIDE.md` y `.sdlc/context/tech-stack.md` (stack, convenciones)
3. Glob archivos relevantes para entender estructura existente
4. Derivar `<feature-slug>` del nombre de la feature (lowercase, hyphens)

---

## Phase 2 — Descomponer en Tareas Atómicas

**Regla**: cada tarea = una sola responsabilidad, 2-5 minutos de implementación, un commit atómico.

**Orden obligatorio por tipo**:
```
backend feature:  schema → migration → entity → repository → service → controller → e2e test
frontend feature: types → component → hook → integration test → e2e test
bug fix:          reproduce test (RED) → fix → verify green
refactor:         capture behavior test → refactor → re-verify
```

**Por cada tarea definir**:
- `id`: TASK-NNN (secuencial, 3 dígitos)
- `title`: verbo imperativo ≤ 60 chars
- `domain`: backend | frontend | platform | security | mixed
- `depends_on`: lista de IDs que deben completarse antes (o `[]`)
- `acceptance_criteria`: ≥ 2 criterios observables y verificables
- `test_first`: descripción del test que debe fallar antes de implementar (TDD RED)
- `files`: rutas exactas a crear/modificar (verificadas con Glob/Grep)
- `verify_cmd`: comando para verificar esta tarea específica
- `estimated_min`: 2–5

---

## Phase 3 — Generar tasks.md

Crear `docs/changes/<feature-slug>/tasks.md`:

```markdown
# Tasks — <Feature Name>
spec: .sdlc/specs/<feature-slug>/DECISIONS.md
created: <ISO date>
workflow_id: <feature-slug>-<timestamp>

## TASK-001
title: <verbo imperativo>
domain: backend
depends_on: []
acceptance_criteria:
  - <criterio 1 observable>
  - <criterio 2 observable>
test_first: |
  describe('<unit>', () => {
    it('should <behavior> when <condition>', () => {
      // RED: este test debe fallar antes de implementar
    });
  });
files:
  - src/path/to/file.ts  [create]
  - src/path/to/other.ts [modify]
verify_cmd: npm test -- --testPathPattern="<file>"
estimated_min: 3

## TASK-002
...
```

---

## Phase 3b — Escribir Active Plan Artifact

Inmediatamente después de generar `docs/changes/<feature-slug>/tasks.md`, escribir también a `.sdlc/tasks/active-plan.md`:

```markdown
# Active Plan — <Feature Name>
created: <ISO date>
source: docs/changes/<feature-slug>/tasks.md

## Objetivo Global
<acceptance criteria del spec en 2-3 líneas — qué debe ser verdad cuando todo termine>

## Task Map
| ID | Título | Dominio | Depende de | Criterio verificable |
|----|--------|---------|------------|----------------------|
| TASK-001 | ... | backend | [] | [cmd] → exit 0 |
| TASK-002 | ... | frontend | [TASK-001] | [cmd] → exit 0 |

## Decisiones Tomadas
- [decisiones de DECISIONS.md relevantes para todos los subagentes]
- [elecciones de stack, patrones, convenciones aplicadas]

## Constraints Globales
- [reglas que TODAS las tareas deben respetar: naming, patterns, stack versions]
```

**Por qué**: Cada subagente en `subagent-driven-development` recibe `@.sdlc/tasks/active-plan.md` como contexto global. Sin él, los subagentes toman decisiones localmente correctas pero globalmente incompatibles (ej: dos subagentes eligiendo schemas de datos distintos para el mismo recurso). Con el plan compartido, todos trabajan desde el mismo mapa.

---

## Phase 4 — Validar el Plan

Antes de presentar, verificar:
- [ ] Todas las rutas en `files` existen o tienen path válido para creación
- [ ] `depends_on` no tiene ciclos
- [ ] Cada tarea tiene `test_first` (TDD Iron Law)
- [ ] `verify_cmd` es ejecutable (no referencia archivos que aún no existen)
- [ ] Suma de `estimated_min` es coherente con complejidad

---

## Phase 5 — Presentar y Confirmar

```
📋 Plan generado: docs/changes/<feature>/tasks.md
   Tareas: N  |  Tiempo estimado: ~X min  |  Waves: K

Wave 1 (paralelo): TASK-001, TASK-002
Wave 2 (paralelo): TASK-003, TASK-004
Wave 3 (secuencial): TASK-005

¿Proceder con subagent-driven-development? [S]í / [E]ditar tasks / [C]ancelar
```

---

## Guardrails

- ❌ Nunca escribir código en este skill — solo el plan
- ❌ No asumir rutas de archivos sin verificar con Glob/Grep
- ❌ No crear tareas de más de 5 min — dividir si es necesario
- ❌ No omitir `test_first` — es el Iron Law de SDD
- ✅ El plan debe ser auto-suficiente: un agente fresco debe poder ejecutar cualquier tarea leyendo solo tasks.md

---

## Integración

```
brainstorming → DECISIONS.md (Approved: yes) → plan → tasks.md → subagent-driven-development
reverse-engineer → captured behavior → plan → tasks.md → subagent-driven-development
```

**Siguiente skill**: `Skill('subagent-driven-development')` (lee tasks.md)
**Skill previo**: `Skill('brainstorming')` o `Skill('reverse-engineer')`
