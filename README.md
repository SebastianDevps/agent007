# Agent007 v5 — Manual de Uso

> Ecosistema autónomo de desarrollo AI. 8 agentes expertos · 34+ skills activas · 29 hooks · 10 primitivas OpenClaw · 3 comandos de entrada.

---

## Los 3 comandos de entrada

### `/dev "tarea"` — Comando maestro

Clasifica la tarea automáticamente y elige el camino óptimo:

```
Simple  → implementa directo → verifica → done
Medium  → plan → subagentes con review → cierre de branch
Complex → brainstorming → worktree → plan → subagentes + ralph → cierre
```

**Flags disponibles:**

| Flag | Efecto |
|---|---|
| `--simple` | Fuerza implementación directa, sin pipeline |
| `--full` | Fuerza pipeline completo (brainstorm → worktree → plan → subagents) |
| `--ralph` | Activa el ralph loop en cada iteración |
| `--max-iterations N` | Límite de iteraciones (default 20, max 50) |
| `--verify "cmd"` | Comando de verificación personalizado para ralph |
| `--no-review` | Salta reviews (solo prototipos) |

**Ejemplos:**

```bash
# Bug simple → directo, sin pipeline
/dev "Fix null pointer en UserService.findById()"

# Feature nueva → genera plan, despacha subagentes por tarea
/dev "Agregar paginación cursor-based al endpoint /users"

# Feature compleja → pipeline completo
/dev "Implementar módulo de auth JWT + refresh tokens" --full

# Autónomo hasta que tests pasen
/dev "Implementar sistema de notificaciones" --full --ralph --max-iterations 30 --verify "npm test"
```

---

### `/consult "pregunta"` — Consulta experta

Auto-selecciona el agente por keywords y responde desde su perspectiva especializada.

**Mapeo keywords → agente:**

| Keywords | Agente |
|---|---|
| api, nestjs, database, query, typeorm, cache, schema, microservice, resilience | backend-db-expert |
| auth, jwt, owasp, vulnerability, cors, xss, injection, encryption | security-expert |
| react, next, component, tailwind, ux, form, accessibility, gsap, animation | frontend-ux-expert |
| docker, ci/cd, test, tdd, coverage, kubernetes, deploy, pipeline | platform-expert |
| roadmap, mvp, backlog, user story, rice, prioritize | product-expert |

**Flags:**

| Flag | Cuándo |
|---|---|
| `--quick` | Respuesta directa, sin trade-offs |
| default | Recomendación con análisis (~60 líneas) |
| `--deep` | Arquitectura, decisiones complejas (~120 líneas) |
| `--experts X,Y` | Dos opiniones independientes |

**Ejemplos:**

```bash
/consult "¿Cómo implemento circuit breaker en NestJS?" --quick
/consult "¿Cursor-based o offset pagination para 10M registros?" --deep
/consult "¿JWT stateless vs sessions con Redis?" --experts backend,security
```

---

### `/ralph-loop "tarea"` — Loop autónomo hasta completar

Itera hasta detectar `<promise>COMPLETE</promise>`. El Stop hook bloquea salidas prematuras e inyecta continuación automáticamente.

```bash
/ralph-loop "Implementar herramienta de gestión de proyectos"

Requisitos:
- Aplicación Next.js + Tailwind con localStorage
- Tablero Kanban (columnas: Todo / In Progress / Done)
- Sin errores de linter

Criterios de éxito:
- npm test pasa
- Sin errores de TypeScript

--max-iterations 30 --verify "npm test"
```

---

## Lifecycle completo de desarrollo

Hay **5 checkpoints** donde tú decides. Nada avanza sin tu aprobación.

```
[CP 0] Clasificación automática → muestra routing antes de actuar
         ↓
[CP 1] Plan de tareas generado → lo lees y apruebas antes de implementar
         ↓
[CP 2] Review por tarea (spec compliance + code quality) → subagente corrige si falla
         ↓
[CP 3] Branch finish → 4 opciones: merge / push+PR / keep / discard
         ↓
[CP implícito] Stop hook → verifica completitud real antes de permitir salir
```

---

## Los 8 agentes expertos

| Agente | Modelo | Dominio |
|---|---|---|
| `backend-db-expert` | opus | APIs, NestJS, TypeORM, PostgreSQL, Redis, microservicios, queries, schema |
| `frontend-ux-expert` | sonnet | React, Next.js 14, Tailwind, GSAP, animaciones, TanStack Query, WCAG, Core Web Vitals |
| `platform-expert` | sonnet | CI/CD, GitHub Actions, Docker, Jest, Playwright, Kubernetes, monitoring |
| `product-expert` | opus | RICE/ICE, user stories, roadmap, AARRR, MVP scoping, product discovery |
| `security-expert` | opus | OWASP Top 10, JWT, threat modeling, GDPR, SOC2, penetration testing |
| `code-reviewer` | sonnet | Revisión de calidad general con taxonomía CRITICAL/HIGH/MEDIUM/LOW |
| `loop-operator` | sonnet | Gestión del ralph-loop, stall detection, cost drift monitoring |
| `refactor-cleaner` | sonnet | Dead code detection, batch removal, safe refactoring |

---

## Skills de pipeline (invocados por /dev)

