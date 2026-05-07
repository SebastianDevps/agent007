# Discovery Document Template

Output template emitted by `product-discovery` after the 8-question script is complete.

```markdown
# Product Discovery: [Feature Name]

**Date**: [fecha]
**Status**: Discovery Complete → Ready for Brainstorming

---

## Problem Statement
[Resumen claro del problema]

## Target User
- **Persona**: [descripción]
- **Context**: [cuándo y dónde usa la feature]
- **Current workaround**: [qué hace hoy]

## Evidence
- [Tipo de evidencia y fuente]

## Proposed Solution (MVP)
[Descripción de la solución mínima]

### In Scope
- [Item 1]
- [Item 2]

### Out of Scope
- [Item excluido] (reason: [razón])

## Success Metrics
- **Primary**: [métrica + target]
- **Secondary**: [métrica + target]
- **Guardrail**: [métrica que no debe empeorar]

## Assumptions to Validate
- [ ] [Assumption 1] - How to test: [método]
- [ ] [Assumption 2] - How to test: [método]

## Risks
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| [Risk 1] | Medium | High | [Mitigation] |

## Dependencies
- [Dependency 1]
- [Dependency 2]

---

**Next Step**: → brainstorming (technical exploration)
```

---

## Checklist: Discovery Completa

Antes de pasar a brainstorming, confirmar:

- [ ] **Problema articulado**: Podemos explicar el "por qué" en una oración
- [ ] **Usuario identificado**: Sabemos quién y en qué contexto
- [ ] **Evidencia presentada**: No es solo intuición
- [ ] **MVP definido**: Scope claro con must/should/could/won't
- [ ] **Métricas establecidas**: Sabemos cómo medir éxito
- [ ] **Assumptions listadas**: Sabemos qué estamos asumiendo
- [ ] **Risks evaluados**: Sabemos qué puede fallar

---

## Integration with Workflow

### Discovery → Brainstorming → Planning → TDD

```
Product Discovery (this skill)
  → Define WHAT and WHY
  → Output: Discovery Document

Brainstorming (workflow/brainstorming)
  → Define HOW technically
  → Input: Discovery Document
  → Output: Design Document

Writing Plans (workflow/writing-plans)
  → Break into tasks
  → Input: Design Document
  → Output: Task List

TDD (workflow/tdd)
  → Implement with tests
  → Input: Task List
  → Output: Working code
```
