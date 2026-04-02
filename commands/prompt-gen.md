---
name: prompt-gen
version: 3.0.0
description: "Convierte intención vaga del usuario en un prompt de precisión quirúrgica. Conduce entrevista de calidad antes de generar. Prioriza siempre: investigar → planificar → construir. El resultado que busca el usuario siempre importa más que la velocidad de entrega."
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

## Step 4 — Construir el prompt (10 componentes)

### Componente 1: Identity
Primera línea, prosa directa, fuera de XML. Stack real + proyecto específico.

```
❌ "You are an expert developer."
✅ "Eres un frontend engineer especializado en Next.js 14 + GSAP 3 + Tailwind,
   construyendo una landing page premium para AirPods Pro.
   El nivel de referencia es apple.com/airpods-pro."
```

### Componente 2: `<task_context>`
Decisiones ya tomadas + razones. El agente no debe re-evaluar lo que ya se decidió.

```xml
<task_context>
  <referente>[URL o descripción del nivel de calidad objetivo]</referente>
  <stack>[tecnologías reales]</stack>
  <decisions>
    - [decisión 1]: [razón]
    - [decisión 2]: [razón]
  </decisions>
  <anti_fail>[qué haría que el resultado sea inaceptable — de la entrevista]</anti_fail>
</task_context>
```

### Componente 3: `<constraints>`
Cada constraint incluye la razón. Sin razón el agente no puede generalizar a edge cases.

```xml
<constraints>
  <constraint>
    <rule>Investigar antes de implementar</rule>
    <reason>Un agente que construye sin contexto produce resultados promedio.
    La investigación define la diferencia entre 'funciona' y 'impresiona'.</reason>
  </constraint>
  <constraint>
    <rule>Velocidad de entrega NO es criterio de éxito</rule>
    <reason>El usuario prefiere un resultado excepcional que tarda más
    sobre uno mediocre que termina rápido.</reason>
  </constraint>
  <!-- constraints técnicos específicos del proyecto -->
</constraints>
```

### Componente 4: `<behavioral_guidelines>`

| Tipo de tarea | Guideline |
|---------------|-----------|
| Implementación visual | "Si el resultado se ve genérico, iterar hasta que se vea premium. No declarar done por completar tareas técnicas." |
| Implementación técnica | "Leer antes de editar. Verificar con comando antes de afirmar. Commit después de cada tarea." |
| Code review | "Cada hallazgo: archivo + línea + evidencia + severidad + fix concreto." |
| Debugging | "Reproducir primero. Nunca proponer fix sin reproducción." |

### Componente 5: `<task_specific_instructions>`
Fases en modo imperativo con criterios de completitud verificables.

**Verbos obligatorios**: Investiga / Documenta / Implementa / Verifica / Itera

| ❌ Rechazar | ✅ Usar |
|------------|---------|
| "considera implementar" | "Implementa" |
| "podrías agregar" | "Agrega" |
| "sería bueno" | "Crea" |
| "se recomienda" | "Aplica" |
| "intenta hacer" | "Ejecuta" |

### Componentes 6-10
`<output_format>` / `<examples>` / `<thinking>` / `{{variables}}` / `<meta_instructions>`

Ver v2.0.0 para referencia de estos componentes — sin cambios en v3.

---

## Step 5 — Output según target

### `--target dev` (default) — ≤400 palabras

```
/dev "[objetivo concreto en modo imperativo — con nivel de calidad explícito]"

[Identity: una oración prosa con stack + referente de calidad]

<context>
  <referente>[URL o descripción]</referente>
  <stack>[tecnologías]</stack>
  <anti_fail>[qué haría que el resultado sea inaceptable]</anti_fail>
  <decisions>
    - [decisión]: [razón]
  </decisions>
</context>

<constraints>
  - Investigar antes de implementar — porque sin contexto el resultado es promedio
  - Velocidad NO es criterio — calidad sí
  - [constraints técnicos con razones]
</constraints>

<phases>
  FASE 0 — INVESTIGACIÓN: [qué investigar, dónde, qué documentar]
  FASE 1 — IMPLEMENTACIÓN: [fases concretas con verificación]
  FASE FINAL — QUALITY GATE: [criterios técnicos + criterios visuales si Premium]
</phases>

<success_criteria>
  Técnico:
  - [comando]: exit 0
  Visual (si Premium):
  - [pregunta de quality self-check 1]
  - [pregunta de quality self-check 2]
</success_criteria>

[quality_modifier según tier]
```

### `--target subagent` y `--target session`
XML completo con los 10 componentes. Todas las secciones dinámicas con `{{variables}}`.

---

## Step 6 — Guardar (`--save`)

```
Guardado en: .claude/prompts/<intent-slug>-YYYYMMDD.md
```

Incluye: metadata + entrevista de calidad + prompt generado completo.

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
