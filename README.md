# Agent007 v6.0.0

> Intelligent development orchestration for Claude Code.
> 8 expert agents · 44 skills · 26 deterministic hooks · LLM-native routing · SDD-enforced pipeline

---

## What it does

Agent007 turns Claude Code into a structured engineering team. Instead of prompting one model, you get a full development pipeline: specialized agents routed by intent, quality gates enforced at the tool level (not the instruction level), and a spec-driven workflow that catches design problems before implementation.

**The core bet**: hooks are deterministic, CLAUDE.md rules are probabilistic. Agent007 enforces everything non-negotiable via hooks — safety, anti-reward-hacking, context budgets, loop detection, secret scanning, path existence, frontend discovery — and uses rules only for preferences and style.

**v6.0.0 in one line**: same pipeline, less weight. Eager-loaded context dropped from ~7300 lines to 1195 (-84%), 18 silently oversized files brought to zero, and 72 references now lazy-load on demand.

---

## Install

```bash
/plugin marketplace add SebastianDevps/agent007-marketplace
/plugin install agent007@agent007-marketplace
```

Requires Claude Code CLI or the Claude desktop app.

---

## The 8 expert agents

| Agent | Model | Domain |
|-------|-------|--------|
| `backend-db-expert` | Opus | APIs, NestJS, TypeORM, PostgreSQL, Redis, microservices |
| `frontend-ux-expert` | Sonnet | React, Next.js, Tailwind, GSAP, accessibility, Core Web Vitals — **executor with anti-convergence** |
| `platform-expert` | Sonnet | CI/CD, Docker, Jest, Playwright, Kubernetes, monitoring |
| `product-expert` | Opus | RICE, user stories, roadmap, MVP scoping, product discovery |
| `security-expert` | Opus | OWASP Top 10, JWT, threat modeling, GDPR, SOC2 |
| `code-reviewer` | Sonnet | Code quality — CRITICAL/HIGH/MEDIUM/LOW taxonomy |
| `loop-operator` | Sonnet | Ralph loop lifecycle, stall detection, cost drift monitoring |
| `refactor-cleaner` | Sonnet | Dead code detection, batch removal, safe refactoring |

Routing is LLM-native: the orchestrator reads agent descriptions and matches by intent — no keyword table to maintain.

**Removed in v6.0.0** — capabilities preserved as skills:

| Removed agent | Replacement |
|---------------|-------------|
| `architect` | `Skill('architecture-patterns')` |
| `performance-optimizer` | `Skill('performance-profiling')` |

The agents were over-broad — every concrete task they handled now lives in a focused skill that can be composed by any agent.

---

## Frontend executor with anti-convergence

`frontend-ux-expert` no longer just validates — it builds. Four modes:

| Mode | When |
|------|------|
| `BUILDER` (default) | Implement components, styles, transitions |
| `PLANNER` | Break down a UI ticket before any code |
| `CONSULTANT` | Answer design/UX questions without writing |
| `REVIEWER` | Audit existing UI for a11y, tokens, system fit |

The `frontend-discovery-gate.py` hook blocks Edit/Write on `.tsx · .jsx · .css · .html · .svelte · .vue · .astro` until a recent discovery output exists. No more agents converging on identical Tailwind soup without first looking at design tokens or existing components.

Eight new actionable frontend skills:

`discovery-before-code` · `shadcn-component-install` · `a11y-contrast-check` (Node WCAG script) · `design-tokens-extract` · `design-system-doc` (9-section template) · `page-transitions-barba` · `ios-hig-mobile` · `spline-3d-embed`

---

## Pipeline

Two paths. No ambiguity.

```
Trivial  → Skill('generate') → Skill('verify') → done
           (single-file edit, no new behavior, no public surface change)

Substantial → SDD: proposal → spec → design → tasks → apply → verify → archive
              (new behavior, multi-file, public surface, refactor, any high/critical risk)
```

When in doubt, SDD. Over-planning a small change costs one extra round. Under-planning a substantial one can cost a week.

---

## 44 active skills

**Pipeline** (9): `plan` · `generate` · `verify` · `brainstorming` · `tdd-workflow` · `subagent-driven-development` · `using-git-worktrees` · `finishing-a-development-branch` · `sop-reverse`

**Core — always active** (3): `quality-enforcement` · `banned-phrases` · `context-awareness`

