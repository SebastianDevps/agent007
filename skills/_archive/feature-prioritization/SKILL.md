---
name: feature-prioritization
description: "Priorizar features usando RICE/ICE, crear roadmap, gestionar backlog. Para planificación de producto."
invokable: true
accepts_args: true
auto-activate: false
version: 1.0.0
when:
  - user_mentions: ["prioritize", "roadmap", "what to build next", "backlog", "sprint planning"]
---

# Feature Prioritization - Data-Driven Decision Making

**Propósito**: Priorizar features de forma objetiva usando frameworks probados, evitando el "HiPPO" (Highest Paid Person's Opinion).

---

## Frameworks de Priorización

### RICE Score (Recomendado para startups)

**Fórmula**: `(Reach × Impact × Confidence) / Effort`

| Factor | Cómo medir | Escala |
|--------|-----------|--------|
| **Reach** | Usuarios afectados por trimestre | Número real (100, 1000, 10000) |
| **Impact** | Cuánto mejora la experiencia | 3=massive, 2=high, 1=med, 0.5=low, 0.25=min |
| **Confidence** | Qué tan seguros estamos | 100%=data, 80%=some data, 50%=intuition |
| **Effort** | Person-months de trabajo | 0.5, 1, 2, 3, 5, 8 |

**Ejemplo**:
```
Feature: "Add search to dashboard"
Reach:      2000 users/quarter
Impact:     2 (high - saves 5 min/day)
Confidence: 80% (user interviews + data)
Effort:     1 person-month

RICE = (2000 × 2 × 0.8) / 1 = 3200
```

---

### ICE Score (Alternativa rápida)

**Fórmula**: `(Impact + Confidence + Ease) / 3`

| Factor | Escala |
|--------|--------|
| **Impact** | 1-10 (10 = game changer) |
| **Confidence** | 1-10 (10 = 100% seguro) |
| **Ease** | 1-10 (10 = trivial) |

---

### Value vs Effort Matrix

```
              LOW EFFORT          HIGH EFFORT
HIGH VALUE  │ 🟢 QUICK WINS      │ 🔵 BIG BETS
            │ Do first!           │ Plan carefully
            │                     │
LOW VALUE   │ 🟡 FILL-INS        │ 🔴 MONEY PITS
            │ Do if time allows   │ Avoid!
```

---

## Proceso de Priorización

### Paso 1: Listar Features

```markdown
## Feature Backlog

| # | Feature | Source | Status |
|---|---------|--------|--------|
| 1 | [Feature A] | User feedback | New |
| 2 | [Feature B] | CEO request | New |
| 3 | [Feature C] | Support tickets | New |
| 4 | [Tech Debt X] | Engineering | Recurring |
```

---

### Paso 2: Score Each Feature

Para cada feature, hacer estas preguntas:

```markdown
**Feature: [nombre]**

**Reach** (¿Cuántos usuarios se benefician?):
  - [ ] < 100 users → Write number
  - [ ] 100-1000 users → Write number
  - [ ] 1000+ users → Write number

**Impact** (¿Cuánto mejora su vida?):
  - [ ] 3 = Massive (desbloquea uso completo del producto)
  - [ ] 2 = High (mejora significativa en workflow)
  - [ ] 1 = Medium (mejora notable pero no transformadora)
  - [ ] 0.5 = Low (mejora menor)
  - [ ] 0.25 = Minimal (nice to have)

**Confidence** (¿Qué tan seguros estamos?):
  - [ ] 100% = High (datos de analytics + user research)
  - [ ] 80% = Medium (some data o user feedback)
  - [ ] 50% = Low (intuición o competitive analysis)

**Effort** (¿Cuánto trabajo?):
  - [ ] 0.5 = Medio día de trabajo
  - [ ] 1 = 1 person-week
  - [ ] 2 = 2 person-weeks
  - [ ] 3 = 3 person-weeks
  - [ ] 5+ = 1+ month

**RICE** = (Reach × Impact × Confidence) / Effort = ___
```

---

### Paso 3: Rank & Categorize

```markdown
## Prioritized Backlog

| Priority | Feature | RICE | Category | Timeline |
|----------|---------|------|----------|----------|
| 🔴 P0 | Feature A | 3200 | Quick Win | This sprint |
| 🔴 P0 | Feature B | 2800 | Quick Win | This sprint |
| 🟠 P1 | Feature C | 1500 | Big Bet | Next sprint |
| 🟡 P2 | Feature D | 800 | Fill-in | This quarter |
| ⚪ P3 | Feature E | 200 | Backlog | Later |
```

---

### Paso 4: Apply Constraints

Después del RICE score, ajustar por:

```markdown
## Constraint Adjustments

### Dependencies
- Feature C requires Feature A → Move A before C
- Feature D requires DB migration → Add migration task

### Team Capacity
- 2 backend developers × 2 weeks = 4 person-weeks available
- 1 frontend developer × 2 weeks = 2 person-weeks available
- Total capacity: 6 person-weeks this sprint

### Strategic Alignment
- Company goal Q1: Improve retention
  → Boost features that impact retention
  → Deprioritize acquisition features

### Tech Debt Tax
- Allocate 20% capacity to tech debt
  → 1.2 person-weeks for tech debt this sprint
```

---

### Paso 5: Create Roadmap

```markdown
## Roadmap Q1 2026

### NOW (This Sprint - 2 weeks)
| Feature | Owner | Effort | Dependencies |
|---------|-------|--------|-------------|
| Feature A | Backend | 1w | None |
| Feature B | Frontend | 0.5w | None |
| Tech Debt: Fix N+1 | Backend | 0.5w | None |

### NEXT (Next Sprint - 2 weeks)
| Feature | Owner | Effort | Dependencies |
|---------|-------|--------|-------------|
| Feature C | Full-stack | 2w | Feature A |

### LATER (This Quarter)
| Feature | Owner | Effort | Dependencies |
|---------|-------|--------|-------------|
| Feature D | TBD | 3w | Feature C |
| Feature E | TBD | 1w | None |

### NOT DOING (Explicitly Deprioritized)
| Feature | Reason |
|---------|--------|
| Feature F | Low RICE (200), revisit Q2 |
| Feature G | Competitor parity, not user need |
```

---

## Output: Prioritization Report

```markdown
# Feature Prioritization Report

**Date**: [fecha]
**Sprint/Quarter**: [período]
**Team Capacity**: [person-weeks disponibles]

## Scoring Summary

| Feature | Reach | Impact | Conf | Effort | RICE | Priority |
|---------|-------|--------|------|--------|------|----------|
| [A] | 2000 | 3 | 100% | 1 | 6000 | 🔴 P0 |
| [B] | 1500 | 2 | 80% | 0.5 | 4800 | 🔴 P0 |
| [C] | 1000 | 2 | 80% | 2 | 800 | 🟠 P1 |
| [D] | 500 | 1 | 50% | 3 | 83 | 🟡 P2 |

## Recommended Sprint Plan
[Features seleccionadas con justificación]

## Key Decisions
- [Decision 1 con rationale]
- [Decision 2 con rationale]

## What We're NOT Doing (and why)
- [Feature X]: [razón]

## Open Questions
- [ ] [Pregunta que afecta priorización]

---
**Next Step**: product-discovery (para features P0 sin discovery) o brainstorming (para features P0 con discovery completa)
```

---

## Anti-Patterns a Evitar

### 🚩 "Todo es P0"
Si todo es prioridad máxima, nada lo es. Limitar P0 a 2-3 items por sprint.

### 🚩 "El CEO lo pidió"
Scorear igual que cualquier feature. Si tiene alto RICE, bien. Si no, explicar por qué no.

### 🚩 "Es fácil, hagámoslo"
Effort bajo no justifica features de bajo impacto. Quick wins son High Value + Low Effort.

### 🚩 "La competencia lo tiene"
Competitive parity no es razón suficiente. ¿Tus usuarios lo necesitan? ¿Hay evidencia?

### 🚩 Ignorar tech debt
Asignar 15-20% de capacidad a tech debt siempre. La deuda técnica acumula interés.

---

**Tip**: Re-priorizar al inicio de cada sprint. Los scores cambian con nueva información.
