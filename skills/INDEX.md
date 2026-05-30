# Skills INDEX — Agent007 v7 (flat layout)

> Full registry of all skills. Path is relative to `.claude/skills/`.
> All skills are at depth-1 (`<name>/SKILL.md`). Prefix convention: `<category>-<name>/SKILL.md` for namespaced skills.
> Updated: 2026-05-25 (flatten-skills-to-anthropic-spec migration)

---

## All Skills (alphabetical)

| Skill name | Path | Category | Invokable | Description |
|---|---|---|---|---|
| `adr-review` | `adr-review/SKILL.md` | pipeline | ✅ | Periodic check on existing ADRs for aging |
| `adr-write` | `adr-write/SKILL.md` | pipeline | ✅ | Record architectural decisions with multi-change implications |
| `agent-self-diagnosis` | `agent-self-diagnosis/SKILL.md` | quality-gates | ✅ | 4-phase loop recovery: Capture → Diagnose → Recover → Report (fires at 3 repeated calls) |
| `brainstorming` | `brainstorming/SKILL.md` | pipeline | ✅ | Socratic requirements exploration before implementation |
| `changelog` | `changelog/SKILL.md` | workflow-utils | ✅ | Generate changelog from git history |
| `commit` | `commit/SKILL.md` | workflow-utils | ✅ | Pipe-delimited commit: Tipo\|IdTarea\|YYYYMMDD\|Desc |
| `consult-critique` | `consult-critique/SKILL.md` | orchestration | ✅ (via `/consult`) | Planning-only adversarial review of pasted proposals |
| `consult-decide` | `consult-decide/SKILL.md` | orchestration | ✅ (via `/consult`) | Planning-only dual-blind-proposer for option decisions |
| `deep-research` | `deep-research/SKILL.md` | workflow-utils | ✅ | 4-phase systematic research methodology |
| `devrel-api-documentation` | `devrel-api-documentation/SKILL.md` | devrel | ✅ | OpenAPI, Swagger, developer portals, API reference |
| `dispatching-parallel-agents` | `dispatching-parallel-agents/SKILL.md` | orchestration | ✅ | Dispatch one agent per independent problem domain — concurrent investigations |
| `domain-a11y-contrast-check` | `domain-a11y-contrast-check/SKILL.md` | domain | ✅ | Run Node.js script to verify WCAG AA color contrast on TS/TSX/CSS files. Exits 1 if <4.5:1 |
| `domain-api-design-principles` | `domain-api-design-principles/SKILL.md` | domain | ✅ | NestJS REST API design and audit |
| `domain-architecture-patterns` | `domain-architecture-patterns/SKILL.md` | domain | ✅ | Clean Architecture, DDD, Bounded Contexts |
| `domain-design-system-doc` | `domain-design-system-doc/SKILL.md` | domain | ✅ | Generate canonical 9-section DESIGN.md |
| `domain-design-tokens-extract` | `domain-design-tokens-extract/SKILL.md` | domain | ✅ | WebFetch a referent URL → extract palette/typography/spacing → write tokens.css or tokens.json |
| `domain-discovery-before-code` | `domain-discovery-before-code/SKILL.md` | domain | ✅ | Anti-convergence gate: forces referent fetch + style choice + state design + tokens BEFORE any visual code |
| `domain-frontend-design` | `domain-frontend-design/SKILL.md` | domain | ✅ | High-quality UI/UX design and implementation |
| `domain-gsap` | `domain-gsap/SKILL.md` | domain | ✅ | GSAP: tweens, timelines, ScrollTrigger, plugins, React, utils, performance |
| `domain-ios-hig-mobile` | `domain-ios-hig-mobile/SKILL.md` | domain | ✅ | Mobile-first components following Apple HIG for web |
| `domain-behavioral-contracts` | `domain-behavioral-contracts/SKILL.md` | domain | ✅ | Behavioral contracts deep-dive (DECLARE_BEFORE_ACT, SCOPE_IS_CONTRACT, SIMPLEST_SOLUTION, VERIFY_NOT_ASSUME) |
| `domain-nestjs-code-reviewer` | `domain-nestjs-code-reviewer/SKILL.md` | domain | ✅ | NestJS + TypeORM code review + OWASP |
| `domain-page-transitions-barba` | `domain-page-transitions-barba/SKILL.md` | domain | ✅ | Setup barba.js + GSAP page transitions |
| `domain-react-best-practices` | `domain-react-best-practices/SKILL.md` | domain | ✅ | React/Next.js optimization and best practices |
| `domain-resilience-patterns` | `domain-resilience-patterns/SKILL.md` | domain | ✅ | Circuit breakers, retry, health checks |
| `domain-security-review` | `domain-security-review/SKILL.md` | domain | ✅ | OWASP Top 10, auth, authorization, sensitive data |
| `domain-shadcn-component-install` | `domain-shadcn-component-install/SKILL.md` | domain | ✅ | Install shadcn/ui via CLI with mandatory dry-run preview |
| `domain-spline-3d-embed` | `domain-spline-3d-embed/SKILL.md` | domain | ✅ | Embed Spline 3D scenes safely: lazy-load, perf-gated, mobile-aware |
| `finishing-a-development-branch` | `finishing-a-development-branch/SKILL.md` | pipeline | ✅ | Close branch: verify → merge/PR/keep/discard |
| `generate` | `generate/SKILL.md` | pipeline | ✅ | TDD task execution with assumption tracking |
| `issue-creation` | `issue-creation/SKILL.md` | pipeline | ✅ | Create structured GitHub issues |
| `iterative-retrieval` | `iterative-retrieval/SKILL.md` | orchestration | ❌ (auto) | Progressive context refinement for subagent spawning: 3-round minimum-context protocol |
| `plan` | `plan/SKILL.md` | pipeline | ✅ | Unified planning: decompose to 2-5min tasks |
| `prd-author` | `prd-author/SKILL.md` | pipeline | ✅ | Stakeholder-facing requirements authoring |
| `product-product-discovery` | `product-product-discovery/SKILL.md` | product | ✅ | User stories, RICE, roadmap, MVP scoping |
| `pull-request` | `pull-request/SKILL.md` | workflow-utils | ✅ | Create structured GitHub PRs |
| `quality-gates-performance-profiling` | `quality-gates-performance-profiling/SKILL.md` | quality-gates | ✅ | Measure-first performance diagnosis. Profile → isolate → handoff |
| `quality-gates-systematic-debugging` | `quality-gates-systematic-debugging/SKILL.md` | quality-gates | ✅ | Root-cause analysis: reproduce → isolate → fix → verify |
| `receiving-code-review` | `receiving-code-review/SKILL.md` | pipeline | ✅ | Evaluate code review feedback with technical rigor — verify, ask, push back when wrong |
| `ralph-loop-wrapper` | `ralph-loop-wrapper/SKILL.md` | orchestration | ❌ (auto) | Infrastructure: wraps task execution in ralph loop |
| `retrospective` | `retrospective/SKILL.md` | pipeline | ✅ | Post-archive lessons capture |
| `rules-distill` | `rules-distill/SKILL.md` | workflow-utils | ✅ | Scans skills for repeated principles, elevates to rules/ with anti-abstraction guard |
| `sdd-analyze` | `sdd-analyze/SKILL.md` | pipeline | ✅ | Pre-apply consistency gate: cross-checks proposal/spec/design/tasks for coverage, contradictions, scope leaks, naming drift (inspired by spec-kit /speckit.analyze) |
| `sdd-apply` | `sdd-apply/SKILL.md` | orchestration | ❌ (auto) | SDD implement phase: writes code for assigned tasks |
| `sdd-checklist` | `sdd-checklist/SKILL.md` | pipeline | ✅ | Spec-completeness gate: validates spec.md for observable/unambiguous/bounded/testable REQs + Given/When/Then scenarios (inspired by spec-kit /speckit.checklist) |
| `sdd-debate` | `sdd-debate/SKILL.md` | orchestration | ❌ (auto) | Dual blind proposers + state-machine convergence. Auto-fires when `triage.json.debate_required` is true (v7.1) |
| `sdd-verify-diff` | `sdd-verify-diff/SKILL.md` | orchestration | ❌ (auto) | Per-file adversarial review fan-out. Auto-fires when `triage.json.per_diff_verify_required` is true (v7.1) |
| `search-first` | `search-first/SKILL.md` | workflow-utils | ✅ | Pre-coding gate: library + codebase scan → Adopt/Extend/Compose/Build |
| `session-manager` | `session-manager/SKILL.md` | orchestration | ❌ (auto) | Routing, classification, state read/write protocol |
| `skill-stocktake` | `skill-stocktake/SKILL.md` | workflow-utils | ✅ | Automated skill quality audit: Keep/Improve/Retire/Merge |
| `sop-reverse` | `sop-reverse/SKILL.md` | pipeline | ✅ | Reverse-engineer existing code before refactoring |
| `spec` | `spec/SKILL.md` | pipeline | ✅ | SDD spec phase: write acceptance criteria from proposal |
| `subagent-driven-development` | `subagent-driven-development/SKILL.md` | pipeline | ✅ | Dispatch expert subagents per task from plan |
| `tdd-workflow` | `tdd-workflow/SKILL.md` | pipeline | ✅ | Red-Green-Refactor gate: failing test required before any implementation |
| `using-git-worktrees` | `using-git-worktrees/SKILL.md` | pipeline | ✅ | Isolated branch via git worktree |
| `verify` | `verify/SKILL.md` | pipeline | ✅ | Two-pass verification: evidence gate + SDD review |
| `writing-skills` | `writing-skills/SKILL.md` | meta | ✅ | TDD methodology applied to skill authoring |

