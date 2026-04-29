# Getting Started — Agent007 v5.1

> Este plugin convierte Claude Code en un sistema autónomo de desarrollo de software con 8 agentes expertos, 34+ skills y 22 hooks de calidad.

---

## ¿Qué puedes hacer?

| Necesito... | Comando |
|---|---|
| Implementar algo (bug, feature, refactor) | `/dev "descripción"` |
| Consejo experto antes de implementar | `/consult "pregunta"` |
| Iterar autónomamente hasta que funcione | `/dev "tarea" --ralph` |
| Convertir una idea vaga en un prompt preciso | `/prompt-gen "objetivo"` |

---

## Primer task — 5 minutos

### 1. Consulta simple

```
/consult "¿Cómo estructuro un endpoint REST con NestJS y TypeORM?"
```

Verás: routing automático al agente correcto → respuesta experta con code examples.

### 2. Fix de bug directo

```
/dev "Fix el error 500 en POST /users cuando email ya existe" --simple
```

Verás: routing → lectura de archivos relevantes → fix → verificación con evidencia.

### 3. Feature con plan

```
/dev "Agregar validación de email con resend en el registro de usuario"
```

Verás: routing → plan de tareas → subagentes implementan por tarea → review → cierre.

---

## Árbol de decisión: ¿qué comando uso?

```
¿Tengo código que implementar?
  ├─ Sí, es un bug o cambio de 1 archivo       → /dev "..." --simple
  ├─ Sí, es una feature clara                   → /dev "..."
  ├─ Sí, es complejo / arquitectura             → /dev "..." --full
  └─ Sí, quiero que itere solo hasta lograrlo   → /dev "..." --ralph --max-iterations 20

¿Necesito consejo antes de implementar?
  ├─ Respuesta rápida                            → /consult "..." --quick
  ├─ Análisis con trade-offs                     → /consult "..."
  └─ Decisión de arquitectura                    → /consult "..." --deep

¿Tengo una idea vaga que quiero convertir en prompt?
  └─ /prompt-gen "objetivo vago"
     → conduce entrevista de calidad
     → genera prompt de precisión quirúrgica
```

---

## Setup inicial

### Prerrequisitos

- Node.js ≥ 18 (para hooks `.js`)
- Python 3.9+ (para hooks `.py`)
- Claude Code CLI instalado

### Antes de tu primera tarea — llenar contexto del proyecto

El plugin necesita conocer tu stack para dar respuestas precisas. Edita estos dos archivos:

**`.sdlc/context/tech-stack.md`** — tu stack actual:
```markdown
# Tech Stack
- Runtime: Node.js 20 / Python 3.11 / etc.
- Framework: NestJS / Next.js / FastAPI / etc.
- Database: PostgreSQL / MongoDB / etc.
- ORM: TypeORM / Prisma / etc.
- Testing: Jest / Vitest / Pytest / etc.
```

**`.sdlc/context/conventions.md`** — convenciones de tu equipo:
```markdown
# Conventions
- Commit format: conventional commits
- Branch naming: feat/, fix/, refactor/
- API style: REST / GraphQL
- Error handling: ...
```

### Verificar que los hooks funcionan

Al iniciar una nueva sesión de Claude Code, deberías ver en el banner:
```
Agent007 v5.1 | 35 skills | 10 agents | branch: main | RTK: ✓ | Task: none
```

Si no aparece, verifica que Node.js y Python3 están disponibles en tu PATH.

---

## Cómo sabe el agente cuándo terminó

El sistema tiene **5 checkpoints** donde tú decides si continuar:

```
[CP 0] Routing: te muestra qué camino elegirá → puedes cancelar
[CP 1] Plan: te muestra las tareas antes de implementar → puedes editar
[CP 2] Review por tarea: cada tarea pasa por spec + quality review
[CP 3] Branch finish: elige entre merge / PR / mantener / descartar
[CP auto] Stop hook: bloquea al agente si intenta terminar sin completar
```

---

## Flujos comunes

### Bug rápido
```bash
/dev "Fix error 500 en POST /payments cuando amount es 0" --simple
```

### Feature con rama aislada
```bash
/dev "Implementar módulo de notificaciones push" --full --ralph --max-iterations 25
```

### Decisión de arquitectura
```bash
/consult "¿Monorepo Nx o repos separados para 3 microservicios con DTOs compartidos?" --deep --experts backend
```

### Landing page premium con GSAP
```bash
/dev "Crear landing page para producto SaaS con animaciones GSAP nivel producción" --full
```

### Auditoría de seguridad
```bash
/consult "Revisa el módulo de auth en src/auth/ para vulnerabilidades OWASP" --experts security
```

---

## Si algo no funciona

1. **El banner no aparece al iniciar** → Node.js no está en PATH o hay un error en `welcome.py`
2. **El agente no usa el agente correcto** → agrega keywords del dominio a tu pregunta
3. **Los hooks bloquean un comando que debería ser seguro** → revisa `hooks/safety-guard.py` y ajusta las reglas
4. **El ralph-loop no termina** → agrega `--max-iterations 10` y `--verify "npm test"` para acotar

---

## Documentación adicional

| Archivo | Contenido |
|---|---|
| `.claude/CLAUDE.md` | Instrucciones internas del orquestador (fuente de verdad del sistema) |
| `.claude/README.md` | Referencia completa de comandos, agentes y hooks |
| `.sdlc/context/improvement-plan.md` | Plan de mejoras pendientes (Grupo A y B) |
| `.sdlc/context/prompt-improvements.md` | Frases de calidad de Bolt/Cursor/v0/Windsurf para implementar |
