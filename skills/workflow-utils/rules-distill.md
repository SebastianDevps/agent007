---
name: rules-distill
description: "Extrae principios recurrentes de múltiples skills y los eleva a rules/. Cierra el loop entre skill accumulation y rules maintenance. Requiere aprobación explícita antes de escribir."
invokable: true
accepts_args: false
version: 1.0.0
when:
  keywords: ["rules distill", "extract rules", "update rules", "rules from skills", "principles"]
---

# Rules Distill — Principios Cross-Skills → Rules/

**Propósito**: Cerrar el loop entre skills y rules. A medida que se acumulan skills, emergen principios que deberían elevarse a reglas siempre-activas. Sin este proceso, skills y rules divergen.

---

## ¿Cuándo Ejecutar?

- Después de agregar 3+ skills nuevos relacionados
- Cuando se observa una regla implícita repetida en múltiples skills
- Periódicamente (ej. cada mes)

---

## Phase 1 — Inventario

1. Listar todos los skills en `skills/INDEX.md`
2. Listar todas las reglas activas en `rules/`
3. Por cada skill invokable, leer su sección de Guardrails o restricciones

---

## Phase 2 — Extracción de Candidatos

Un principio **califica** para elevarse a rule si:
- Aparece en **2+ skills** (mismo principio, distintas formulaciones)
- Es **accionable**: "haz X" / "nunca hagas Y" (no abstracto)
- Tiene **riesgo de violación claro**: sabemos qué pasa si se incumple
- **No está ya cubierto** en `rules/`

Para cada candidato, proponer una de estas acciones:

| Acción | Descripción |
|--------|-------------|
| `Append` | Agregar al rules/ file existente más relevante |
| `Revise` | Actualizar una rule existente que es parcial |
| `New Section` | Agregar sección a un rules/ file |
| `New File` | Crear nuevo rules/ file para este dominio |
| `Already Covered` | La rule ya existe — no hacer nada |
| `Too Specific` | El principio aplica solo a un skill, no elevarlo |

---

## Phase 3 — Propuesta (Requiere Aprobación)

Presentar al usuario la lista completa de candidatos con la acción propuesta:

```
Candidato: "Siempre buscar antes de escribir utilities nuevos"
Aparece en: search-first.md, plan.md, brainstorming.md
Acción propuesta: Append → rules/patterns.md
Sección: ## Search Before Build
Contenido propuesto:
  "Before writing any utility, helper, or abstraction, execute a structured
   search: codebase → npm/PyPI → MCP servers → GitHub. Decision:
   exact match → Adopt; partial → Extend; multiple weak → Compose; none → Build."
```

**El usuario debe aprobar explícitamente antes de cualquier write.**
Respuesta válida: "sí, procede" / "aprobado" / "proceed with all".

---

## Phase 4 — Ejecución (Solo Tras Aprobación)

Para cada candidato aprobado:
1. Editar el archivo target con la nueva regla
2. Si es New File: crear `rules/<dominio>.md` con frontmatter apropiado
3. Agregar referencia en `CLAUDE.md` si el file es nuevo
4. Verificar que la nueva regla no contradiga reglas existentes

---

## Guardrail Máximo

**NUNCA modificar `rules/` sin aprobación explícita del usuario.**
Este skill es de análisis y propuesta. La escritura es opt-in.
