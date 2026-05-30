# PluginClaude — Project Navigation Map

**Purpose**: this file is the navigation index. CLAUDE.md is identity + behavior; this file tells you WHERE things live. Hot-loaded after CLAUDE.md so the agent doesn't have to grep blindly.

> Pattern stolen from Matt Pocock's skills repo: separate identity (CLAUDE.md) from project navigation (CONTEXT.md). Each file has one job.

---

## Repo at a glance

```
PluginClaude/
├── .claude/                # The plugin itself (THIS is what we're building)
│   ├── CLAUDE.md           # Identity, core rules, routing — HOT loaded
│   ├── CONTEXT.md          # ← THIS FILE — HOT loaded
│   ├── settings.json       # Hooks registry, permissions
│   ├── agents/             # 10 specialist agents (architect, security-expert, etc.)
│   ├── commands/           # High-level orchestrators ONLY (dev, orchestrate, ralph-loop, etc.)
│   ├── skills/             # Invokable units of behavior — THE primary extension surface
│   ├── hooks/              # Deterministic enforcers (Python scripts)
│   ├── rules/              # Declarative project conventions (typescript, security, git, etc.)
│   ├── scripts/            # Node.js CLI tools (instinct-engine, security-scan, wave-scheduler)
│   └── instincts/          # User preference YAMLs (meta-config)
├── .sdlc/                  # Spec-Driven Development state
│   ├── context/            # Project tech-stack, conventions
│   └── state/              # Session state, context-budget, instinct logs
└── docs/                   # External-facing documentation
```

---

## Where to look for what

| Need to do | Look in | Key files |
|---|---|---|
| Invoke a skill | `.claude/skills/INDEX.md` | Trigger keywords → skill path |
| Add a new skill | `.claude/skills/<name>/SKILL.md` (depth-1) | Use `Skill('skill-creator')` |
| Add deterministic enforcement | `.claude/harness/` + `.claude/settings.json` | See `rules/hooks-authoring.md` |
| Modify routing | `.claude/CLAUDE.md` `<routing>` section | Don't put rules here that should be hooks |
| Update project conventions | `.claude/rules/<topic>.md` | Loaded lazily by skills that need them |
| Run an agent | `.claude/agents/<name>.md` | Trigger keywords + tools allowlist |
| Trace session state | `.sdlc/state/session.md` | Updated by state-sync hook |
| Trace context budget | `.sdlc/state/context-budget.json` | Updated by context-engine hook |

---

## Skill categories

| Category | Path pattern | Loading | Examples |
|---|---|---|---|
| rules | `rules/*.md` | auto-inject (always on) | quality-enforcement, banned-phrases, context-awareness |
| pipeline | `skills/<name>/SKILL.md` (depth-1) | invokable on demand | plan, generate, verify, tdd-workflow |
| orchestration | `skills/<name>/SKILL.md` (depth-1) | invokable / auto | sdd-debate, sdd-verify-diff, session-manager, iterative-retrieval |
| domain | `skills/domain-<name>/SKILL.md` | invokable | domain-api-design-principles, domain-security-review, domain-behavioral-contracts |
| quality-gates | `skills/quality-gates-<name>/SKILL.md` | invokable | quality-gates-systematic-debugging, quality-gates-performance-profiling |
| workflow-utils | `skills/<name>/SKILL.md` | invokable | commit, pull-request, changelog, deep-research |
| product/devrel | `skills/<prefix>-<name>/SKILL.md` | invokable | product-product-discovery, devrel-api-documentation |

---

## Hook events and their handlers

| Event | Handlers |
|---|---|
| `SessionStart` | memory-check (manifest staleness), memory-decay (memory file aging), rtk-bootstrap |
| `UserPromptSubmit` | constraint-reinforcement |
| `PreToolUse/Agent` | sdd-guard, context-engine, subagent-context |
| `PreToolUse/Write\|Edit` | safety-guard, mutation-guard, tool-policy-guard, **path-existence-guard (NEW)** |
| `PreToolUse/Bash` | rtk-rewrite, **tool-allowlist-guard (NEW)** |
| `PreToolUse/Config` | config-guard, block-no-verify |
| `PostToolUse/*` | tool-loop-detection, web-distill, context-window-guard |
| `SubagentStart` | transcript-policy, subagent-context |
| `Stop` | state-sync, context-engine (dispose) |

---

## Files NOT to touch without thinking twice

| File | Why |
|---|---|
| `.claude/settings.json` | Wires hooks to events. Breaking this breaks everything. |
| `.claude/CLAUDE.md` | The identity prompt. Always-loaded. |
| `.claude/rules/*.md` | Auto-injected. Bugs leak everywhere. |
| `.sdlc/state/session.md` | Active task state. Concurrent writes corrupt it. |

---

## When in doubt

1. `Skill('skill-stocktake')` → audits skills for redundancy, freshness, broken refs
2. `mem_search` → check what was decided in past sessions before re-deciding
3. Read `rules/hooks-authoring.md` before adding rules to CLAUDE.md (often they should be hooks)
