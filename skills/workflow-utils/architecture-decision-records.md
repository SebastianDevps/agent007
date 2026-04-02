---
name: architecture-decision-records
description: "Captura decisiones de arquitectura como ADRs versionados en docs/adr/. Detecta momentos de decisión y propone estructura Michael Nygard. Requiere consent explícito antes de escribir."
invokable: true
accepts_args: true
version: 1.0.0
when:
  keywords: ["adr", "architecture decision", "decision record", "why did we choose", "document decision", "record decision"]
---

# Architecture Decision Records (ADRs)

**Propósito**: Capturar el *por qué* de las decisiones de arquitectura, no solo el *qué*. Los ADRs son el activo de documentación de mayor retorno: permiten a futuros desarrolladores (y agentes IA) entender restricciones sin reconstruirlas desde el historial de git.

---

## Cuándo Proponer un ADR

Detectar momentos de decisión durante sesiones de planning:
- Elección de framework/librería entre alternativas
- Decisión de diseño de API (REST vs GraphQL, cursor vs offset pagination)
- Patrón de arquitectura (monolito vs microservicios, DDD vs CRUD)
- Trade-off de almacenamiento (Redis vs in-memory, SQL vs NoSQL)
- Decisión de autenticación (JWT vs sessions, OAuth provider)

**Señal**: el usuario dice "decidimos usar X", "elegimos Y sobre Z", o cuando hay una discusión con alternativas.

---

## Formato ADR (Michael Nygard)

Archivo: `docs/adr/NNN-titulo-en-kebab-case.md`

```markdown
# ADR-NNN: Título descriptivo de la decisión

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded by [ADR-XXX]

## Context

Describe el problema o necesidad que fuerza esta decisión.
Incluye restricciones técnicas, de negocio, o de equipo relevantes.

## Decision

La decisión tomada, en una oración clara.
"Hemos decidido usar X para Y."

## Alternatives Considered

| Alternativa | Pros | Contras | Por qué descartada |
|-------------|------|---------|-------------------|
| Opción A (elegida) | ... | ... | — |
| Opción B | ... | ... | [razón concreta] |
| Opción C | ... | ... | [razón concreta] |

## Consequences

### Positive
- ...

### Negative
- ...

### Neutral
- ...
```

---

## Lifecycle de un ADR

```
Proposed → Accepted → (tiempo) → Deprecated | Superseded by ADR-XXX
```

**Superseded**: cuando se toma una nueva decisión que reemplaza esta. Agregar link cruzado:
```markdown
**Status**: Superseded by [ADR-015](015-nueva-decision.md)
```

**Nunca borrar ADRs**: marcar como Deprecated/Superseded con contexto. Los ADRs históricos explican por qué el sistema llegó a su estado actual.

---

## Mantenimiento del Índice

En `docs/adr/README.md`:

```markdown
# Architecture Decision Records

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [001](001-uso-de-jwt.md) | Uso de JWT para autenticación | Accepted | 2026-01-15 |
| [002](002-cursor-pagination.md) | Cursor-based pagination | Accepted | 2026-02-01 |
```

---

## Protocol de Escritura

1. Detectar momento de decisión → proponer ADR al usuario
2. Esperar aprobación explícita antes de crear archivos
3. Si aprobado: crear `docs/adr/` si no existe, numeración secuencial
4. Actualizar `docs/adr/README.md` con la nueva entrada
5. Confirmar con el usuario que el contenido refleja la decisión correctamente

**Guardrail**: nunca escribir archivos ADR sin aprobación. El skill propone; el usuario aprueba.
