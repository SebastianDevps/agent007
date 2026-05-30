---
name: prompt-gen
version: 4.0.0
description: "Convierte intención vaga en un prompt-spec XML canónico (canonical XML conventions). Persiste en .sdlc/state/active-prompt.json para que subagent-context.py lo inyecte a cada delegación. Prioriza investigar → planificar → construir."
accepts_args: true
---

# /prompt-gen — Generador de Prompts de Precisión

**Invocación**:
```
/prompt-gen "[objetivo vago o preciso]"
/prompt-gen "[objetivo]" --target dev|subagent|session
/prompt-gen "[objetivo]" --save
/prompt-gen "[objetivo]" --improve   ← audita y mejora un prompt existente
/prompt-gen "[objetivo]" --quick     ← salta entrevista si el contexto ya es claro
```

---

## Filosofía central

Un prompt vago produce resultado mediocre. Un prompt preciso produce resultado que impresiona.

La mayoría de usuarios saben QUÉ quieren pero no saben cómo expresarlo con suficiente precisión para que el modelo lo entienda. Este skill hace la traducción — pero para traducir bien, primero hay que entender completamente.

**Principio cardinal**: velocidad de entrega nunca es un criterio de éxito. El agente que genera el resultado debe investigar primero, planificar segundo, construir tercero. Un resultado mediocre que termina rápido es un fracaso.

---

## Step 0 — Routing de entrada

| Fuente | Señal | Acción |
|--------|-------|--------|
| `/consult` reciente | Conversación previa con agente experto | Step 1A — extraer decisiones |
| `--improve` flag | Usuario pega prompt existente | Step 1B — auditar vs checklist |
| Intención directa | Usuario describe lo que quiere | Step 1C — entrevista de calidad |

---

## Step 1C — Entrevista de Calidad (el paso más importante)

Antes de generar cualquier prompt, entender completamente qué busca el usuario.

Conducir la entrevista en **máximo 5 preguntas**, una a la vez. Parar cuando el contexto sea suficiente. Las preguntas no son formulario — son diagnóstico.

### Pregunta 1 — El objetivo real
Reformular lo que el usuario dijo en términos de resultado, no de tarea:
```
Entiendo que quieres [X]. ¿El resultado exitoso es un producto que funciona,
o un producto que impresiona? ¿Cuál es la diferencia para ti en este caso?
```

### Pregunta 2 — El referente de calidad (crítica)
```
¿Hay algún sitio web, app, demo, o producto que diga
'quiero algo así de bueno o mejor'? (URL, nombre, empresa)

Si no tienes uno específico: ¿Apple.com nivel / Awwwards nivel / funcional pero simple?
```

La respuesta a esta pregunta determina el Quality Tier:
- Sin referente, funcional → **Standard**
- Referente nombrado pero genérico → **Thorough**
- URL concreta o "nivel Apple / Awwwards / GSAP demos" → **Premium**

### Pregunta 3 — El anti-fail
```
¿Qué haría que al ver el resultado digas 'esto no sirve, es mediocre'?
¿Qué sería inaceptable?
```

Esta pregunta extrae los criterios de calidad reales que el usuario NO suele escribir en el prompt inicial.

### Pregunta 4 — Constrainsts existentes
```
¿Hay decisiones ya tomadas que el agente NO debe re-evaluar?
(stack, diseño, arquitectura, dependencias, tiempo, presupuesto)
```

### Pregunta 5 — Verificación (solo si el contexto aún es ambiguo)
```
¿Cómo sabrás que el resultado está completo?
¿Hay un comando, una pantalla, o un comportamiento concreto que lo confirme?
```

### Señales de que ya hay suficiente contexto (parar antes de las 5)
- El referente de calidad es claro y concreto
- El anti-fail está definido
- El stack y restricciones son conocidos
- Los criterios de completitud son verificables

---

## Step 1A — Extraer contexto del /consult

