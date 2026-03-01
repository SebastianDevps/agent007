# Agent007 v2.0

Un equipo de desarrollo autónomo para Claude Code. 5 agentes expertos, 9 comandos/skills de workflow, y un sistema de iteración autónoma (Ralph Loop) que garantiza que la tarea termine realmente.

---

## Comandos disponibles

Hay 3 comandos de entrada principales. El resto son skills de workflow que se activan internamente (o puedes invocarlos directamente si sabes cuándo usarlos).

### Comandos de entrada

| Comando | Descripción |
|---|---|
| `/dev "tarea"` | Comando maestro. Clasifica la tarea, elige el workflow (simple/medium/complex) y ejecuta de forma autónoma. |
| `/consult "pregunta"` | Auto-selecciona el experto por keywords y responde con contexto especializado. |
| `/ralph-loop "tarea"` | Activa el loop autónomo. Itera hasta que detecta la promise de completitud. |

### Skills de workflow (invocados internamente por `/dev`)

| Skill | Cuándo se activa |
|---|---|
| `/brainstorming` | Tareas complejas con requisitos poco claros. Hace preguntas socráticas de una en una. |
| `/using-git-worktrees` | Crea rama aislada `feat/<nombre>` en `.worktrees/` antes de implementar. |
| `/writing-plans` | Descompone la tarea en sub-tareas de 2-5 min con rutas exactas y código completo. Guarda en `docs/plans/`. |
| `/subagent-driven-development` | Despacha un subagente experto por tarea. Cada tarea pasa por spec review + quality review antes de avanzar. |
| `/requesting-code-review` | Review en 2 etapas: cumplimiento de spec → calidad de código. Se corre después de cada tarea. |
| `/finishing-a-development-branch` | Cierra el branch: verifica tests y presenta 4 opciones (merge local / push+PR / mantener / descartar). |

### Skills de dominio (invocados por los agentes)

`api-design-principles` · `architecture-patterns` · `resilience-patterns` · `nestjs-code-reviewer` · `frontend-design` · `react-best-practices` · `security-review`

---

## Los 3 comandos en detalle

### `/dev "tarea"`

Clasifica automáticamente y elige el camino:

```
Simple  → implementa directo → verifica → done
Medium  → /writing-plans → /subagent-driven-development → /finishing-a-development-branch
Complex → /brainstorming → /using-git-worktrees → /writing-plans
          → /subagent-driven-development → /finishing-a-development-branch
```

Flags:

| Flag | Efecto |
|---|---|
| `--simple` | Fuerza implementación directa |
| `--full` | Fuerza pipeline completo (brainstorm → worktree → plan → subagents) |
| `--ralph` | Activa ralph loop por iteración |
| `--max-iterations N` | Límite de iteraciones (default 20, max 50) |
| `--verify "cmd"` | Comando de verificación para ralph |

Ejemplos:

```
/dev "Fix null pointer en UserService.findById()"
/dev "Agregar paginación cursor-based al endpoint /users"
/dev "Implementar módulo de notificaciones completo" --full --ralph --max-iterations 30
```

---

### `/consult "pregunta"`

Auto-selecciona el experto por keywords:

| Keywords detectados | Experto asignado |
|---|---|
| api, nestjs, database, query, typeorm, cache, schema | backend-db-expert |
| auth, jwt, owasp, vulnerability, cors, xss | security-expert |
| react, next, component, tailwind, ux, form | frontend-ux-expert |
| docker, ci/cd, test, tdd, coverage, kubernetes | platform-expert |
| roadmap, mvp, backlog, user story, rice | product-expert |

Flags: `--deep` (120 líneas) · `--experts backend,security` (consulta múltiple)

Ejemplos:

```
/consult "¿Cómo implemento circuit breaker en NestJS?"
/consult "¿Cursor-based o offset pagination para mi API?" --deep
/consult "¿JWT o session para auth?" --experts backend,security
```

---

### `/ralph-loop "tarea"`

Itera autónomamente hasta que se detecta `<promise>COMPLETE</promise>` en la respuesta. El Stop hook (`ralph-check.js`) bloquea que Claude pare, incrementa el contador e inyecta contexto de continuación en cada iteración.

Routing automático por complejidad:

| Condición | Modo |
|---|---|
| ≥ 3 requisitos **o** múltiples tecnologías | **ORCHESTRATED**: worktree → plan → subagents → verify |
| < 3 requisitos, alcance pequeño | **DIRECT**: implementa directo → verifica |

Formato completo:

