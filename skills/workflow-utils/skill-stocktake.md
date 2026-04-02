---
name: skill-stocktake
description: "Auditoría periódica de calidad del skill registry. Detecta skills obsoletos, solapados, o de bajo valor. Produce veredictos: Keep / Improve / Retire / Merge."
invokable: true
accepts_args: true
version: 1.0.0
when:
  keywords: ["skill audit", "stocktake", "review skills", "skill quality", "clean skills"]
---

# Skill Stocktake — Auditoría Periódica del Registry

**Propósito**: Prevenir el deterioro del skill library. A medida que crece, skills pueden quedar obsoletos, solapados, o sin valor real.

---

## Modos

### Quick Scan (default)
Re-evalúa solo los skills modificados recientemente comparando contra `results.json` cacheado.
Usar: cuando quieres una auditoría rápida sin recorrer todo el registry.

```
Skill('skill-stocktake') mode=quick
```

### Full Stocktake
4 fases completas: inventory → quality assessment → summary → consolidation plan.
Usar: periódicamente (ej. cada 2 semanas o después de agregar 5+ skills nuevos).

```
Skill('skill-stocktake') mode=full
```

---

## Phase 1 — Inventory

Listar todos los skills con:
- Ruta del archivo
- Fecha de última modificación
- Invokable (sí/no)
- Keywords registradas

---

## Phase 2 — Quality Assessment

Para cada skill, evaluar con esta checklist:

| Criterio | Pregunta |
|----------|----------|
| Overlap | ¿Más de 2 skills cubren el mismo dominio? |
| Currency | ¿El contenido sigue siendo técnicamente correcto? |
| Actionability | ¿Produce output concreto o es solo teoría? |
| Scope alignment | ¿El scope es correcto? ¿No es demasiado amplio ni demasiado específico? |
| Keywords | ¿Las keywords son las que un usuario real usaría? |

**Verdicts posibles**:

| Veredicto | Significado |
|-----------|-------------|
| `Keep` | Skill de calidad, sin cambios |
| `Improve` | Skill válido pero necesita actualización de contenido |
| `Update` | Keywords o metadata desactualizados, contenido OK |
| `Retire` | Skill obsoleto o completamente cubierto por otro |
| `Merge into [target]` | Contenido valioso pero mejor como sección de otro skill |

---

## Phase 3 — Summary

Tabla resumen con todos los veredictos:

| Skill | Veredicto | Razón |
|-------|-----------|-------|
| `plan` | Keep | Pipeline core, bien mantenido |
| `gsap-core` (old) | Retired | Consolidado en gsap monolítico |
| ... | ... | ... |

---

## Phase 4 — Consolidation Plan

Para cada `Retire` o `Merge`:
1. Confirmar con el usuario antes de ejecutar
2. Si Merge: copiar sección relevante al target antes de eliminar
3. Actualizar `skills/INDEX.md` después de cada cambio
4. Cachear resultados en `.claude/skill-stocktake-results.json`

---

## Guardrail

**Nunca ejecutar Phase 4 sin aprobación explícita del usuario.**
El skill solo propone; el usuario aprueba cada cambio destructivo.
