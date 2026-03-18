# Agent007

Plugin para Claude Code que resuelve dos problemas concretos: Claude para demasiado pronto y responde genéricamente sin contexto de dominio. Agent007 agrega un loop de iteración autónoma que bloquea el stop hasta que la tarea esté verificablemente completa, y un sistema de routing que inyecta skills especializados antes de responder.

**No es un IDE, no tiene UI, no reemplaza a Cursor.** Se usa con Claude Code CLI cuando necesitas control preciso del pipeline de desarrollo.

`v4.1` · `macOS · Linux · Windows` · `41 skills` · `5 agentes` · `16 comandos` · autor: [Sebastian Guerra](https://github.com/SebastianDevps)

---

## El problema

Claude Code funciona bien para tareas acotadas: fix puntual, refactor local, pregunta sobre un archivo. Se queda corto en tres situaciones:

**1. Tareas largas → Claude para a mitad**
```
/dev "Implementar módulo de notificaciones con email, push y websocket"
# Claude implementa el servicio de email, reporta "listo", y para.
# Las integraciones de push y websocket nunca ocurren.
```
No es un bug de Claude — es su comportamiento natural. Cada turno es independiente. Si no hay un mecanismo que fuerce la continuación, para cuando cree que terminó.

**2. Preguntas técnicas → respuesta genérica**
```
/consult "¿Cómo implemento circuit breaker en mi API?"
# Respuesta vanilla: "Puedes usar la librería X o implementar un contador de errores..."
# Sin saber que tu stack es NestJS + TypeORM + Redis, sin revisar tus patrones actuales.
```

**3. Feature compleja → decisión incorrecta del workflow**
Una feature de auth con breaking changes requiere worktree aislado, plan aprobado, subagentes y review. Una corrección de tipo requiere solo un edit directo. Sin clasificación automática, usas el mismo enfoque para todo.

---

## Los 4 comandos

### `/dev "tarea"` — comando maestro

Clasifica la tarea, elige el workflow y ejecuta de forma autónoma.

```
Input: /dev "tarea"
         │
         ├── Simple  (fix, typo, type change)
         │     └── implementa directo → verification-before-completion → done
         │
         ├── Medium  (feature acotada, refactor con contexto)
         │     └── writing-plans → subagent-driven-development
         │           └── por tarea: spec review → quality review → commit
         │           → finishing-a-development-branch
         │
         └── Complex (feature multi-módulo, refactor con breaking changes)
               └── brainstorming → using-git-worktrees → writing-plans
                     → subagent-driven-development + ralph-loop
                     → finishing-a-development-branch
```

**Ejemplos:**

```bash
# Simple — fix directo, sin overhead de plan
/dev "Fix null pointer en UserService.findById() cuando el usuario no existe"

# Medium — genera plan, despacha subagentes
/dev "Agregar paginación cursor-based al endpoint GET /users"

# Complex — brainstorm primero, worktree aislado, ralph loop activado
/dev "Implementar módulo de autenticación OAuth2 con Google y GitHub" --full --ralph

# Forzar modo específico
/dev "Rename UserDto to CreateUserDto en todo el proyecto" --simple
/dev "Refactor auth middleware a OAuth2" --full --ralph --max-iterations 30
```

**Qué ocurre internamente en modo Medium:**
- `writing-plans` descompone la tarea en sub-tareas de 2-5 minutos con rutas exactas y código completo, guarda el plan en `docs/changes/<feature>/spec.md`
- `subagent-driven-development` despacha un subagente fresco por tarea — contexto limpio, sin contaminación de tareas anteriores
- Cada tarea pasa por dos reviews antes de avanzar: cumplimiento del spec, luego calidad de código
- `finishing-a-development-branch` presenta 4 opciones: merge local / push+PR / mantener / descartar

---

### `/consult "pregunta"` — consulta experta

No responde desde conocimiento general. Detecta keywords, selecciona el agente con más matches, carga sus skills especializados como contexto adicional, y responde desde esa perspectiva.

```
Input: /consult "¿Implemento circuit breaker o retry con backoff exponencial?"
         │
         ├── keywords detectados: retry, circuit-breaker → backend-db-expert
         │
         ├── carga skills del agente:
         │     api-design-principles + architecture-patterns + resilience-patterns
         │
         └── responde con contexto real de:
               - patrones NestJS específicos (decoradores, interceptors)
               - cuándo circuit breaker vs retry no es una pregunta de or
               - implementación con @nestjs/axios + opossum
```

**Tabla de routing por keywords:**

| Keywords detectados | Agente |
|---------------------|--------|
| `api, nestjs, database, query, typeorm, cache, redis, schema, retry, resilience, circuit-breaker` | `backend-db-expert` |
| `auth, jwt, owasp, vulnerability, injection, cors, xss, encryption` | `security-expert` |
| `react, next, component, tailwind, ux, accessibility, form, design` | `frontend-ux-expert` |
| `deploy, docker, ci/cd, test, coverage, kubernetes, monitoring, pipeline` | `platform-expert` |
| `roadmap, mvp, backlog, user story, rice, acceptance criteria, discovery` | `product-expert` |

```bash
/consult "¿Cursor-based o offset pagination para una API con millones de registros?" --deep
/consult "¿JWT stateless o session con Redis para auth?" --experts backend,security
/consult "¿Cómo estructuro el backlog para MVP de marketplace?" --experts product
```

Flags: `--deep` (120 líneas, carga todos los skills del agente) · `--quick` (25 líneas) · `--experts X,Y` (consulta secuencial a múltiples agentes)

---

### `/prompt-gen "[objetivo]"` — convierte el contexto del consult en prompt ejecutable

Después de `/consult`, las recomendaciones del experto quedan como texto conversacional. La siguiente invocación de `/dev` no las recuerda — Claude las redescubre desde cero o las ignora. `/prompt-gen` toma ese contexto y lo estructura con los 10 componentes del framework Anthropic (XML): identity, task_context, constraints, fases numeradas con criterios de completitud, scratchpad, meta-instrucciones.

```
/consult "¿Cómo implemento refresh token rotation en NestJS?"
    │
    └── security-expert responde con 5 decisiones técnicas concretas
          │
          └── /prompt-gen "implementar refresh token rotation" --target dev
                │
                ├── extrae: httpOnly cookie, hash en DB, rotación en cada uso,
                │   replay attack → revocar todas las sesiones, TTL 15min/7días
                │
                └── genera instrucción /dev con todo ese contexto codificado
                      → /dev arranca sin re-preguntar al experto
```

**Targets:**

| Flag | Output | Cuándo |
|------|--------|--------|
| `--target dev` _(default)_ | Instrucción comprimida ≤250 palabras | Continuar con `/dev` en la misma sesión |
| `--target subagent` | XML completo con los 10 componentes | Pre-cargar contexto para `subagent-driven-development` |
| `--target session` | System prompt standalone | Nueva sesión / otro modelo / uso externo |

```bash
# Genera instrucción /dev comprimida con contexto del experto
/prompt-gen "implementar refresh token rotation" --target dev

# Genera system prompt XML para dispatch de subagente
/prompt-gen "diseñar módulo de pagos con bounded contexts" --target subagent

# Genera y guarda system prompt standalone en .claude/prompts/
/prompt-gen "auth OAuth2 con Google" --target session --save
```

**Qué ocurre internamente:**
- Extrae del contexto reciente: qué experto respondió, cuáles fueron las 3-5 decisiones técnicas, qué trade-offs se mencionaron, qué quedó abierto
- Construye `<identity>` con stack real (no genérico), `<task_context>` con las decisiones ya tomadas, `<constraints>` con las 4 reglas de Agent007 + restricciones del dominio, fases ejecutables con criterios de completitud concretos
- `/consult` ofrece automáticamente este comando al final de cada respuesta técnica

---

### `/ralph-loop "tarea"` — loop autónomo hasta completitud

El Stop hook de Claude Code intercepta cada turno antes de que Claude pare. Si `ralph-complete.txt` no existe, bloquea el stop, incrementa el contador de iteración, e inyecta contexto de continuación. Claude retoma donde quedó.

La tarea termina cuando Claude escribe explícitamente `<promise>COMPLETE</promise>` — lo que activa `echo COMPLETE > .claude/ralph-complete.txt` y el Stop hook libera el control.

**Routing automático por complejidad:**

```
≥ 3 requisitos o múltiples tecnologías → ORCHESTRATED
  worktree → plan → subagents por tarea → verificación final

< 3 requisitos, alcance pequeño → DIRECT
  implementa directo → verifica → COMPLETE
```

```bash
/ralph-loop "Implementar herramienta de gestión de proyectos"

Requisitos:
- Next.js + Tailwind con localStorage
- Tablero Kanban: columnas Todo / In Progress / Done
- CRUD completo de tareas
- Sin errores de linter

Criterios de éxito:
- Todos los requisitos implementados
- npm run build sin errores
- npm run lint sin warnings

Output <promise>COMPLETE</promise> al finalizar.
--max-iterations 30
```

---

## Ralph Loop — por qué existe

Claude tiene un comportamiento natural: cuando cree que terminó, para y reporta éxito. En tareas largas esto produce completitud aparente — la arquitectura está, pero el módulo de email no está conectado, los tests no pasan, el linter tiene 12 warnings.

El Stop hook es el mecanismo que rompe ese patrón.

**Ciclo de vida del Stop hook:**

```
Claude produce respuesta
         │
         ▼
ralph-check.js (Stop hook)
         │
         ├── ¿Existe .claude/ralph-complete.txt?
         │     └── SÍ → permite parar ✅
         │
         └── NO → bloquea el stop
               └── incrementa iteración N
               └── inyecta: "Iteración N/30. Criterios pendientes: [lista]"
               └── Claude recibe el contexto y continúa
```

**DIRECT mode** (tarea simple, < 3 requisitos):

```
Iteración 1: implementa componente Kanban
Iteración 2: agrega drag-and-drop
Iteración 3: npm run lint → 2 warnings
Iteración 4: fix warnings → npm run build ✅ → COMPLETE
echo COMPLETE > .claude/ralph-complete.txt
Stop hook detecta archivo → libera control → Claude para
```

**ORCHESTRATED mode** (tarea compleja, múltiples tecnologías):

```
Iteración 1: using-git-worktrees → feat/kanban-board en .worktrees/
Iteración 2: writing-plans → docs/changes/kanban-board/spec.md (18 tareas)
Iteraciones 3-20: subagent-driven-development
  └── Subagente 1 → Tarea 1 (Board layout) → spec review → quality review → commit
  └── Subagente 2 → Tarea 2 (Column component) → spec review → quality review → commit
  └── (...)
Iteración 21: npm run build && npm run lint → ✅
Iteración 22: COMPLETE → archivo escrito → Stop hook libera
```

**Costo honesto:** cada iteración consume tokens adicionales (contexto de continuación + re-evaluación del estado). Tareas con ralph activo consumen entre 2x y 3x los tokens de un single-pass. Úsalo cuando el costo de una tarea incompleta sea mayor que el costo de tokens extra.

---

## Los 5 agentes expertos

Cada agente tiene skills especializados que se inyectan como contexto al consultar. No es solo un label diferente — es conocimiento de dominio concreto que cambia la calidad de la respuesta.

---

**`backend-db-expert`** (Claude Opus) — APIs, NestJS, TypeORM, microservicios, queries

```
/consult "¿Cómo evito N+1 queries en este endpoint?"

→ keywords: query, typeorm → backend-db-expert
→ inyecta: api-design-principles + architecture-patterns + resilience-patterns
→ responde con: eager loading vs lazy loading en TypeORM, uso de QueryBuilder
  con JOINs explícitos, DataLoader para GraphQL, índices relevantes
```

---

**`security-expert`** (Claude Opus) — OWASP, JWT, threat modeling, GDPR, SOC2

```
/consult "¿Mi implementación de JWT es segura?"

→ keywords: jwt, auth → security-expert
→ inyecta: security-review
→ responde con: checklist OWASP para JWT (alg none attack, weak secrets,
  missing expiry), validación de claims, rotación de refresh tokens,
  storage seguro en cliente (httpOnly cookie vs localStorage trade-offs)
```

---

**`frontend-ux-expert`** (Claude Sonnet) — React/Next.js, accesibilidad, design systems

```
/consult "¿Cómo optimizo el re-render de esta lista de 5000 items?"

→ keywords: react, component → frontend-ux-expert
→ inyecta: react-best-practices + frontend-design
→ responde con: windowing con react-virtual, memo y useCallback con criterios
  concretos de cuándo usarlos, profiling con React DevTools Profiler,
  por qué key={index} rompe el reconciliador en listas dinámicas
```

---

**`platform-expert`** (Claude Sonnet) — CI/CD, Docker, testing, monitoreo

```
/consult "¿Cómo estructura el pipeline de CI para un monorepo NestJS + Next.js?"

→ keywords: ci/cd, deploy → platform-expert
→ inyecta: scenario-driven-development + systematic-debugging
→ responde con: matrix builds por workspace, cache de node_modules por hash
  de lockfile, staging smoke tests como gate obligatorio antes de prod,
  rollback con imagen tageada (v1.2.3, no solo latest)
```

---

**`product-expert`** (Claude Opus) — product discovery, roadmap, user stories

```
/consult "Quiero agregar un sistema de notificaciones"

→ keywords: feature, discovery → product-expert
→ inyecta: product-discovery
→ responde con: 8 preguntas socráticas (¿qué problema tiene el usuario?,
  ¿cuándo ocurre?, ¿cómo lo resuelve hoy?), Discovery Document con
  Must/Should/Could/Won't, métricas de éxito medibles
```

---

## Comparativa honesta

| Capacidad | Claude Code vanilla | Agent007 | Cursor | GitHub Copilot |
|-----------|:-------------------:|:--------:|:------:|:--------------:|
| Routing por complejidad (simple/medium/complex) | ❌ | ✅ `/dev` | ❌ | ❌ |
| Loop hasta completitud verificada | ❌ | ✅ Ralph | ❌ | ❌ |
| Agentes especializados por dominio | ❌ | ✅ 5 expertos | ❌ | ❌ |
| Skill injection en consultas | ❌ | ✅ `/consult` | ❌ | ❌ |
| SDD enforcement (gate, no recomendación) | ❌ | ✅ hook | ❌ | ❌ |
| Subagentes con contexto limpio por tarea | ❌ | ✅ | ❌ | ❌ |
| Contexto nativo de codebase | ✅ | ✅ | ✅ | ⚠️ parcial |
| UI / IDE integration | ❌ terminal | ❌ terminal | ✅ | ✅ |
| Costo de tokens vs single-pass | baseline | 2-3x (ralph) | similar | similar |
| Plataforma | multi | ✅ multi | multi | multi |

Agent007 no reemplaza a Cursor o Copilot. Se usa con Claude Code CLI cuando necesitas control explícito del pipeline: worktree aislado, plan aprobado, subagentes por tarea, review en dos etapas. Para autocompletado o edición asistida en el IDE, usa Cursor.

---

## Walk-through: módulo JWT en NestJS

Escenario completo desde comando hasta PR.

**1. Comando inicial**

```bash
/dev "Implementar autenticación JWT con access token (15 min) y refresh token (7 días) en NestJS"
```

**2. Clasificación automática**

```
🎯 [FEATURE] → /dev Medium
Risk: high (auth) | Stack: NestJS detectado
⚠️  Riesgo alto detectado: autenticación. Confirmar antes de continuar.
¿Proceder con pipeline completo? [S/n]
```

**3. Plan generado por `writing-plans`**

```
Guardando plan en docs/changes/jwt-auth/spec.md...

# Plan: JWT Authentication
Risk: Critical | Duración estimada: 2h | Tareas: 12

Fase 1 — Dependencias y configuración (tareas 1-3, ~10 min)
  Tarea 1: Instalar @nestjs/jwt, @nestjs/passport, passport-jwt      (2 min)
  Tarea 2: Crear JwtConfigService con secrets desde .env             (3 min)
  Tarea 3: Registrar JwtModule en AuthModule                         (2 min)

Fase 2 — Entidades y DTOs (tareas 4-5, ~8 min)
  Tarea 4: Agregar campo refreshToken a User entity                  (3 min)
  Tarea 5: Crear LoginDto y TokenResponseDto con class-validator     (3 min)

Fase 3 — Servicios y guards (tareas 6-9, ~20 min)
  Tarea 6: Implementar AuthService.login() → genera access + refresh (5 min)
  Tarea 7: Implementar AuthService.refresh() con rotación de token   (5 min)
  Tarea 8: Crear JwtStrategy para validar access tokens              (4 min)
  Tarea 9: Crear JwtAuthGuard y aplicar a rutas protegidas           (3 min)

Fase 4 — Tests y verificación (tareas 10-12, ~15 min)
  Tarea 10: Tests unitarios AuthService (login, refresh, logout)     (5 min)
  Tarea 11: Tests de integración /auth/login y /auth/refresh         (5 min)
  Tarea 12: Revisión OWASP: alg none, secrets en env, expiry        (3 min)

¿Aprobar plan? [S/n]
```

**4. Dispatch de subagentes**

```
[Tarea 1/12] → security-expert (auth domain detectado)
  ✅ spec review: @nestjs/jwt instalado, passport-jwt tipado
  ✅ quality review: secrets en ConfigService, no hardcoded
  ✅ commit: feat(auth): install JWT dependencies

[Tarea 2/12] → backend-db-expert
  ✅ spec review: JwtConfigService implementado
  ✅ quality review: validación de env vars al startup (no lazy)
  ✅ commit: feat(auth): add JWT config service

[Tarea 6/12] → security-expert
  ⚠️  quality review: refresh token no está hasheado antes de persistir
  → subagente corrige → re-review → ✅
  ✅ commit: feat(auth): implement login with hashed refresh token
```

**5. Verificación final**

```
npm run test:unit   → 47 passed
npm run test:e2e    → 12 passed
npm run lint        → 0 errors, 0 warnings
npm run build       → compiled successfully
```

**6. `finishing-a-development-branch`**

```
Branch: feat/jwt-auth
Commits: 12 | Tests: 59 passed | Build: ✅ | Lint: ✅

Opciones:
  [1] Merge local en main
  [2] Push + abrir PR en GitHub
  [3] Mantener branch sin hacer nada
  [4] Descartar branch
→ 2

PR creado: github.com/tu-org/tu-repo/pull/47
"feat: JWT authentication with access and refresh tokens"
```

---

## Instalación

**Opción A — script de instalación** (recomendado)

```bash
git clone https://github.com/SebastianDevps/agent007
bash agent007/install.sh /ruta/a/tu-proyecto
```

El script copia `.claude/` al proyecto, da permisos a los hooks, y muestra confirmación si ya existe una instalación previa.

**Opción B — manual**

```bash
git clone https://github.com/SebastianDevps/agent007
cp -r agent007/.claude/ tu-proyecto/.claude/
```

Abre tu proyecto en Claude Code — los hooks y comandos se activan automáticamente. En la primera sesión verás el banner de bienvenida de Agent007 en la terminal.

**Requisito:** Claude Code CLI instalado. **Plataforma:** macOS · Linux · Windows (todos los hooks son Python 3 o Node.js).

Referencia completa de comportamiento, enforcement rules y routing: [`.claude/CLAUDE.md`](.claude/CLAUDE.md)

---

## Estructura

```
.claude/
├── agents/                   # Definiciones de los 5 agentes expertos
│   ├── backend-db-expert.md
│   ├── frontend-ux-expert.md
│   ├── platform-expert.md
│   ├── product-expert.md
│   └── security-expert.md
│
├── commands/                 # 16 comandos invocables con /nombre o Skill()
│   ├── dev.md                              ← clasificación + routing maestro
│   ├── consult.md                          ← keyword match + skill injection
│   ├── prompt-gen.md                       ← convierte /consult en prompt ejecutable
│   ├── ralph-loop.md                       ← loop autónomo hasta COMPLETE
│   ├── brainstorming.md                    ← exploración socrática de requisitos
│   ├── writing-plans.md                    ← descomposición en tareas de 2-5 min
│   ├── using-git-worktrees.md              ← branch aislado en .worktrees/
│   ├── subagent-driven-development.md      ← dispatch de subagentes por tarea
│   ├── requesting-code-review.md           ← review en 2 etapas (spec + calidad)
│   ├── finishing-a-development-branch.md   ← cierre de branch con 4 opciones
│   ├── verification-before-completion.md   ← gate obligatorio antes de declarar done
│   ├── scenario-driven-development.md      ← metodología anti-reward-hacking (SDD)
│   ├── deep-research.md                    ← investigación sistemática en 4 fases
│   ├── commit.md                           ← conventional commits con semver signals
│   ├── pull-request.md                     ← PR estructurado con summary + test plan
│   └── changelog.md                        ← changelog desde git history (Keep a Changelog)
│
├── skills/                   # 40 skills agrupados por dominio
│   ├── _core/                        ← enforcement (anti-rationalization, verification)
│   ├── _orchestration/               ← session state, ralph-loop-wrapper
│   ├── workflow/                     ← 18 skills de proceso (commit, PR, changelog, prompt-gen...)
│   ├── sop/                          ← pipeline SOP: discovery → planning → assist → review
│   ├── quality-gates/                ← systematic-debugging, architecture-review
│   ├── product/                      ← product-discovery
│   ├── devrel/                       ← api-documentation
│   └── [dominio]/                    ← api-design-principles, resilience-patterns,
│                                        security-review, nestjs-code-reviewer,
│                                        react-best-practices, frontend-design,
│                                        architecture-patterns
│
├── hooks/                    # Se ejecutan automáticamente en eventos de Claude Code
│   ├── welcome.py                    ← SessionStart: banner de bienvenida (primera sesión)
│   ├── ralph-check.js                ← Stop: bloquea si ralph-complete.txt no existe
│   ├── sdd-test-guard.py             ← PreToolUse Edit/Write: bloquea si no hay escenario
│   ├── sdd-auto-test.py              ← PostToolUse Edit/Write: corre tests tras cada edit
│   ├── memory-check.py               ← SessionStart: detecta cambios en dependencias
│   ├── subagent-start.py             ← SubagentStart: inyecta skills al subagente
│   ├── format-on-save.py             ← PostToolUse: formatea archivo editado (cross-platform)
│   ├── constraint-reinforcement.py   ← UserPromptSubmit: reinyecta reglas en sesiones largas
│   ├── stop-state-sync.py            ← Stop: serializa session-state a .session-state.json y actualiza STATE.md
│   ├── context-window-guard.py       ← PostToolUse: advierte al 30% y 15% de contexto restante
│   └── agent007-statusline.js        ← PreToolUse: muestra skill activo + contexto% en terminal (ANSI)
│
├── STATE.md                  # Persistencia entre sesiones (tarea activa, decisiones)
├── CLAUDE.md                 # Instrucciones del sistema (auto-cargado por Claude Code)
└── settings.json             # Permisos, hooks registrados, context includes
```

---

## Session intelligence (v4.1)

`stop-state-sync.py` serializa el estado de la sesión a `.claude/.session-state.json` en cada Stop — el routing recuerda el skill previo entre procesos. `context-window-guard.py` inyecta un advisory cuando el contexto baja del 30% (warning) o 15% (crítico) para evitar truncaciones silenciosas. `agent007-statusline.js` muestra en la terminal el skill activo, la tarea en curso y el porcentaje de contexto restante con barra ANSI coloreada.

---

## Licencia

MIT — ver [LICENSE](LICENSE)