| Skill | Propósito |
|---|---|
| `plan` | Descompone en sub-tareas de 2-5 min con rutas exactas y TDD steps |
| `generate` | Implementación con TDD cycle: RED → GREEN → REFACTOR |
| `verify` | Gate mandatorio antes de cualquier claim de "done" (evidencia requerida) |
| `brainstorming` | Preguntas socráticas una a la vez para clarificar requisitos ambiguos |
| `subagent-driven-development` | Despacha subagente experto por tarea con wave execution |
| `using-git-worktrees` | Crea rama aislada `feat/<nombre>` en `.worktrees/` |
| `finishing-a-development-branch` | Tests + 4 opciones: merge / push+PR / mantener / descartar |
| `reverse-engineer` | Ingeniería inversa de código existente → escenarios para refactors seguros |

---

## Hooks activos (22 total)

Los hooks garantizan calidad a nivel de herramienta, no de instrucción.

| Hook | Evento | Qué hace |
|---|---|---|
| `welcome.py` | SessionStart | Banner de estado: versión, skills, agentes, branch, tarea activa |
| `memory-check.py` | SessionStart | Detecta cambios en manifests via stat+MD5 |
| `safety-guard.py` | PreToolUse (Bash) | Bloquea comandos destructivos (rm -rf, force push, DROP TABLE) |
| `sdd-guard.py` | PreToolUse/PostToolUse (Edit/Write) | Bloquea reward-hacking (edits que reducen assertions) |
| `context-engine.py` | PreToolUse + Stop | Proactive context budget antes de cada Agent spawn |
| `rtk-rewrite.py` | PreToolUse (Bash) | Comprime comandos para ahorrar tokens (~40% reducción) |
| `format-on-save.py` | PostToolUse (Edit/Write) | Prettier automático en .ts .tsx .js .jsx .json .css .md |
| `tool-loop-detection.py` | PostToolUse | Detecta loops repetitivos, circuit breaker a 30× |

---

## Técnicas de ahorro de tokens

| Comando | Tokens aprox | Cuándo |
|---|---|---|
| `/consult --quick` | ~2K | Respuesta directa |
| `/consult` | ~5K | Análisis con trade-offs |
| `/consult --deep` | ~10K | Decisiones de arquitectura |
| `/dev --simple` | ~3-8K | Bug, cambio de 1 archivo |
| `/dev` medium | ~15-40K | Feature clara, 3-6 tasks |
| `/dev --full` | ~40-80K | Feature compleja con brainstorm |

**`/compact` estratégico** — entre fases, no dentro de una:

```
✅ Después del plan, antes de implementar
✅ Entre features consecutivas
❌ A la mitad de un subagent-driven-development
```

---

## Estructura de archivos

```
.claude/
├── agents/                    # 8 agentes expertos (opus/sonnet)
│   ├── backend-db-expert.md
│   ├── frontend-ux-expert.md
│   ├── platform-expert.md
│   ├── product-expert.md
│   ├── security-expert.md
│   ├── code-reviewer.md
│   ├── loop-operator.md
│   └── refactor-cleaner.md
│
├── commands/                  # Comandos de entrada + slash commands
│   ├── dev.md
│   ├── consult.md
│   ├── prompt-gen.md
│   └── ...
│
├── skills/
│   ├── pipeline/              # plan, generate, verify, brainstorming, subagent-driven-development...
│   ├── orchestration/         # ralph-loop-wrapper, session-manager, state-sync
│   ├── workflow-utils/        # deep-research, commit, pull-request, changelog, search-first...
│   ├── quality-gates/         # systematic-debugging, architecture-review
│   ├── domain/                # gsap, react-best-practices, frontend-design, api-design-principles...
│   ├── product/               # product-discovery
│   └── devrel/                # api-documentation
│
├── hooks/                     # 22 hooks activos
│   ├── welcome.py             # SessionStart: banner de estado
│   ├── safety-guard.py        # PreToolUse: bloquea comandos destructivos
│   ├── sdd-guard.py           # PreToolUse/PostToolUse: anti-reward-hacking
│   ├── context-engine.py      # PreToolUse+Stop: proactive context budget
│   ├── rtk-rewrite.py         # PreToolUse: compresión de comandos
│   └── ...
│
├── scripts/
│   ├── agent007-init.js       # Genera banner de estado para welcome.py
│   ├── context-budget.js      # Mide uso de contexto
│   └── ...
│
├── rules/                     # Reglas de código (TypeScript, security, git-workflow, patterns)
├── scenarios/                 # Prompts de escenarios de uso (airpods-landing, etc.)
├── CLAUDE.md                  # Instrucciones del orquestador (auto-cargado) ← fuente de verdad
├── GETTING_STARTED.md         # Guía de onboarding para nuevos usuarios
├── README.md                  # Este archivo
├── settings.json              # Hooks, permisos, context includes
└── STATE.md                   # Redirect → .sdlc/state/session.md
```

---

## Persistencia entre sesiones

`.sdlc/state/session.md` se actualiza silenciosamente al completar cada tarea y al final de cada sesión.

- Si "Tarea Activa" ≠ "ninguna" → muestra banner de retomada al inicio
- Planes activos en `.sdlc/tasks/active-plan.md`
- Decisiones arquitectónicas en `.sdlc/context/`
