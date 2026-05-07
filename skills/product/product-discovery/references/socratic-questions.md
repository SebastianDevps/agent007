# Socratic Questions — Product Discovery

The full 8-question script used by `product-discovery` to validate a feature idea before any technical brainstorming.

**Rule**: One question at a time. Wait for the user's answer before sending the next question.

---

## Fase 1 — Problem Framing

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

## Fase 2 — User & Context

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

## Fase 3 — Solution Exploration

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

## Fase 4 — Scope Definition

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
