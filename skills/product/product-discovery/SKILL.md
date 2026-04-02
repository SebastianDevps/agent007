---
name: product-discovery
description: "Validar ideas de producto, definir MVP, explorar problemas de usuario. Use when user asks to 'validate idea', 'define MVP', 'product discovery', or 'validate user needs'."
invokable: true
accepts_args: true
allowed-tools: ["Read", "Grep", "Glob"]
auto-activate: false
version: 1.0.0
when:
  - task_type: product
    risk_level: [medium, high, critical]
  - user_mentions: ["validate idea", "mvp", "product discovery", "user needs", "problem validation"]
---

# Product Discovery - Problem-First Feature Definition

**Propósito**: Validar que estamos resolviendo un problema real antes de invertir en construir soluciones. Usar antes de brainstorming técnico.

**Cuándo se activa**:
- Antes de features nuevas (validar necesidad)
- Al explorar nuevos productos/módulos
- Cuando el usuario dice "quiero agregar X" sin contexto de usuario

---

## Proceso de Discovery

### Fase 1: Problem Framing

**Pregunta una a la vez (estilo socrático):**

```markdown
**Q1: Problem Statement**
¿Qué problema específico estamos resolviendo?
  - ¿Quién tiene este problema? (segmento específico)
  - ¿Con qué frecuencia lo experimentan?
  - ¿Qué tan doloroso es? (showstopper, annoying, nice-to-have)

[Wait for answer]

**Q2: Current Alternatives**
¿Cómo lo resuelven hoy los usuarios?
  A) Manual workaround (Excel, email, etc.)
  B) Herramienta de terceros
  C) No lo resuelven (sufren en silencio)
  D) Feature existente parcialmente lo cubre

[Wait for answer]

**Q3: Evidence**
¿Qué evidencia tenemos de que este problema es real?
  A) User interviews / tickets de soporte
  B) Data de analytics (drop-offs, workarounds)
  C) Competitive analysis
  D) Intuición / hipótesis (necesita validación)

[Wait for answer]
```

---

### Fase 2: User & Context

```markdown
**Q4: Target User**
¿Quién es el usuario principal de esta feature?
  - Rol / persona
  - Nivel técnico
  - Frecuencia de uso
  - Contexto (mobile, desktop, on-the-go)

[Wait for answer]

**Q5: User Journey**
¿En qué momento del journey del usuario aparece esta necesidad?
  - ¿Qué estaba haciendo antes?
  - ¿Qué trigger activa la necesidad?
  - ¿Qué espera lograr?
  - ¿Qué hace después?

[Wait for answer]
```

---

### Fase 3: Solution Exploration

```markdown
**Q6: Minimum Viable Solution**
¿Cuál es la versión más simple que valida la hipótesis?

Opciones para explorar:
  A) Fake door test (botón que mide interés)
  B) Manual behind the scenes (concierge MVP)
  C) Feature mínima (1 happy path, sin edge cases)
  D) Feature completa (todas las variantes)

Mi recomendación: empezar con C a menos que haya evidencia fuerte.

[Wait for answer]

**Q7: Success Metrics**
¿Cómo sabemos que esta feature fue exitosa?
  - Métrica primaria: [ej: % de usuarios que completan el flujo]
  - Métrica secundaria: [ej: tiempo para completar]
  - Guardrail: [ej: no debe empeorar retention]

[Wait for answer]
```

---

### Fase 4: Scope Definition

```markdown
**Q8: MVP Scope**
Basado en tus respuestas, propongo este scope:

**Must Have** (sin esto no tiene valor):
- [ ] Item 1
- [ ] Item 2

**Should Have** (mejora significativa):
- [ ] Item 3
- [ ] Item 4

**Could Have** (nice to have):
- [ ] Item 5

**Won't Have** (explícitamente excluido):
- [ ] Item 6 (razón: [complejidad/poco valor])

¿Estás de acuerdo con este scope?

[Wait for confirmation]
```

---

## Output: Discovery Document

Al completar las fases, generar:

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

## Red Flags - Discovery Incompleta

### 🚩 "Build it because competitor has it"
```diff
- ❌ "Slack has threads, we should add threads"
+ ✅ "Our users request threaded conversations because they lose context in long channels (evidence: 15 support tickets in last month)"
```

### 🚩 "The CEO/stakeholder wants it"
```diff
- ❌ "The CEO wants a dashboard"
+ ✅ "The CEO needs to see daily revenue, active users, and churn rate to make decisions about marketing spend"
```

### 🚩 "It should be easy"
```diff
- ❌ "Just add a button to export to PDF"
+ ✅ "Users need PDF export for reports. Questions: What content? What format? Who has access? How often?"
```

### 🚩 Solution disguised as problem
```diff
- ❌ "We need a notification system" (solución)
+ ✅ "Users miss important updates because they don't check the app daily" (problema)
```

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

**Required follow-up skill**: brainstorming (technical exploration after discovery)
