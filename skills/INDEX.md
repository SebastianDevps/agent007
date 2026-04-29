# Skills INDEX — Agent007 v5.1

> Full registry of all skills. Path is relative to `.claude/skills/`.
> Updated: 2026-04-28

---

## pipeline/ — Development Flow

| Skill | Path | Invokable | Description |
|-------|------|-----------|-------------|
| `plan` | `pipeline/plan.md` | ✅ | Unified planning: decompose to 2-5min tasks (was: writing-plans + sop-planning) |
| `generate` | `pipeline/generate.md` | ✅ | TDD task execution with assumption tracking (was: sop-code-assist) |
| `verify` | `pipeline/verify.md` | ✅ | Two-pass verification: evidence gate + SDD review (was: verification-before-completion + sop-reviewer) |
| `brainstorming` | `pipeline/brainstorming.md` | ✅ | Socratic requirements exploration before implementation |
| `tdd-workflow` | `pipeline/tdd-workflow.md` | ✅ | Red-Green-Refactor gate: failing test required before any implementation |
| `subagent-driven-development` | `pipeline/subagent-driven-development.md` | ✅ | Dispatch expert subagents per task from plan |
| `using-git-worktrees` | `pipeline/using-git-worktrees.md` | ✅ | Isolated branch via git worktree |
| `finishing-a-development-branch` | `pipeline/finishing-a-development-branch.md` | ✅ | Close branch: verify → merge/PR/keep/discard |
| `sop-reverse` | `pipeline/sop-reverse.md` | ✅ | Reverse-engineer existing code before refactoring |

---

## core/ — Quality Enforcement (Always Active)

| Skill | Path | Invokable | Description |
|-------|------|-----------|-------------|
| `quality-enforcement` | `core/quality-enforcement.md` | ❌ (auto) | Anti-rationalization + verification rules |
| `banned-phrases` | `core/banned-phrases.md` | ❌ (auto) | Quick-ref: banned phrases → required replacements |
| `context-awareness` | `core/context-awareness.md` | ❌ (auto) | Task type detection, risk assessment, routing logic |

---

## orchestration/ — Session Management

| Skill | Path | Invokable | Description |
|-------|------|-----------|-------------|
| `session-manager` | `orchestration/session-manager.md` | ❌ (auto) | Routing, classification, state read/write protocol |
| `ralph-loop-wrapper` | `orchestration/ralph-loop-wrapper.md` | ❌ (auto) | Infrastructure: wraps task execution in ralph loop |
| `state-sync` | `orchestration/state-sync.md` | ❌ (auto) | Sync session state: .sdlc/state/session.md ↔ STATE.md |
| `iterative-retrieval` | `orchestration/iterative-retrieval.md` | ❌ (auto) | Progressive context refinement for subagent spawning: 3-round minimum-context protocol |

---

## domain/ — Domain-Specific Expertise

| Skill | Path | Invokable | Description |
|-------|------|-----------|-------------|
| `api-design-principles` | `domain/api-design-principles/SKILL.md` | ✅ | NestJS REST API design and audit |
| `architecture-patterns` | `domain/architecture-patterns/SKILL.md` | ✅ | Clean Architecture, DDD, Bounded Contexts |
| `resilience-patterns` | `domain/resilience-patterns/SKILL.md` | ✅ | Circuit breakers, retry, health checks |
| `nestjs-code-reviewer` | `domain/nestjs-code-reviewer/SKILL.md` | ✅ | NestJS + TypeORM code review + OWASP |
| `security-review` | `domain/security-review/SKILL.md` | ✅ | OWASP Top 10, auth, authorization, sensitive data |
| `react-best-practices` | `domain/react-best-practices/SKILL.md` | ✅ | React/Next.js optimization and best practices |
| `frontend-design` | `domain/frontend-design/SKILL.md` | ✅ | High-quality UI/UX design and implementation |
| `gsap` | `domain/gsap/SKILL.md` | ✅ | GSAP monolítico: tweens, timelines, ScrollTrigger, plugins, React, utils, performance |

---

## quality-gates/ — Quality & Debugging

| Skill | Path | Invokable | Description |
|-------|------|-----------|-------------|
| `systematic-debugging` | `quality-gates/systematic-debugging/SKILL.md` | ✅ | Root-cause analysis: reproduce → isolate → fix → verify |
| `agent-self-diagnosis` | `quality-gates/agent-self-diagnosis.md` | ✅ | 4-phase loop recovery: Capture → Diagnose → Recover → Report (fires at 3 repeated calls) |

---

## devrel/ — Developer Relations & Documentation

