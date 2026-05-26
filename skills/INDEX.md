# Skills INDEX — Agent007 v6 (flat layout)

> Full registry of all skills. Path is relative to `Agent007/skills/`.
> All skills are at depth-1 (`<name>/SKILL.md`). Prefix convention: `<category>-<name>/SKILL.md` for namespaced skills.
> Updated: 2026-05-26 (flatten-skills-to-anthropic-spec migration — mirror from `.claude/`)

---

## All Skills (alphabetical)

| Skill name | Path | Category | Invokable | Description |
|---|---|---|---|---|
| `adr-review` | `adr-review/SKILL.md` | pipeline | ✅ | Periodic check on existing ADRs for aging |
| `adr-write` | `adr-write/SKILL.md` | pipeline | ✅ | Record architectural decisions with multi-change implications |
| `agent-self-diagnosis` | `agent-self-diagnosis/SKILL.md` | quality-gates | ✅ | 4-phase loop recovery: Capture → Diagnose → Recover → Report |
| `brainstorming` | `brainstorming/SKILL.md` | pipeline | ✅ | Socratic requirements exploration before implementation |
| `changelog` | `changelog/SKILL.md` | workflow-utils | ✅ | Generate changelog from git history |
| `commit` | `commit/SKILL.md` | workflow-utils | ✅ | Pipe-delimited commit: Tipo\|IdTarea\|YYYYMMDD\|Desc |
| `consult-critique` | `consult-critique/SKILL.md` | orchestration | ✅ (via `/consult`) | Planning-only adversarial review of pasted proposals |
| `consult-decide` | `consult-decide/SKILL.md` | orchestration | ✅ (via `/consult`) | Planning-only dual-blind-proposer for option decisions |
| `deep-research` | `deep-research/SKILL.md` | workflow-utils | ✅ | 4-phase systematic research methodology |
| `devrel-api-documentation` | `devrel-api-documentation/SKILL.md` | devrel | ✅ | OpenAPI, Swagger, developer portals, API reference |
| `domain-a11y-contrast-check` | `domain-a11y-contrast-check/SKILL.md` | domain | ✅ | Run Node.js script to verify WCAG AA color contrast. Exits 1 if <4.5:1 |
| `domain-api-design-principles` | `domain-api-design-principles/SKILL.md` | domain | ✅ | NestJS REST API design and audit |
| `domain-architecture-patterns` | `domain-architecture-patterns/SKILL.md` | domain | ✅ | Clean Architecture, DDD, Bounded Contexts |
| `domain-design-system-doc` | `domain-design-system-doc/SKILL.md` | domain | ✅ | Generate canonical 9-section DESIGN.md |
| `domain-design-tokens-extract` | `domain-design-tokens-extract/SKILL.md` | domain | ✅ | WebFetch a referent URL → extract palette/typography/spacing → write tokens |
| `domain-discovery-before-code` | `domain-discovery-before-code/SKILL.md` | domain | ✅ | Anti-convergence gate: referent fetch + style choice + state design BEFORE code |
| `domain-frontend-design` | `domain-frontend-design/SKILL.md` | domain | ✅ | High-quality UI/UX design and implementation |
| `domain-gsap` | `domain-gsap/SKILL.md` | domain | ✅ | GSAP: tweens, timelines, ScrollTrigger, plugins, React, utils, performance |
| `domain-ios-hig-mobile` | `domain-ios-hig-mobile/SKILL.md` | domain | ✅ | Mobile-first components following Apple HIG for web |
| `domain-karpathy` | `domain-karpathy/SKILL.md` | domain | ✅ | Karpathy behavioral contracts deep-dive |
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
| `plan` | `plan/SKILL.md` | pipeline | ✅ | Unified planning: decompose to 2-5min tasks |
| `prd-author` | `prd-author/SKILL.md` | pipeline | ✅ | Stakeholder-facing requirements authoring |
| `product-product-discovery` | `product-product-discovery/SKILL.md` | product | ✅ | User stories, RICE, roadmap, MVP scoping |
| `pull-request` | `pull-request/SKILL.md` | workflow-utils | ✅ | Create structured GitHub PRs |
| `quality-gates-performance-profiling` | `quality-gates-performance-profiling/SKILL.md` | quality-gates | ✅ | Measure-first performance diagnosis. Profile → isolate → handoff |
| `quality-gates-systematic-debugging` | `quality-gates-systematic-debugging/SKILL.md` | quality-gates | ✅ | Root-cause analysis: reproduce → isolate → fix → verify |
| `retrospective` | `retrospective/SKILL.md` | pipeline | ✅ | Post-archive lessons capture |
| `rules-distill` | `rules-distill/SKILL.md` | workflow-utils | ✅ | Scans skills for repeated principles, elevates to rules/ |
| `sdd-debate` | `sdd-debate/SKILL.md` | orchestration | ❌ (auto) | Dual blind proposers + state-machine convergence. Auto-fires when `triage.json.debate_required` is true (v7.1) |
| `sdd-verify-diff` | `sdd-verify-diff/SKILL.md` | orchestration | ❌ (auto) | Per-file adversarial review fan-out. Auto-fires when `triage.json.per_diff_verify_required` is true (v7.1) |
| `search-first` | `search-first/SKILL.md` | workflow-utils | ✅ | Pre-coding gate: library + codebase scan → Adopt/Extend/Compose/Build |
| `skill-stocktake` | `skill-stocktake/SKILL.md` | workflow-utils | ✅ | Automated skill quality audit: Keep/Improve/Retire/Merge |
| `sop-reverse` | `sop-reverse/SKILL.md` | pipeline | ✅ | Reverse-engineer existing code before refactoring |
| `subagent-driven-development` | `subagent-driven-development/SKILL.md` | pipeline | ✅ | Dispatch expert subagents per task from plan |
| `tdd-workflow` | `tdd-workflow/SKILL.md` | pipeline | ✅ | Red-Green-Refactor gate: failing test required before any implementation |
| `using-git-worktrees` | `using-git-worktrees/SKILL.md` | pipeline | ✅ | Isolated branch via git worktree |
| `verify` | `verify/SKILL.md` | pipeline | ✅ | Two-pass verification: evidence gate + SDD review |