```xml
<consult_context>
  <expert>[agente: backend-db-expert | security-expert | frontend-ux-expert | etc.]</expert>
  <original_question>[pregunta original del usuario]</original_question>
  <key_decisions>
    <!-- decisión + razón del experto — nunca solo la regla sin el por qué -->
  </key_decisions>
  <stack>[tecnologías reales identificadas]</stack>
  <trade_offs>[compromisos aceptados explícitamente]</trade_offs>
  <open_questions>[lo que depende de contexto adicional]</open_questions>
  <quality_bar>[nivel de calidad definido por el experto o el usuario]</quality_bar>
</consult_context>
```

---

## Step 1B — Auditar prompt existente (`--improve`)

Evaluar contra los criterios de calidad:

| Criterio | OK | Problema |
|----------|----|---------|
| Tiene fase de investigación antes de construir | ✅ | ❌ va directo a implementar |
| Referente de calidad especificado | ✅ | ❌ criterios solo técnicos |
| Anti-mediocrity guardrail presente | ✅ | ❌ "termina y listo" implícito |
| Identity específico con stack real | ✅ | ❌ genérico |
| Cada constraint tiene razón | ✅ | ❌ reglas sin por qué |
| Success criteria son visuales + técnicos | ✅ | ❌ solo build/lint |
| Self-review de calidad incluido | ✅ | ❌ ausente |
| Verbos imperativos (no "considera", "podrías") | ✅ | ❌ lenguaje suave |

Producir: lista de problemas + versión mejorada.

---

## Step 2 — Quality Tier

Auto-detectar basado en la entrevista. Mostrar antes de generar:

```
🎯 prompt-gen → [TARGET] | Tier: [QUALITY] | Referente: [URL o descripción] | Stack: [tech]
```

| Tier | Señal | Lo que se agrega al prompt |
|------|-------|---------------------------|
| **Minimal** | Tarea técnica simple, un archivo, sin estética | Sin modificador visual |
| **Standard** | Feature nueva, múltiples archivos | "Produce a complete, production-ready solution." |
| **Thorough** | Arquitectura, seguridad, multi-módulo | "Go beyond the basics. Cover edge cases and observability. A senior engineer will review this." |
| **Premium** | Referente visual concreto (Apple, Awwwards, GSAP demos) | Ver sección Premium Quality Modifier abajo |

### Premium Quality Modifier

Cuando el tier es Premium, agregar obligatoriamente al prompt generado:

```
<quality_standard>
  Referente: [URL o descripción del referente]

  El resultado debe alcanzar o superar el nivel visual/funcional de ese referente.
  Un resultado que compila pero se ve mediocre es un FAIL — no un resultado incompleto, un FAIL.

  Antes de escribir código: investigar el referente con WebFetch/WebSearch.
  Documentar en RESEARCH.md qué hace que ese referente sea excepcional y qué técnicas específicas usarás.
  No avanzar a implementación sin RESEARCH.md escrito.

  Quality self-check obligatorio antes de declarar COMPLETE:
  Responder honestamente estas preguntas:
  - ¿El resultado se compara favorablemente con el referente?
  - ¿Hay algo que claramente se podría mejorar con 30 minutos más de trabajo?
  - ¿Le mostrarías esto a un cliente sin disculparte primero?

  Si alguna respuesta es negativa: iterar antes de COMPLETE.
</quality_standard>
```

---

## Step 3 — Principio Investigar → Planificar → Construir

Todo prompt de complejidad Standard o mayor debe incluir explícitamente estas fases en orden. Nunca saltarse la investigación ni la planificación:

```
FASE 0 — INVESTIGACIÓN (obligatoria, no saltear)
  Antes de escribir código:
  - [Qué investigar: referencias, docs, codebase existente, APIs]
  - Documentar hallazgos en [archivo]
  - No avanzar hasta completar esta fase

FASE 1 — PLANIFICACIÓN
  Con los hallazgos de FASE 0:
  - Definir estructura de archivos y componentes
  - Identificar dependencias entre tareas
  - Documentar decisiones de implementación

FASE 2+ — IMPLEMENTACIÓN
  Ejecutar plan. Por cada tarea:
  - Implementar
  - Verificar con comando: [cmd]
  - Si falla: el output del error es el input del siguiente intento (no retry genérico)

FASE FINAL — QUALITY GATE
  [Para Premium: self-check de calidad visual]
  [Para todos: build + lint + criterios técnicos]
  Si algo no pasa: diagnosticar, corregir, re-verificar. No declarar done sin evidencia.
```