**Orchestration — always active** (4): `session-manager` · `ralph-loop-wrapper` · `state-sync` · `iterative-retrieval`

**Domain — backend & architecture** (6): `api-design-principles` · `architecture-patterns` · `resilience-patterns` · `nestjs-code-reviewer` · `security-review` · `performance-profiling`

**Domain — frontend** (10): `react-best-practices` · `frontend-design` · `gsap` · `discovery-before-code` · `shadcn-component-install` · `a11y-contrast-check` · `design-tokens-extract` · `design-system-doc` · `page-transitions-barba` · `ios-hig-mobile`

**Domain — frontend extras** (1): `spline-3d-embed`

**Quality gates** (2): `systematic-debugging` · `agent-self-diagnosis`

**DevRel** (1): `api-documentation`

**Product** (1): `product-discovery`

**Workflow utils** (7): `commit` · `pull-request` · `changelog` · `deep-research` · `search-first` · `rules-distill` · `skill-stocktake`

---

## 26 deterministic hooks

| Hook | Trigger | What it enforces |
|------|---------|-----------------|
| `memory-check.py` | SessionStart | Detects manifest changes via MD5 |
| `rtk-bootstrap.py` | SessionStart | Token compression binary setup |
| `memory-decay.py` | SessionStart | Marks MEMORY.md entries stale at 30d, archives at 60d |
| `session-recover.py` | SessionStart | Reads context-budget tail; injects prior-session summary if <4h old |
| `context-tick.py` | SessionStart + PostToolUse + Stop | Persists token telemetry to `.sdlc/state/context-budget.jsonl` |
| `constraint-reinforcement.py` | UserPromptSubmit | Reinjects core rules at every turn |
| `subagent-context.py` | SubagentStart | Injects project context + skill registry into every subagent |
| `transcript-policy.py` | SubagentStart | Model-tier directives: haiku → concise, opus → deep-analysis |
| `state-sync.py` | Stop | Writes session state to `.sdlc/state/session.md` |
| `context-engine.py` | PreToolUse/Agent + Stop | Blocks Agent spawns at ≥80% context budget |
| `web-distill.py` | PreToolUse/WebFetch | Strips HTML noise, returns semantic text only (≤10KB) |
| `tool-policy-guard.py` | PreToolUse/Edit\|Write | Enforces tool_profile per active agent |
| `tool-allowlist-guard.py` | PreToolUse/Bash | Skill-level bash whitelist (shadcn-style scoping) |
| `path-existence-guard.py` | PreToolUse/Edit\|Read | Blocks paths that don't exist (no more hallucinated files) |
| `frontend-discovery-gate.py` | PreToolUse/Edit\|Write | Blocks frontend file edits without recent discovery output |
| `sdd-guard.py` | PreToolUse+PostToolUse/Edit\|Write | Blocks reward-hacking (edits that reduce assertions) |
| `config-guard.py` | PreToolUse/Edit\|Write | Protects settings.json and hooks from accidental edits |
| `mutation-guard.py` | PreToolUse/Edit\|Write\|Bash | Fingerprints writes, skips exact duplicates silently |
| `safety-guard.py` | PreToolUse/Bash | Blocks destructive commands (rm -rf, force push, DROP TABLE) |
| `rtk-rewrite.py` | PreToolUse/Bash | Compresses git/npm/docker commands (~40% token reduction) |
| `block-no-verify.py` | PreToolUse/Bash | Blocks `git commit --no-verify` |
| `pre-commit-guard.py` | PreToolUse/Bash | Scans for secrets and .env files before commit |
| `context-window-guard.py` | PostToolUse | Warns when context window is filling |
| `tool-loop-detection.py` | PostToolUse | SHA-256 fingerprint loop detection, circuit breaker at 30× |
| `format-on-save.py` | PostToolUse/Edit\|Write | Auto-formats .ts .tsx .js .jsx .json .css .md |
| `notify.py` | Notification | macOS/Linux desktop notifications on task completion |

**Five new in v6.0.0**: `path-existence-guard`, `tool-allowlist-guard`, `frontend-discovery-gate`, `context-tick`, `session-recover`. The first three close real escape hatches the LLM was using. The last two power cross-session recovery.

**Hook runtime profiles** — control overhead via `CLAUDE_HOOK_PROFILE`:

