---
name: ralph-loop-wrapper/context-compact
description: Proactive context compaction checkpoint pattern (OpenHands-inspired) — compress at 60% before reactive pressure
---

# Proactive Context Compact Checkpoint (patrón OpenHands)

Antes de cada iteración del loop, verificar budget de contexto. Si supera el 60%, el agente debe comprimir proactivamente **antes** de que la presión de contexto fuerce una compactación de emergencia.

```
PRE-ITERATION CHECKPOINT (ejecutar al inicio de cada iteración):

1. Verificar: leer .sdlc/state/context-budget.json (escrito por context-engine.py hook)
   - Si percent < 60% → continuar iteración normalmente
   - Si percent ≥ 60% → ejecutar /compact ANTES de continuar

2. Después de /compact, escribir a .sdlc/state/session.md con schema fijo:
   ---
   compact_at: <ISO timestamp>
   iteration: <N de M>
   completed_tasks: [lista de tareas completadas en este loop]
   pending_tasks: [lista de tareas aún pendientes]
   current_branch: <branch>
   last_verified_state: <output del último verify_cmd exitoso>
   open_assumptions: [decisiones tomadas que podrían necesitar revisión]
   ---

3. En la siguiente iteración: releer .sdlc/state/session.md en vez de reconstruir
   estado desde historial de conversación completo.
```

**Por qué esto importa**: El enfoque actual espera al 70% para advertir y al 85% para bloquear — ambas son respuestas reactivas bajo presión. Un agente que comprime proactivamente al 60% mantiene headroom suficiente para completar la iteración actual sin interrupciones. El estado serializado en session.md sobrevive la compactación porque está en disco — no en el contexto del modelo.
