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
references:
  - references/socratic-questions.md
  - references/discovery-document.md
---

# Product Discovery — Problem-First Feature Definition

**Propósito**: Validar que estamos resolviendo un problema real antes de invertir en construir soluciones. Usar antes de brainstorming técnico.

**Cuándo se activa**:
- Antes de features nuevas (validar necesidad)
- Al explorar nuevos productos/módulos
- Cuando el usuario dice "quiero agregar X" sin contexto de usuario

---

## Proceso de Discovery (4 fases)

El proceso es socrático: **una pregunta por vez, esperar respuesta antes de la siguiente**. El script completo (Q1–Q8 con todas las opciones) vive en `references/socratic-questions.md`.

| Fase | Preguntas | Goal |
|------|-----------|------|
| 1. Problem Framing | Q1 problema · Q2 alternativas actuales · Q3 evidencia | Confirmar que existe un problema real con dueño |
| 2. User & Context | Q4 target user · Q5 user journey | Entender quién, cuándo, en qué contexto |
| 3. Solution Exploration | Q6 MVP options · Q7 success metrics | Acordar la versión más chica que valida la hipótesis |
| 4. Scope Definition | Q8 must/should/could/won't | Cerrar scope antes de pasar a técnica |

**Recomendación por defecto en Q6**: empezar con feature mínima (1 happy path, sin edge cases) salvo evidencia fuerte que justifique más.

---

## Output: Discovery Document

Al cerrar las 4 fases, emitir el documento siguiendo el template de `references/discovery-document.md`. Secciones obligatorias: Problem Statement, Target User, Evidence, Proposed Solution (MVP), Success Metrics, Assumptions to Validate, Risks, Dependencies.

Antes de pasar a brainstorming técnico, confirmar el checklist de discovery completa (también en `references/discovery-document.md`).

---

## Red Flags — Discovery Incompleta

### "Build it because competitor has it"
```diff
- ❌ "Slack has threads, we should add threads"
+ ✅ "Our users request threaded conversations because they lose context in long channels (evidence: 15 support tickets in last month)"
```

### "The CEO/stakeholder wants it"
```diff
- ❌ "The CEO wants a dashboard"
+ ✅ "The CEO needs to see daily revenue, active users, and churn rate to make decisions about marketing spend"
```

### "It should be easy"
```diff
- ❌ "Just add a button to export to PDF"
+ ✅ "Users need PDF export for reports. Questions: What content? What format? Who has access? How often?"
```

### Solution disguised as problem
```diff
- ❌ "We need a notification system" (solución)
+ ✅ "Users miss important updates because they don't check the app daily" (problema)
```

---

## Anti-patterns (NEVER)

- ❌ Saltar a brainstorming técnico antes de validar el problema
- ❌ Hacer las 8 preguntas en un solo bloque — el script es socrático, una a la vez
- ❌ Aceptar "competitor has it" o "stakeholder wants it" como evidencia
- ❌ Confundir solución con problema ("necesitamos sistema de notificaciones" no es un problema)
- ❌ Definir scope sin Won't Have explícito — sin exclusiones, todo se vuelve must
- ❌ Métricas sin guardrail — siempre incluir qué métrica NO debe empeorar
- ❌ Cerrar discovery sin lista de assumptions a validar

## Required (ALWAYS)

- ✅ Una pregunta a la vez, esperar respuesta antes de continuar
- ✅ Q8 produce must / should / could / won't con razones
- ✅ Output final usa el template de `references/discovery-document.md`

---

## Integration with Workflow

```
Product Discovery (this skill) → Brainstorming → Writing Plans → TDD
        WHAT/WHY                    HOW                 TASKS         CODE
```

**Required follow-up skill**: `brainstorming` (technical exploration after discovery)