**Regla de hierro**: si el prompt no tiene fase de investigación, está incompleto. Un agente que construye sin investigar primero produce resultados promedio.

---

## Step 4 — Construir el prompt (5 componentes canónicos)

> Convergimos al set canónico de [canonical XML conventions](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags). Antes había 10 componentes parcialmente solapados — ahora 5 + 2 opcionales.

### 1. `<identity>` (obligatorio)
Una línea prosa: rol + stack + referente de calidad.

```xml
<identity>Frontend engineer en Next.js 14 + GSAP 3, construyendo landing AirPods Pro nivel apple.com/airpods-pro.</identity>
```

### 2. `<context>` (obligatorio)
Reemplaza `task_context` viejo. Incluye decisiones ya tomadas, stack, anti-fail, y `<task_input>$ARGUMENTS</task_input>` literal.

```xml
<context>
  <referente url="...">Nivel objetivo</referente>
  <stack>...</stack>
  <decisions>
    <decision reason="...">...</decision>
  </decisions>
  <anti_fail>Qué haría inaceptable el resultado</anti_fail>
  <task_input>$ARGUMENTS</task_input>
</context>
```

### 3. `<constraints>` (obligatorio)
Cada constraint con `reason=`. Verbos imperativos. Anti-patterns a enforzar (Code Sovereignty + Stop-Loss del repo `affaan-m/everything-claude-code`):

```xml
<constraints>
  <constraint reason="Sin contexto el resultado es promedio">Investigar antes de implementar</constraint>
  <constraint reason="Calidad sobre velocidad">Velocidad NO es criterio de éxito</constraint>
  <constraint reason="Code Sovereignty — el spec define el scope">Nunca tocar archivos fuera de los listados en <phases></constraint>
  <constraint reason="Self-check sin evidencia es teatro">Cada item de visual debe tener output o screenshot, no solo "sí"</constraint>
</constraints>
```

### 4. `<phases>` (obligatorio)
Fases con `gate=` verificable. Verbos imperativos: **Investiga / Documenta / Implementa / Verifica / Itera**.

```xml
<phases>
  <phase id="0" name="Investigación" gate="RESEARCH.md escrito">...</phase>
  <phase id="1" name="Planificación" gate="PLAN.md con archivos y dependencias">...</phase>
  <phase id="2" name="Implementación" gate="cmd: pnpm test → exit 0">...</phase>
  <phase id="final" name="Quality Gate" gate="self-check completo con evidencia">...</phase>
</phases>
```

### 5. `<success_criteria>` (obligatorio)
Técnico (con `cmd=`) + visual (preguntas auto-evaluables).

```xml
<success_criteria>
  <technical><check cmd="pnpm build">exit 0</check></technical>
  <visual>
    <check>¿El resultado se compara favorablemente con [referente]?</check>
    <check>¿Hay algo que con 30min más se podría mejorar?</check>
  </visual>
</success_criteria>
```

### 6. `<example>` (opcional, recomendado para tier Premium)
Se recomienda 1-3 ejemplos input→ideal_output dentro del prompt.

### 7. `<self_check>` (opcional pero crítico en Premium)
Verbos: "Considera / Evalúa / Razona a través de" — **NO usar "think"** (Opus 4.7+ con extended thinking off).

```xml
<self_check>
  Antes de declarar COMPLETE: responder honestamente las preguntas en <visual>.
  Si alguna es negativa: iterar. Considera el resultado contra el referente.
</self_check>
```

**Verbos rechazados** (mismo set que v3): "considera implementar" / "podrías" / "sería bueno" / "se recomienda" / "intenta" → reemplazar por imperativos directos.

---

## Step 5 — Output: envelope `<prompt_spec>` canónico

**Una sola plantilla**. Solo cambian `<phases>` y `<task_input>` según target.