---

## Legacy paths (kept for backward compat, content migrated)

| Old Path | New Location |
|----------|-------------|
| `_core/anti-rationalization/` | `rules/quality-enforcement.md` |
| `_core/verification-enforcement/` | `rules/quality-enforcement.md` |
| `_core/context-awareness/` | `rules/context-awareness.md` |
| `_core/decision-memory/` | `rules/` (reference only — logic in orchestration) |
| `_core/session-state/` | `session-manager/SKILL.md` |
| `_orchestration/session-orchestrator/` | `session-manager/SKILL.md` |
| `_orchestration/ralph-loop-wrapper/` | `ralph-loop-wrapper/SKILL.md` |
| `workflow/writing-plans/` | `plan/SKILL.md` |
| `sop/sop-planning/` | `plan/SKILL.md` |
| `sop/sop-code-assist/` | `generate/SKILL.md` |
| `workflow/verification-before-completion/` | `verify/SKILL.md` |
| `sop/sop-reviewer/` | `verify/SKILL.md` |
| `workflow/brainstorming/` | `brainstorming/SKILL.md` |
| `workflow/subagent-driven-development/` | `subagent-driven-development/SKILL.md` |
| `workflow/using-git-worktrees/` | `using-git-worktrees/SKILL.md` |
| `workflow/finishing-a-development-branch/` | `finishing-a-development-branch/SKILL.md` |
| `sop/sop-reverse/` | `sop-reverse/SKILL.md` |
| `pipeline/*.md` | `<skill>/SKILL.md` (Ola 22 flattening 2026-05-11) |
| `api-design-principles/` | `domain-api-design-principles/SKILL.md` |
| `architecture-patterns/` | `domain-architecture-patterns/SKILL.md` |
| `resilience-patterns/` | `domain-resilience-patterns/SKILL.md` |
| `nestjs-code-reviewer/` | `domain-nestjs-code-reviewer/SKILL.md` |
| `security-review/` | `domain-security-review/SKILL.md` |
| `react-best-practices/` | `domain-react-best-practices/SKILL.md` |
| `frontend-design/` | `domain-frontend-design/SKILL.md` |
| `workflow/commit/` | `commit/SKILL.md` |
| `workflow/pull-request/` | `pull-request/SKILL.md` |
| `workflow/changelog/` | `changelog/SKILL.md` |
| `workflow/deep-research/` | `deep-research/SKILL.md` |
| `core/banned-phrases.md` | `rules/banned-phrases.md` (Ola 25 flatten 2026-05-25) |
| `core/context-awareness.md` | `rules/context-awareness.md` (Ola 25 flatten 2026-05-25) |
| `core/quality-enforcement.md` | `rules/quality-enforcement.md` (Ola 25 flatten 2026-05-25) |
| `domain/<name>/SKILL.md` | `domain-<name>/SKILL.md` (Ola 25 flatten 2026-05-25) |
| `quality-gates/<name>/SKILL.md` | `quality-gates-<name>/SKILL.md` (Ola 25 flatten 2026-05-25) |
| `product/product-discovery/` | `product-product-discovery/SKILL.md` (Ola 25 flatten 2026-05-25) |
| `devrel/api-documentation/` | `devrel-api-documentation/SKILL.md` (Ola 25 flatten 2026-05-25) |
| `workflow-utils/<name>.md` | `<name>/SKILL.md` (Ola 25 flatten 2026-05-25) |
| `orchestration/{session-manager,ralph-loop-wrapper,iterative-retrieval}.md` | `<name>/SKILL.md` (Ola 25 flatten 2026-05-25) |