```
/ralph-loop "Implementar herramienta de gestión de proyectos"

Requisitos:
- Aplicación Next.js + Tailwind con localStorage
- Tablero Kanban (columnas: Todo / In Progress / Done)
- Lista de tareas con CRUD completo
- Sin errores de linter

Criterios de éxito:
- Todos los requisitos implementados
- Sin errores de linter
- Documentación actualizada

Output <promise>COMPLETE</promise> al finalizar. --max-iterations 30 --completion-promise "COMPLETE"
```

Lo que sucede internamente (modo ORCHESTRATED):

```
1. Escribe .claude/ralph-state.json con loopId, task, requirements, maxIterations
2. Banner: RALPH LOOP ACTIVATED — Task / Iterations / Completion promise
3. /using-git-worktrees → feat/<task-slug> en .worktrees/
4. /writing-plans → docs/plans/YYYY-MM-DD-<feature>.md
5. /subagent-driven-development:
   ├── experto → Tarea 1 → spec review → quality review → commit
   ├── experto → Tarea 2 → spec review → quality review → commit
   └── (una por una, sin paralelo)
6. npm run build && npm run lint (verificación final)
7. <promise>COMPLETE</promise> + echo COMPLETE > .claude/ralph-complete.txt
8. Stop hook detecta ralph-complete.txt → permite parar
```

Si algo falla antes de COMPLETE: el Stop hook bloquea, incrementa iteración e inyecta "continúa trabajando, esto falta: [criterios pendientes]". Claude retoma donde quedó.

---

## Los 5 agentes expertos

| Agente | Dominio |
|---|---|
| `backend-db-expert` | APIs, NestJS, TypeORM, microservicios, queries, schema design |
| `frontend-ux-expert` | React, Next.js, Tailwind, accesibilidad, UX, design systems |
| `platform-expert` | CI/CD, Docker, testing (TDD/BDD), cobertura, monitoreo |
| `product-expert` | Product discovery, roadmap, user stories, RICE/ICE, MVP |
| `security-expert` | OWASP, JWT, threat modeling, GDPR, SOC2 |

Asignación automática por dominio en `subagent-driven-development`:

| Dominio detectado | Agente |
|---|---|
| API, DB, NestJS, backend | backend-db-expert |
| React, Next.js, UI/UX, Tailwind | frontend-ux-expert |
| CI/CD, tests, infra | platform-expert |
| Auth, permisos, seguridad | security-expert |
| Mixed / general | platform-expert |

---

## Hooks

**Stop hook** — se ejecuta al terminar cada turno de Claude:
1. `ralph-check.js` — si ralph está activo y no existe `ralph-complete.txt`, bloquea el stop e inyecta contexto de continuación con iteración incrementada
2. Task verifier (prompt LLM) — verifica que la tarea del usuario esté realmente completa antes de permitir parar

**PostToolUse hook** — en cada `Edit` o `Write`:
- `format-on-save.sh` — formatea el archivo automáticamente

**Notification hook**:
- Notificación macOS cuando Claude necesita atención

---

## Estructura

```
.claude/
├── agents/              # 5 definiciones de agentes expertos
├── commands/            # 9 comandos/skills:
│   ├── dev.md                          ← comando maestro
│   ├── consult.md                      ← consulta experta
│   ├── ralph-loop.md                   ← loop autónomo
│   ├── brainstorming.md
│   ├── writing-plans.md
│   ├── using-git-worktrees.md
│   ├── subagent-driven-development.md
│   ├── requesting-code-review.md
│   └── finishing-a-development-branch.md
├── skills/              # Skills de dominio (cargados por agentes)
│   ├── api-design-principles/
│   ├── architecture-patterns/
│   ├── resilience-patterns/
│   ├── nestjs-code-reviewer/
│   ├── frontend-design/
│   ├── react-best-practices/
│   └── security-review/
├── hooks/
│   ├── ralph-check.js       # Stop hook: control del ralph loop
│   └── format-on-save.sh
├── README.md            # Manual de uso detallado
├── STATE.md             # Persistencia entre sesiones (auto-cargado)
└── settings.json        # Permisos, hooks, context includes
```

---

## Instalación en tu proyecto

```bash
# Clona el repo
git clone https://github.com/SebastianDevps/agent007

# Copia la carpeta .claude/ a tu proyecto
cp -r agent007/.claude/ tu-proyecto/.claude/
```

Los hooks y comandos se activan automáticamente al abrir Claude Code en el directorio del proyecto.

---

## Licencia

MIT — ver [LICENSE](LICENSE)