| Profile | Active hooks | Use when |
|---------|-------------|----------|
| `minimal` | safety-guard, sdd-guard, block-no-verify, pre-commit-guard, config-guard | Rapid prototyping |
| `standard` (default) | All 26 | Normal sessions |
| `strict` | All 26 | Pre-merge, security reviews |

```bash
export CLAUDE_HOOK_PROFILE=minimal
```

---

## OpenClaw primitives

Five primitives run automatically on every session with no configuration needed:

| Primitive | What it does |
|-----------|-------------|
| `tool-loop-detection` | SHA-256 fingerprint window (30 calls). Warning at 10, circuit break at 30. 4h TTL auto-reset. |
| `context-engine` | Hard block at ≥80% context before Agent spawns. Advisory at 60-79%. |
| `mutation-guard` | Deduplicates writes by content hash. Silent skip on exact duplicates. |
| `memory-decay` | Marks stale memory entries automatically. No manual cleanup needed. |
| `web-distill` | All WebFetch calls go through semantic HTML distillation. ~99% noise reduction. |

---

## Telemetry & cross-session recovery

`context-tick.py` writes one line per tool call to `.sdlc/state/context-budget.jsonl`. `session-recover.py` reads the tail at SessionStart and, if the previous session ended <4h ago, emits an `additionalContext` summary so the next session resumes without you re-explaining anything.

`scripts/lifecycle/waste-report.py` audits the telemetry:

- Top files by load count
- Reference hit rate
- p95 token cost per tool call
- Never-loaded references (delete candidates)

The waste report is what drove the v6.0.0 -84% reduction. It's the same script you run going forward.

---

## Memory protocol — 3-layer disclosure

Inspired by claude-mem progressive disclosure. ~10× token savings vs single-fetch:

| Layer | Tool | Returns |
|-------|------|---------|
| 1. Discovery | `mem_search` | IDs + titles + score (no bodies) |
| 2. Context | `mem_timeline` | Chronology of related observations |
| 3. Detail | `mem_get_observation(id)` | Full untruncated body |

The orchestrator only descends layers when narrowing a candidate. Most queries resolve at layer 1.

---

## CLAUDE.md + CONTEXT.md (Pocock pattern)

`CLAUDE.md` is now identity, core rules, and routing only — nothing the model has to skim every turn that isn't actually decision-making.

`CONTEXT.md` is project navigation: where things live, hook events, lazy-loaded references. The orchestrator points to it instead of inlining it.

Result: smaller eager prompt, faster classification, fewer stale duplicates.

---

## RTK — Token compression

All eligible Bash commands are rewritten automatically via `rtk-rewrite.py`:

Covered: `git` · `npm` · `pnpm` · `cargo` · `pytest` · `vitest` · `docker` · `kubectl` · `bun` · `npx` · `eslint` · `tsc` · `jest` · `playwright` · `go` · `rspec` · `curl`

Ultra-compact mode auto-applied to: `git log` · `docker ps` · `docker logs` · `kubectl` · `npm list`

---

## Session persistence

`.sdlc/state/session.md` is written silently after every task and at session end.

- Active task ≠ "ninguna" → resume banner at next session start
- Telemetry tail (<4h) → `session-recover.py` auto-injects last-session summary
- Active plans in `.sdlc/tasks/active-plan.md`
- Architecture decisions in `.sdlc/context/`

---

## Lifecycle scripts

Under `scripts/lifecycle/`:

| Script | Purpose |
|--------|---------|
| `verify.sh` | End-to-end gate: settings, frontmatter, hooks, line caps, references — 6/6 must pass |
| `install.sh` | Idempotent install into a target project |
| `uninstall.sh` | Clean removal — settings restored, state preserved |
| `sync-to-public.sh` | Publish from working `.claude/` to `Agent007/` for marketplace |
| `test-hooks.py` | 13 fixture regression suite for hook payloads |
| `waste-report.py` | Audit telemetry: top files, hit rate, p95, never-loaded refs |

---

## CI

`.github/workflows/plugin-validate.yml` — six jobs, no excuses:

1. `settings.json` schema valid
2. Skill/agent/command frontmatter lint
3. Hook syntax (Python compile)
4. Line caps per file (200 lines, debt registered in `.line-cap-exemptions`)
5. All `@references` resolve to real files
6. `verify.sh` full pass

