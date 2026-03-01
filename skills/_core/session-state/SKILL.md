---
name: session-state
description: "Gestión de STATE.md para persistencia de estado entre sesiones. Reglas embedidas en session-orchestrator."
invokable: false
version: 1.0.0
---

# Session State - Reference Documentation

**Note**: This is reference documentation. The actual session-state rules are embedded in the `session-orchestrator` skill which is auto-loaded and manages STATE.md transparently on every session.

---

## Propósito

Permitir que Agent007 retenga contexto entre sesiones de Claude Code. Sin STATE.md, cada sesión comienza desde cero y el developer pierde 5-10 minutos reconstruyendo contexto. Con STATE.md, el contexto se retoma en < 30 segundos.

---

## Estructura de STATE.md

```markdown
# Agent007 Session State
_Última actualización: YYYY-MM-DD_

## Posición Actual
- **Branch**: {nombre del branch git}
- **Fase**: {idle|planning|execution|verification}
- **Tarea Activa**: {descripción o "ninguna"}

## Decisiones Tomadas
- YYYY-MM-DD: {decisión} → {rationale}

## Blockers Activos
- [ ] {descripción del blocker (qué lo desbloquea)}

## Tareas Completadas
- [x] {tarea} (YYYY-MM-DD HH:MM)

## Resumen de Última Sesión
- {bullet 1: qué se completó}
- {bullet 2: qué falta}
- {bullet 3: próximo paso recomendado}
```

---

## Reglas de Escritura

### Cuándo actualizar STATE.md

| Evento | Campos a actualizar |
|--------|---------------------|
| Inicio de sesión | Solo leer (no escribir) |
| Inicio de tarea | `Tarea Activa`, `Fase` |
| Decisión tomada | `Decisiones Tomadas` |
| Blocker detectado | `Blockers Activos` |
| Tarea completada | `Tareas Completadas`, `Tarea Activa` |
| Captura [D] | `Decisiones Tomadas` |
| Fin de sesión | `Resumen de Última Sesión`, `_Última actualización_` |

### Principios

1. **Silencioso**: Todos los updates son sin output al usuario
2. **Atómico**: Leer → modificar → escribir (no writes parciales)
3. **Conciso**: Máximo 3 bullets en Resumen, máximo 5 items en Completadas
4. **Honesto**: Si hay blocker, documentarlo aunque sea incómodo

---

## Ejemplos

### STATE.md con trabajo en progreso

```markdown
# Agent007 Session State
_Última actualización: 2026-02-28_

## Posición Actual
- **Branch**: feat/user-registration
- **Fase**: execution
- **Tarea Activa**: Implementar POST /users endpoint con validación

## Decisiones Tomadas
- 2026-02-28: JWT sobre sessions → stateless scaling requerido
- 2026-02-28: UUID para IDs → evitar enumeración

## Blockers Activos
- [ ] Email service provider no definido (bloquea tarea de confirmación)

## Tareas Completadas
- [x] CreateUserDto con validación (2026-02-28 14:32)
- [x] UserEntity con TypeORM (2026-02-28 13:15)

## Resumen de Última Sesión
- Completé DTO y Entity, tests pasando
- Falta: endpoint, servicio, e2e tests
- Próximo: implementar UsersService.create()
```

### STATE.md en estado limpio (fin de sprint)

```markdown
# Agent007 Session State
_Última actualización: 2026-02-28_

## Posición Actual
- **Branch**: main
- **Fase**: idle
- **Tarea Activa**: ninguna

## Decisiones Tomadas
- 2026-02-28: Usar cursor-based pagination → evitar N+1 con offset

## Blockers Activos
_(ninguno)_

## Tareas Completadas
- [x] User registration endpoint completo (2026-02-28 17:00)
- [x] E2E tests pasando (2026-02-28 16:45)
- [x] PR abierto y mergeado (2026-02-28 17:15)

## Resumen de Última Sesión
- Sprint de user registration completo, merge a main
- Tests: 47 passing, 0 failing
- Próximo sprint: email verification flow
```

---

## Banner de Retomada

Cuando `Tarea Activa` no es "ninguna" al iniciar sesión:

```
📋 **Retomando sesión anterior**

**Branch**: feat/user-registration
**Tarea Activa**: Implementar POST /users endpoint con validación
**Blockers**: Email service provider no definido
**Último avance**: Completé DTO y Entity, tests pasando. Falta: endpoint, servicio, e2e tests.

¿Continuamos con esto? [S/n]
```

Cuando `Tarea Activa` es "ninguna": sin banner, inicio silencioso.

---

## Integración con Knowledge Capture

Cuando el usuario selecciona [D] (Decisión) en el prompt post-tarea:
- La decisión se guarda en `.claude/memory/` (ya existente)
- **Y también** se agrega a `Decisiones Tomadas` en STATE.md

Esto asegura que las decisiones son visibles tanto en el estado de sesión (contexto inmediato) como en la memoria de largo plazo.