```xml
<prompt_spec version="4" target="dev|subagent|session" tier="minimal|standard|thorough|premium">
  <identity>...</identity>

  <context>
    <referente url="...">...</referente>
    <stack>...</stack>
    <decisions>
      <decision reason="...">...</decision>
    </decisions>
    <anti_fail>...</anti_fail>
    <task_input>$ARGUMENTS</task_input>
  </context>

  <constraints>
    <constraint reason="...">...</constraint>
  </constraints>

  <phases>
    <phase id="0" name="Investigación" gate="...">...</phase>
    <phase id="1" name="Planificación" gate="...">...</phase>
    <phase id="2" name="Implementación" gate="...">...</phase>
    <phase id="final" name="Quality Gate" gate="self-check">...</phase>
  </phases>

  <success_criteria>
    <technical><check cmd="...">exit 0</check></technical>
    <visual>
      <check>...</check>
    </visual>
  </success_criteria>

  <self_check>...</self_check>

  <example>
    <input>...</input>
    <ideal_output>...</ideal_output>
  </example>
</prompt_spec>
```

**Diferencia por target**:
- `dev`: prefijo `/dev "..."` antes del envelope, `<task_input>` con el objetivo concreto
- `subagent`: `<task_input>` describe la tarea delegada al subagent
- `session`: `<task_input>` es el goal de toda la sesión

---

## Step 6 — Persistir + guardar opcional

**Persistencia automática (siempre, no flag)**: tras generar el spec, escribir a `.sdlc/state/active-prompt.json` con `os.replace()` atómico:

```json
{
  "version": 4,
  "generated_at": "<ISO 8601 UTC>",
  "target": "dev|subagent|session",
  "tier": "minimal|standard|thorough|premium",
  "intent_slug": "<short slug>",
  "spec_xml": "<prompt_spec ...>...</prompt_spec>",
  "summary_oneline": "<una oración del goal>",
  "ttl_seconds": 7200
}
```

`subagent-context.py` lee este archivo y lo inyecta a cada subagente delegado. TTL 2h: pasado eso, el hook lo ignora (no contamina sesiones futuras).

**`--save` (opcional)**: además de la persistencia state, guarda el `.md` legible en `.claude/prompts/<intent-slug>-YYYYMMDD.md` con metadata + entrevista + spec completo.

---

## Checklist de calidad pre-entrega

```
✓ Entrevista de calidad completada — referente y anti-fail definidos
✓ Tier correcto detectado (Minimal / Standard / Thorough / Premium)
✓ Fase de investigación incluida en el prompt (siempre, salvo Minimal)
✓ Fase de planificación incluida (Standard o mayor)
✓ Quality gate incluido — criterios técnicos + visuales según tier
✓ Anti-mediocrity guardrail explícito en Premium
✓ Identity con stack real y referente de calidad
✓ Constraints con razones — no solo reglas
✓ Verbos imperativos — sin "considera", "podrías", "sería bueno"
✓ Success criteria verificables con evidencia real (comandos / visual checklist)
✓ Self-check como fase final obligatoria
✓ "Velocidad no es criterio" explícito en Premium y Thorough
✓ Sin prefill en assistant turn
✓ Documentos largos antes de instrucciones específicas
✓ Tags XML del set canónico (identity/context/constraints/phases/success_criteria)
✓ <task_input>$ARGUMENTS</task_input> presente
✓ Persistido en .sdlc/state/active-prompt.json (atomic write)
✓ NO usar palabra "think" — usar "considera/evalúa/razona"
```

---

## Auto-activación

Al final de cada `/consult` con recomendaciones técnicas, ofrecer:
```
💡 ¿Convertir estas decisiones en prompt ejecutable?
   /prompt-gen "[objetivo]" para generar instrucción precisa para /dev
```

Cuando el usuario describe algo vagamente ("quiero una landing chida", "hazme un dashboard"):
```
Antes de generar el prompt necesito entender el nivel de calidad que buscas.
[Pregunta 1 de la entrevista]
```

**Target por defecto**: `--target dev`
**Directorio de prompts guardados**: `.claude/prompts/`