Total: 47 SKILL.md files at depth-2.

---

## Auto-loaded orchestration patterns (NOT invokable as skills)

These were previously bare `.md` files under `skills/orchestration/`. They are auto-injected context for the orchestrator, not invoked via `Skill('<name>')`. Relocated to `docs/orchestration/`:

| File | Purpose |
|------|---------|
| `docs/orchestration/iterative-retrieval.md` | Progressive context refinement for subagent spawning: 3-round minimum-context protocol |
| `docs/orchestration/ralph-loop-wrapper.md` | Infrastructure: wraps task execution in ralph loop |
| `docs/orchestration/session-manager.md` | Routing, classification, state read/write protocol |

References previously under `skills/orchestration/references/` are now in `docs/orchestration-references/`.

---

## Auto-injected rules (was `skills/core/`)

These live at `rules/<name>.md` and are always-on:

| File | Purpose |
|------|---------|
| `rules/banned-phrases.md` | Quick-ref: banned phrases → required replacements |
| `rules/context-awareness.md` | Always read state before assuming |
| `rules/quality-enforcement.md` | Anti-rationalization + verification enforcement |

Supporting references at `rules/references/{configuration,detection-algorithm,examples}.md`.

---

## Legacy paths (kept for backward compat, content migrated)

| Old Path | New Location |
|----------|-------------|
| `skills/core/banned-phrases.md` | `rules/banned-phrases.md` (Ola 25 flatten 2026-05-26) |
| `skills/core/context-awareness.md` | `rules/context-awareness.md` |
| `skills/core/quality-enforcement.md` | `rules/quality-enforcement.md` |
| `skills/core/references/*.md` | `rules/references/*.md` |
| `skills/domain/<name>/SKILL.md` | `skills/domain-<name>/SKILL.md` |
| `skills/quality-gates/<name>/SKILL.md` | `skills/quality-gates-<name>/SKILL.md` |
| `skills/quality-gates/agent-self-diagnosis.md` | `skills/agent-self-diagnosis/SKILL.md` (wrapped) |
| `skills/product/product-discovery/` | `skills/product-product-discovery/SKILL.md` |
| `skills/devrel/api-documentation/` | `skills/devrel-api-documentation/SKILL.md` |
| `skills/workflow-utils/<name>.md` | `skills/<name>/SKILL.md` (wrapped) |
| `skills/orchestration/{session-manager,ralph-loop-wrapper,iterative-retrieval}.md` | `docs/orchestration/<name>.md` (auto-injected docs, NOT skills) |
| `skills/orchestration/references/*.md` | `docs/orchestration-references/*.md` |

---

## Compressed Registry (for embedding in subagent prompts)

```
PIPELINE: plan, generate, verify, brainstorming, tdd-workflow, subagent-driven-development,
          using-git-worktrees, finishing-a-development-branch, sop-reverse,
          adr-review, adr-write, prd-author, retrospective, issue-creation
ORCH: sdd-debate*, sdd-verify-diff*, consult-decide, consult-critique
DOMAIN: domain-api-design-principles, domain-architecture-patterns, domain-resilience-patterns,
        domain-nestjs-code-reviewer, domain-security-review, domain-react-best-practices,
        domain-frontend-design, domain-gsap, domain-discovery-before-code,
        domain-shadcn-component-install, domain-a11y-contrast-check,
        domain-design-tokens-extract, domain-design-system-doc, domain-page-transitions-barba,
        domain-ios-hig-mobile, domain-spline-3d-embed, domain-karpathy
QUALITY-GATES: quality-gates-systematic-debugging, agent-self-diagnosis,
               quality-gates-performance-profiling
DEVREL: devrel-api-documentation
PRODUCT: product-product-discovery
UTILS: commit, pull-request, changelog, deep-research, search-first, rules-distill, skill-stocktake
Total: 45 invokable + 2 auto-injected = 47 active skills (v6 flat layout)
(* = auto-injected)
AUTO-DOCS (not skills): docs/orchestration/{session-manager,ralph-loop-wrapper,iterative-retrieval}.md
```