---

## Compressed Registry (for embedding in subagent prompts)

```
PIPELINE: plan, generate, verify, brainstorming, tdd-workflow, subagent-driven-development,
          using-git-worktrees, finishing-a-development-branch, sop-reverse,
          adr-review, adr-write, prd-author, retrospective, issue-creation, spec,
          receiving-code-review
ORCH: session-manager*, ralph-loop-wrapper*, iterative-retrieval*,
      sdd-apply*, sdd-debate*, sdd-verify-diff*, consult-decide, consult-critique,
      dispatching-parallel-agents
DOMAIN: domain-api-design-principles, domain-architecture-patterns, domain-resilience-patterns,
        domain-nestjs-code-reviewer, domain-security-review, domain-react-best-practices,
        domain-frontend-design, domain-gsap, domain-discovery-before-code,
        domain-shadcn-component-install, domain-a11y-contrast-check,
        domain-design-tokens-extract, domain-design-system-doc, domain-page-transitions-barba,
        domain-ios-hig-mobile, domain-spline-3d-embed, domain-behavioral-contracts
QUALITY-GATES: quality-gates-systematic-debugging, agent-self-diagnosis,
               quality-gates-performance-profiling
DEVREL: devrel-api-documentation
PRODUCT: product-product-discovery
UTILS: commit, pull-request, changelog, deep-research, search-first, rules-distill, skill-stocktake
Total: 46 invokable + 8 auto-injected = 54 active skills (v7 flat layout, 2026-05-29)
(* = auto-injected)
```