| Skill | Path | Invokable | Description |
|-------|------|-----------|-------------|
| `api-documentation` | `devrel/api-documentation/SKILL.md` | ✅ | OpenAPI, Swagger, developer portals, API reference |

---

## product/ — Product Discovery

| Skill | Path | Invokable | Description |
|-------|------|-----------|-------------|
| `product-discovery` | `product/product-discovery/SKILL.md` | ✅ | User stories, RICE, roadmap, MVP scoping |

---

## workflow-utils/ — Utilities

| Skill | Path | Invokable | Description |
|-------|------|-----------|-------------|
| `commit` | `workflow-utils/commit.md` | ✅ | Pipe-delimited commit: Tipo\|IdTarea\|YYYYMMDD\|Desc |
| `pull-request` | `workflow-utils/pull-request.md` | ✅ | Create structured GitHub PRs |
| `changelog` | `workflow-utils/changelog.md` | ✅ | Generate changelog from git history |
| `deep-research` | `workflow-utils/deep-research.md` | ✅ | 4-phase systematic research methodology |
| `search-first` | `workflow-utils/search-first.md` | ✅ | Pre-coding gate: library + codebase scan → Adopt/Extend/Compose/Build before any custom implementation |
| `rules-distill` | `workflow-utils/rules-distill.md` | ✅ | Scans skills for repeated principles, elevates to rules/ with anti-abstraction guard and per-item approval |
| `skill-stocktake` | `workflow-utils/skill-stocktake.md` | ✅ | Automated skill quality audit: Keep/Improve/Retire/Merge with incremental cache |

---

## Legacy paths (kept for backward compat, content migrated to v5 dirs)

| Old Path | New Location |
|----------|-------------|
| `_core/anti-rationalization/` | `core/quality-enforcement.md` |
| `_core/verification-enforcement/` | `core/quality-enforcement.md` |
| `_core/context-awareness/` | `core/context-awareness.md` |
| `_core/decision-memory/` | `core/` (reference only — logic in orchestration) |
| `_core/session-state/` | `orchestration/state-sync.md` |
| `_orchestration/session-orchestrator/` | `orchestration/session-manager.md` |
| `_orchestration/ralph-loop-wrapper/` | `orchestration/ralph-loop-wrapper.md` |
| `workflow/writing-plans/` | `pipeline/plan.md` |
| `sop/sop-planning/` | `pipeline/plan.md` |
| `sop/sop-code-assist/` | `pipeline/generate.md` |
| `workflow/verification-before-completion/` | `pipeline/verify.md` |
| `sop/sop-reviewer/` | `pipeline/verify.md` |
| `workflow/brainstorming/` | `pipeline/brainstorming.md` |
| `workflow/subagent-driven-development/` | `pipeline/subagent-driven-development.md` |
| `workflow/using-git-worktrees/` | `pipeline/using-git-worktrees.md` |
| `workflow/finishing-a-development-branch/` | `pipeline/finishing-a-development-branch.md` |
| `sop/sop-reverse/` | `pipeline/sop-reverse.md` |
| `api-design-principles/` | `domain/api-design-principles/` |
| `architecture-patterns/` | `domain/architecture-patterns/` |
| `resilience-patterns/` | `domain/resilience-patterns/` |
| `nestjs-code-reviewer/` | `domain/nestjs-code-reviewer/` |
| `security-review/` | `domain/security-review/` |
| `react-best-practices/` | `domain/react-best-practices/` |
| `frontend-design/` | `domain/frontend-design/` |
| `workflow/commit/` | `workflow-utils/commit.md` |
| `workflow/pull-request/` | `workflow-utils/pull-request.md` |
| `workflow/changelog/` | `workflow-utils/changelog.md` |
| `workflow/deep-research/` | `workflow-utils/deep-research.md` |

---

## Compressed Registry (for embedding in subagent prompts)

```
PIPELINE: plan, generate, verify, brainstorming, tdd-workflow, subagent-driven-development,
          using-git-worktrees, finishing-a-development-branch, sop-reverse
CORE: quality-enforcement*, banned-phrases*, context-awareness*  (* = auto-injected)
ORCH: session-manager*, ralph-loop-wrapper*, state-sync*, iterative-retrieval*
DOMAIN: api-design-principles, architecture-patterns, resilience-patterns,
        nestjs-code-reviewer, security-review, react-best-practices, frontend-design, gsap
QUALITY-GATES: systematic-debugging, agent-self-diagnosis
DEVREL: api-documentation
PRODUCT: product-discovery
UTILS: commit, pull-request, changelog, deep-research, search-first, rules-distill, skill-stocktake
Total: 28 invokable + 7 auto-injected = 35 active skills
```
