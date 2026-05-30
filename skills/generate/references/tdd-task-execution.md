# TDD Task Execution — Reference

Detailed reflection-retry protocol used by `generate.md` Phase 4 / verify failures.

## Reflection Retry — Forced Enumeration

The error does not trigger a generic retry. The literal output of the verify command becomes the next input to the implementer. The model corrects itself with real context.

### Attempt 1 FAIL — Standard Reflection

```
reflected_message = f"""
{output_literal_del_verify_cmd}

Intento 1/3 falló.
Root cause: {diagnosis}
Fix concreto: {fix_sugerido}
"""
→ volver a Phase 1 con reflected_message
```

### Attempt 2 FAIL — Forced Enumeration (MANDATORY, do not skip)

Retry 2 has the same sampling distribution as retry 1 → likely same result.
Forced enumeration changes the approach before the third attempt.

```
reflected_message = f"""
{output_literal_del_verify_cmd}

Intento 2/3 falló. El fix anterior no funcionó.

ANTES de intentar cualquier corrección, enumerar EXACTAMENTE 3 causas raíz candidatas
en orden de probabilidad:

1. [causa más probable] — probabilidad: X%
2. [segunda causa] — probabilidad: Y%
3. [tercera causa] — probabilidad: Z%

Causa elegida: [la #1]
Fix targeting esa causa específica: {fix_para_causa_1}
"""
→ volver a Phase 1 con reflected_message (fix debe apuntar a causa #1)
```

### Attempt 3 FAIL — Pivot to Cause #2

```
reflected_message = f"""
{output_literal_del_verify_cmd}

Intento 3/3. La causa #1 ({causa_1}) fue descartada.
Implementando fix para causa #2: {fix_para_causa_2}
"""
```

## Failure Output (3/3 exhausted)

```
❌ TASK-NNN: <title>
   Intentos: 3/3
   Último error: <output del verify_cmd>
   Archivos modificados: <lista>

<promise>FAIL</promise>
```

## Key Rules

- The reflected_message ALWAYS includes: literal output, diagnosed root cause (file:line:function), concrete fix.
- If the same error repeats twice → fix is not working; change approach completely before attempt 3.
- Forced-enumeration is non-negotiable on attempt 2 — same sampling distribution otherwise produces the same result.
