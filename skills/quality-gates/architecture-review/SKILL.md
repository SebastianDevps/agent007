---
name: architecture-review
description: "Deep architecture review: DRY violations, testing gaps, edge cases, performance. Interactive 4-section process (Architecture → Code Quality → Testing → Performance) with 2-3 options per issue."
invokable: true
accepts_args: scope
auto-activate: false
required-before: Major refactoring or architecture changes
version: 1.0.0
when:
  - user_mentions: ["architecture review", "deep review", "code quality review"]
  - user_invokes: "/architecture-review"
---

# Architecture Review - Deep Code & Design Analysis

**SCOPE**: Comprehensive architecture, code quality, testing, and performance review.
**NOT** for task decomposition (use `/plan` for that) or quick code review (use `/review` for that).

This skill provides an interactive, thorough review process with explicit trade-offs and user decision points.

---

## Preferencias de Ingeniería

- **DRY** (Don't Repeat Yourself) es importante: identificar la repetición de forma agresiva.
- El **código bien probado** no es negociable; prefiero tener demasiadas pruebas antes que muy pocas.
- El código debe estar **suficientemente diseñado** — no sub-diseñado (frágil, *hacky*) y no sobre-diseñado (abstracción prematura, complejidad innecesaria).
- Preferencia por **manejar más casos límite**, no menos; la consideración prima sobre la velocidad.
- Preferencia por lo **explícito** sobre lo ingenioso.

---

## Secciones de Revisión

### 1. Revisión de Arquitectura

- Diseño general del sistema y límites de componentes.
- Grafo de dependencias y preocupaciones de acoplamiento.
- Patrones de flujo de datos y posibles cuellos de botella.
- Características de escalado y puntos únicos de fallo.
- Arquitectura de seguridad (autenticación, acceso a datos, límites de API).

### 2. Revisión de Calidad del Código

- Organización del código y estructura de módulos.
- Violaciones de DRY (ser agresivo aquí).
- Patrones de manejo de errores y casos límite faltantes (especificarlos explícitamente).
- Puntos críticos de deuda técnica.
- Áreas que están sobre-diseñadas o sub-diseñadas en relación con las preferencias del usuario.

### 3. Revisión de Pruebas

- Brechas en la cobertura de pruebas (unidad, integración, e2e).
- Calidad de las pruebas y fuerza de las aserciones.
- Cobertura de casos límite faltantes (ser exhaustivo).
- Modos de fallo y rutas de error no probados.

### 4. Revisión de Rendimiento

- Consultas N+1 y patrones de acceso a la base de datos.
- Preocupaciones sobre el uso de memoria.
- Oportunidades de *caching*.
- Rutas de código lentas o de alta complejidad.

---

## Para cada problema encontrado

Para cada problema específico (bug, *smell*, preocupación de diseño o riesgo):

1. Describir el problema de forma concreta, con referencias a archivos y líneas.
2. Presentar **2-3 opciones**, incluyendo "no hacer nada" cuando sea razonable.
3. Para cada opción, especificar: esfuerzo de implementación, riesgo, impacto en otro código y carga de mantenimiento.
4. Dar la **opción recomendada** y por qué, mapeada a las preferencias del usuario mencionadas anteriormente.
5. Preguntar explícitamente si el usuario está de acuerdo o si desea elegir una dirección diferente **antes de continuar**.

---

## Flujo de Trabajo

- No asumir las prioridades del usuario en cuanto a plazos o escala.
- Después de cada sección, **pausar y pedir retroalimentación** del usuario antes de continuar.

---

## ANTES DE EMPEZAR

Preguntar al usuario qué opción prefiere:

**1/ CAMBIO GRANDE:** Trabajar de forma interactiva, una sección a la vez (Arquitectura → Calidad del Código → Pruebas → Rendimiento) con un **máximo de 4 problemas principales** en cada sección.

**2/ CAMBIO PEQUEÑO:** Trabajar de forma interactiva **UNA pregunta por sección** de revisión.

---

## PARA CADA ETAPA DE REVISIÓN

- Mostrar la explicación y los pros y contras de las preguntas de cada etapa **y** su recomendación fundamentada y por qué.
- Usar `AskUserQuestion` (o equivalente: preguntar explícitamente y esperar respuesta).
- **NUMERAR** los problemas y dar **LETRAS** para las opciones.
- Al usar `AskUserQuestion`, asegurarse de que cada opción etiquete claramente el **NÚMERO** del problema y la **LETRA** de la opción para que el usuario no se confunda.
- La **opción recomendada** debe ser siempre la **1ª opción**.

---

## Diferenciación de Otros Skills

- **vs `/plan`**: `/plan` descompone features en tareas de 2-5 minutos. Este skill hace revisión profunda de arquitectura.
- **vs `/review`**: `/review` es para NestJS + TypeORM code review. Este skill es más amplio (arquitectura, testing, performance).
- **vs `/systematic-debugging`**: Ese skill es para bugs (4 fases). Este es para revisión preventiva de diseño.

---

## Ejemplo de Salida Esperada

### Problema 1: Violación DRY en validación de usuarios

**Archivos afectados:**
- `src/users/users.controller.ts:45-52`
- `src/auth/auth.controller.ts:78-85`

**Opciones:**

**A. (Recomendada) Extraer a un validador compartido**
- Esfuerzo: 30 min
- Riesgo: Bajo
- Impacto: 2 archivos, + 1 nuevo archivo utils
- Mantenimiento: Mejora significativa (single source of truth)

**B. Dejar como está**
- Esfuerzo: 0
- Riesgo: Alto (divergencia futura)
- Impacto: Ninguno
- Mantenimiento: Duplicación continua

**C. Usar decorador de class-validator personalizado**
- Esfuerzo: 1 hora
- Riesgo: Medio (nueva abstracción)
- Impacto: 3 archivos
- Mantenimiento: Abstracción adicional

**¿Qué opción prefieres para el Problema 1?**
