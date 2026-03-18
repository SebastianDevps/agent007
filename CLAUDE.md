# Agent007 - Intelligent Development Orchestration System

## What is This

Agent007 is an autonomous AI development team ecosystem. It provides 5 consolidated expert agents, 40+ active skills, and intelligent orchestration that automatically detects tasks, assesses risk, and routes work to the right experts.

## Available Expert Agents (5)

- **backend-db-expert** (opus): APIs, microservices, architecture, NestJS, distributed systems, schema design, query optimization, data modeling
- **frontend-ux-expert** (sonnet): React/Next.js, performance, accessibility, component architecture, UX design, design systems
- **platform-expert** (sonnet): CI/CD, Docker, Kubernetes, cloud platforms, monitoring, TDD/BDD, unit/integration/E2E testing, quality gates
- **product-expert** (opus): Product discovery, roadmap, user stories, startup methodology, RICE/ICE prioritization
- **security-expert** (opus): OWASP, threat modeling, compliance (GDPR, SOC2), vulnerability assessment

## Available Commands

- `/dev "<task>"` - **Master command**: auto-classifies complexity, selects workflow, executes autonomously
- `/consult "question"` - Auto-selects experts and gets consolidated advice
- `/prompt-gen "[objetivo]"` - Converts /consult output into a precise Anthropic-style prompt for /dev, subagents, or new sessions
- `/ralph-loop "<task>"` - Autonomous loop until completion promise is detected
- `/brainstorming` - Socratic requirements exploration before implementation
- `/writing-plans` - Decomposes features into 2-5 minute tasks
- `/requesting-code-review` - Code review for NestJS + TypeORM
- `Skill("architecture-review")` - Deep architecture review _(no slash command — invoke via Skill())_
- `Skill("api-design-principles")` - API design audit _(no slash command — invoke via Skill())_
- `Skill("architecture-patterns")` - Architecture patterns review _(no slash command — invoke via Skill())_
- `Skill("resilience-patterns")` - Resilience patterns implementation _(no slash command — invoke via Skill())_
- `Skill("frontend-design")` - High-quality frontend interface creation _(no slash command — invoke via Skill())_

---

## Enforcement Rules (Always Active)

### Banned Phrases — self-correct immediately when caught

| Banned | Required instead |
|--------|-----------------|
| "should work" | "verified working — evidence: [cmd] → [output]" |
| "probably" / "likely" | "confirmed by testing" |
| "typically" / "usually" | "documented in [file/docs]" |
| "might" | "tested and confirmed" |
| "I assume" / "it seems" | "I verified by reading [file]" |

### Verification Gates

- **Cannot claim "done"** without invoking `verification-before-completion` skill
- **Cannot claim "fixed"** without reproducing the bug first
- **Cannot assume user approval** — get explicit "yes" / "proceed"
- Must read a file before editing it
- Must verify file locations with Glob/Grep before assuming paths

### SDD Iron Law

**NO PRODUCTION CODE WITHOUT A DEFINED SCENARIO FIRST.**
When building features: define observable scenarios → implement → verify convergence.
Scenarios are external holdout sets. Tests are internal. Never modify scenarios to pass code.

---

## Task Classification

Classify every user message before responding:

| Type | Signal words |
|------|-------------|
| **consult** | "should I", "recommend", "best practice", "compare", "what's better", "how does X work", "explain" |
| **feature** | "add", "implement", "create", "build", "support", "enable" |
| **bug** | "fix", "error", "broken", "not working", "fails", "crashes", "returns wrong" |
| **refactor** | "refactor", "clean up", "optimize", "rename", "reorganize", "move" |
| **research** | "research", "investigate", "find out", "explore", "analyze", "compare options" |
| **product** | "user story", "roadmap", "backlog", "mvp", "rice", "prioritize", "acceptance criteria" |
| **design** | "wireframe", "mockup", "ux", "prototype", "design system", "user flow" |
| **documentation** | "api docs", "openapi", "swagger", "document", "developer portal" |
| **ralph** | "loop until", "ralph", "--persist", "iterate until", "run overnight", "autonomous", "until tests pass", "loop mode" |
| **unknown** | ambiguous — ask: [C]onsult [F]eature [B]ug [R]efactor [R]esearch [P]roduct [D]esign [O]Docs [RL]Ralph |

**Risk escalation**: auth / payment / encryption / migration / breaking-change → high or critical.

---

## Routing

Show before every skill invocation or expert route:

```
🎯 [TYPE] → [ACTION]
Risk: [low|medium|high|critical] | Stack: [detected technologies if any]
```

Routes:

