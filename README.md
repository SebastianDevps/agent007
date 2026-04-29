# Agent007 v5.1

> Intelligent development orchestration for Claude Code.
> 10 expert agents · 35 skills · 21 deterministic hooks · LLM-native routing · SDD-enforced pipeline

---

## What it does

Agent007 turns Claude Code into a structured engineering team. Instead of prompting one model, you get a full development pipeline: specialized agents routed by intent, quality gates enforced at the tool level (not the instruction level), and a spec-driven workflow that catches design problems before implementation.

**The core bet**: hooks are deterministic, CLAUDE.md rules are probabilistic. Agent007 enforces everything non-negotiable via hooks — safety, anti-reward-hacking, context budgets, loop detection, secret scanning — and uses rules only for preferences and style.

---

## Install

```bash
/plugin marketplace add SebastianDevps/agent007-marketplace
/plugin install agent007@agent007-marketplace
```

Requires Claude Code CLI or the Claude desktop app.

---

## The 10 expert agents

| Agent | Model | Domain |
|-------|-------|--------|
| `backend-db-expert` | Opus | APIs, NestJS, TypeORM, PostgreSQL, Redis, microservices |
| `frontend-ux-expert` | Sonnet | React, Next.js, Tailwind, GSAP, accessibility, Core Web Vitals |
| `platform-expert` | Sonnet | CI/CD, Docker, Jest, Playwright, Kubernetes, monitoring |
| `product-expert` | Opus | RICE, user stories, roadmap, MVP scoping, product discovery |
| `security-expert` | Opus | OWASP Top 10, JWT, threat modeling, GDPR, SOC2 |
| `code-reviewer` | Sonnet | Code quality — CRITICAL/HIGH/MEDIUM/LOW taxonomy |
| `loop-operator` | Sonnet | Ralph loop lifecycle, stall detection, cost drift monitoring |
| `refactor-cleaner` | Sonnet | Dead code detection, batch removal, safe refactoring |
| `architect` | Opus | System design, ADR, hexagonal/clean architecture, DDD |
| `performance-optimizer` | Sonnet | Bundle, N+1, Lighthouse, LCP/CLS/TTI, cache strategy |

Routing is LLM-native: the orchestrator reads agent descriptions and matches by intent — no keyword table to maintain.

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

## 35 active skills

**Pipeline** (9): `plan` · `generate` · `verify` · `brainstorming` · `tdd-workflow` · `subagent-driven-development` · `using-git-worktrees` · `finishing-a-development-branch` · `sop-reverse`

**Core — always active** (3): `quality-enforcement` · `banned-phrases` · `context-awareness`

**Orchestration — always active** (4): `session-manager` · `ralph-loop-wrapper` · `state-sync` · `iterative-retrieval`

**Domain** (8): `api-design-principles` · `architecture-patterns` · `resilience-patterns` · `nestjs-code-reviewer` · `security-review` · `react-best-practices` · `frontend-design` · `gsap`

**Quality gates** (2): `systematic-debugging` · `agent-self-diagnosis`

**DevRel** (1): `api-documentation`

**Product** (1): `product-discovery`

**Workflow utils** (7): `commit` · `pull-request` · `changelog` · `deep-research` · `search-first` · `rules-distill` · `skill-stocktake`

---

## 21 deterministic hooks

| Hook | Trigger | What it enforces |
|------|---------|-----------------|
| `memory-check.py` | SessionStart | Detects manifest changes via MD5 |
| `rtk-bootstrap.py` | SessionStart | Token compression binary setup |
| `memory-decay.py` | SessionStart | Marks MEMORY.md entries stale at 30d, archives at 60d |
| `constraint-reinforcement.py` | UserPromptSubmit | Reinjects core rules at every turn |
| `subagent-context.py` | SubagentStart | Injects project context + skill registry into every subagent |
| `transcript-policy.py` | SubagentStart | Model-tier directives: haiku → concise, opus → deep-analysis |
| `state-sync.py` | Stop | Writes session state to `.sdlc/state/session.md` |
| `context-engine.py` | PreToolUse/Agent + Stop | Blocks Agent spawns at ≥80% context budget |
| `web-distill.py` | PreToolUse/WebFetch | Strips HTML noise, returns semantic text only (≤10KB) |
| `tool-policy-guard.py` | PreToolUse/Edit\|Write | Enforces tool_profile per active agent |
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

**Hook runtime profiles** — control overhead via `CLAUDE_HOOK_PROFILE`:

| Profile | Active hooks | Use when |
|---------|-------------|----------|
| `minimal` | safety-guard, sdd-guard, block-no-verify, pre-commit-guard, config-guard | Rapid prototyping |
| `standard` (default) | All 21 | Normal sessions |
| `strict` | All 21 | Pre-merge, security reviews |

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

## RTK — Token compression

All eligible Bash commands are rewritten automatically via `rtk-rewrite.py`:

Covered: `git` · `npm` · `pnpm` · `cargo` · `pytest` · `vitest` · `docker` · `kubectl` · `bun` · `npx` · `eslint` · `tsc` · `jest` · `playwright` · `go` · `rspec` · `curl`

Ultra-compact mode auto-applied to: `git log` · `docker ps` · `docker logs` · `kubectl` · `npm list`

---

## Session persistence

`.sdlc/state/session.md` is written silently after every task and at session end.

- Active task ≠ "ninguna" → shows resume banner at next session start
- Active plans in `.sdlc/tasks/active-plan.md`
- Architecture decisions in `.sdlc/context/`

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
├── agents/          # 10 agent definitions (opus/sonnet)
├── commands/        # Slash commands (/dev, /consult, /ralph-loop, /sdd-*)
├── hooks/           # 21 deterministic quality gates
├── rules/           # Code conventions (TypeScript, security, git, patterns)
├── scripts/         # CLI utilities (wave-scheduler, context-budget)
├── skills/          # 35 skills organized by domain
├── CLAUDE.md        # Orchestrator instructions (auto-loaded) ← source of truth
├── GETTING_STARTED.md
├── README.md
└── settings.json    # Hook registration, permissions, context includes

.sdlc/
├── context/         # tech-stack.md, conventions.md, project-overview.md
│                    # (injected into every subagent via subagent-context.py)
├── state/           # session.md, context-budget.json, loop-state.json
└── tasks/           # Active plans
```

---

## Model routing

| Tier | Model | When |
|------|-------|------|
| Haiku | `claude-haiku-4-5-20251001` | Classification, boilerplate, narrow single-file edits |
| Sonnet | `claude-sonnet-4-6` | Implementation, refactors, API design, debugging — default |
| Opus | `claude-opus-4-6` | Architecture, root-cause analysis, multi-file invariants, security |

Agent defaults: Opus → backend-db-expert, product-expert, security-expert, architect · Sonnet → all others.

---

## Requirements

- Claude Code CLI (any tier) or Claude desktop app
- Python 3.8+ (for hook scripts)
- macOS, Linux, or Windows (WSL recommended for hooks)