`.line-cap-exemptions` is an explicit debt register, not a silencer — every entry is a TODO with an owner.

---

## v6.0.0 metrics

| Metric | v5.1 | v6.0.0 | Change |
|--------|------|--------|--------|
| Eager-loaded total lines | ~7300 | 1195 | -84% |
| Auto-inject overhead lines | 1239 | 237 | -81% |
| Eager files >200 lines | 18 (silent) | 0 | fixed |
| Lazy-loaded references | — | 72 | new |
| Hook regression tests | — | 13 | new |
| `verify.sh` baseline | — | 6/6 pass · 0 warnings | new |

Removed in v6.0.0: `metrics/` directory, six orphaned legacy scripts (`test-loop-detection.py`, `test-memory-decay.py`, `test-mutation-guard.py`, `agent007-init.js`, `subagent-spawn.js`, `monitor-session.sh`) — about 916 lines of unreferenced code out.

---

## Entry commands

| Command | What it does |
|---------|-------------|
| `/dev "task"` | Auto-classifies and routes: simple → direct, medium → plan+subagents, complex → full pipeline |
| `/consult "question"` | Routes to the best expert agent by intent. Flags: `--quick` `--deep` `--experts X,Y` |
| `/ralph-loop "task"` | Autonomous loop until `<promise>COMPLETE</promise>`. Stall detection included. |
| `/sdd-new "change"` | Starts spec-driven development: proposal → spec → design → tasks → apply → verify |
| `/sdd-ff "change"` | Fast-forward: runs all planning phases (propose → spec → design → tasks) in sequence |

---

## File structure

```
.claude/
├── agents/          # 8 agent definitions (opus/sonnet)
├── commands/        # Slash commands (/dev, /consult, /ralph-loop, /sdd-*)
├── hooks/           # 26 deterministic quality gates
├── rules/           # Code conventions (TypeScript, security, git, patterns)
├── scripts/         # CLI utilities + lifecycle/ (verify, install, waste-report)
├── skills/          # 44 skills organized by domain
├── CLAUDE.md        # Identity, core rules, routing (lean — Pocock pattern)
├── CONTEXT.md       # Project navigation, hook events, lazy refs
├── GETTING_STARTED.md
├── README.md
└── settings.json    # Hook registration, permissions, context includes

.sdlc/
├── context/         # tech-stack.md, conventions.md, project-overview.md
├── state/           # session.md, context-budget.jsonl, loop-state.json
└── tasks/           # Active plans

.github/workflows/
└── plugin-validate.yml   # 6-job CI gate
```

---

## Model routing

| Tier | Model | When |
|------|-------|------|
| Haiku | `claude-haiku-4-5-20251001` | Classification, boilerplate, narrow single-file edits |
| Sonnet | `claude-sonnet-4-6` | Implementation, refactors, API design, debugging — default |
| Opus | `claude-opus-4-6` | Architecture, root-cause analysis, multi-file invariants, security |

Agent defaults: Opus → `backend-db-expert`, `product-expert`, `security-expert` · Sonnet → all others.

---

## Honest comparison

What Agent007 is good at: catching reward-hacking before it lands, refusing to edit hallucinated paths, blocking frontend code without discovery, persisting context across sessions, keeping the eager prompt small.

What it is not: a magic wand. The orchestrator still depends on the underlying model. Hooks reduce the blast radius of bad decisions; they don't make every decision good. If you don't write specs, SDD won't help you. If you ignore the discovery gate by re-running discovery to satisfy it, you're cheating yourself.

---

## Why it works

Hooks fire at the tool layer. The model can lie in prose; it cannot lie about a `PreToolUse` exit code. Every non-negotiable behavior is a hook. Everything contextual is a rule. Skills are protocols, not paragraphs of advice. That's it.

---

## Requirements

- Claude Code CLI (any tier) or Claude desktop app
- Python 3.8+ (for hook scripts)
- Node 18+ (for `a11y-contrast-check` and lifecycle scripts)
- macOS, Linux, or Windows (WSL recommended for hooks)

---

## Contributing

PRs welcome. Two hard rules:

1. `verify.sh` must stay 6/6 with zero warnings
2. New hooks need a fixture in `test-hooks.py` — no exceptions

The line cap is 200. If you can't fit, register the file in `.line-cap-exemptions` with an owner and a removal plan. Debt is allowed; hidden debt is not.