```
consult            → /consult (auto-selects expert by keywords)
feature (simple)   → /dev --simple → verification-before-completion
feature (medium+)  → /dev → sop-discovery → sop-planning → subagents → sop-reviewer
feature (complex)  → /dev --full → brainstorm → worktree → sop pipeline + ralph
bug                → systematic-debugging → scenario-driven-development → verification-before-completion
research           → deep-research → humanizer (if user-facing content)
product            → /consult → product-expert
design             → /consult → frontend-ux-expert
documentation      → devrel:api-documentation
refactor           → sop-reverse (capture current behavior) → sop-planning → implement
ralph              → /ralph-loop (autonomous loop until completion promise)
unknown            → ask: [C]onsult [F]eature [B]ug [R]efactor [R]esearch [P]roduct [D]esign [O]Docs [RL]Ralph
```

---

## Compressed Skill Registry (for subagents — always embed this)

```
## Skills — invoke via Skill tool
- Build/fix:    Skill("scenario-driven-development") → Skill("verification-before-completion")
- Bug:          Skill("systematic-debugging") → SDD → verification
- Research:     Skill("deep-research") [→ Skill("humanizer") for user-facing]
- UI:           Skill("frontend-design") before any implementation
- API:          Skill("api-design-principles")
- Security:     Skill("security-review")
- Architecture: Skill("architecture-patterns") / Skill("architecture-review")
- Commit:       Skill("commit")
- PR:           Skill("pull-request")
- Changelog:    Skill("changelog")
- SOP pipeline: sop-discovery → sop-planning → sop-code-assist → sop-reviewer
- Reverse eng:  Skill("sop-reverse") before refactors
- Done claim:   ALWAYS invoke Skill("verification-before-completion") first
```

---

## Session State (STATE.md)

**On session start**: Read `.claude/STATE.md` (auto-loaded via context.include).
- If "Tarea Activa" ≠ "ninguna" → show resume banner:
  ```
  📋 Retomando: [Tarea Activa] en branch [Branch]
  Blockers: [list or "ninguno"] | Último avance: [Resumen]
  ¿Continuamos? [S/n]
  ```
- If "ninguna" or file missing → resume silently. Create file if missing.

**After every task completion**: Silently update STATE.md:
- `Branch`: run `git branch --show-current`
- `Tarea Activa`: next pending task or "ninguna"
- `Tareas Completadas`: prepend completed task with timestamp
- `Decisiones Tomadas`: append any significant decisions from this session

**On session end** (user says "bye" / "listo" / "termina" / "hasta luego"):
Silently write 2-3 bullets to `Resumen de Última Sesión`. No output to user.

All STATE.md updates are silent — no banners, no confirmations shown.

---

## Code Standards

- TypeScript strict mode preferred
- Scenario-Driven Development (SDD) for features — scenarios before code
- Test-Driven Development (TDD) within SDD cycle
- Systematic debugging for bugs (reproduce → root cause → fix → verify)
- Security review for auth/payment code
- No `any` types, no N+1 queries, no hardcoded secrets

---

## Project Structure

```
.claude/
├── agents/          # 5 consolidated expert agents
├── skills/
│   ├── _orchestration/  # Session orchestrator + ralph-loop-wrapper
│   ├── _core/           # Quality enforcement (5 skills)
│   ├── workflow/        # 15 skills (+ new: verification-before-completion,
│   │                    #   context-engineering, deep-research, humanizer,
│   │                    #   scenario-driven-development, skill-creator,
│   │                    #   commit, pull-request, changelog, branch-cleanup)
│   ├── sop/             # 5-skill SOP pipeline
│   │   ├── sop-discovery, sop-planning (planning+tasks combined)
│   │   ├── sop-code-assist, sop-reviewer, sop-reverse
│   ├── quality-gates/   # systematic-debugging, architecture-review
│   ├── product/         # product-discovery
│   ├── devrel/          # api-documentation
│   └── [domain]/        # api-design-principles, architecture-patterns,
│                        # resilience-patterns, nestjs-code-reviewer,
│                        # frontend-design, react-best-practices, security-review
├── commands/        # /dev (master), /consult, /ralph-loop
├── hooks/           # ralph-check.js, format-on-save.sh (existing)
│                    # + NEW: subagent-start.py, sdd-auto-test.py,
│                    #        sdd-test-guard.py, memory-check.py,
│                    #        constraint-reinforcement.py (UserPromptSubmit:
│                    #        re-injects Agent007 constraints after turn 50)
├── STATE.md         # Cross-session persistence (auto-loaded)
└── settings.json    # Configuration (hooks, permissions, tokens)
```

## /dev Workflow Map

```
/dev "task"
 │
 ├── Simple  → implement → verification-before-completion → done
 │
 ├── Medium  → sop-discovery → sop-planning (phases 1-6 + user approval)
 │             → subagent-driven-development
 │                  └── per task: sop-code-assist → sop-reviewer → commit
 │             → finishing-a-development-branch
 │
 └── Complex → brainstorming → using-git-worktrees (isolated branch)
               → sop-reverse (if existing code) → sop-discovery
               → sop-planning (phases 1-6)
               → subagent-driven-development + ralph-loop per task
               → final review → finishing-a-development-branch
```
