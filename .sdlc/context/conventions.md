# Conventions — Agent007 Plugin

## Commit Format (pipe-delimited)
```
tipo|TASK-ID|YYYYMMDD|descripción imperativa
```
Tipos: feat · fix · refactor · docs · test · chore · perf · style · ci · build · revert · wip
Example: `feat|GAP-007|20260428|Add web-distill PreToolUse hook`

## Branch Naming
- feat/<short-kebab>
- fix/<issue-or-desc>
- refactor/<scope>

## Hook Authoring
- Hooks = deterministic (non-negotiable behavior → hook)
- CLAUDE.md rules = probabilistic (contextual judgment → rule)
- Skills = multi-step on-demand protocols
- Hooks MUST use stdlib only — no pip installs
- Exit 0 = allow · Exit non-zero = block
- NEVER block on parse errors — passthrough on invalid input
- Performance budget: < 30ms per hook

## Skill Structure
- Frontmatter: name, description, invokable, version
- Phases: numbered steps with clear inputs/outputs
- Guardrails: explicit list of what the skill blocks or requires
- No external dependencies

## Agent Definitions
- model: opus (architecture/security/product) · sonnet (default) · haiku (boilerplate)
- tool_profile: minimal · coding · full
- triggers[]: terms the LLM uses for routing — not a keyword table, used as descriptions
- forbidden[]: explicit list of things the agent must NOT do

## File Length Limits
- Hooks: 200 lines max
- Skills: no hard limit, but split at logical phases
- Rules: 50 lines max per file

## No External Attribution
- NEVER add Co-Authored-By to commits
- NEVER add tool branding to PRs or commits
