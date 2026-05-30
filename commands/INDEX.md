# Commands INDEX — Agent007 v7

**Commands** son orquestadores de alto nivel. Para skills invocables (commit, pull-request, changelog, deep-research, etc.) ver `.claude/skills/INDEX.md`.

| Command | Description |
|---------|-------------|
| `/dev "task"` | Master command: classify, route, execute autonomously |
| `/consult "question"` | Expert consultation with skill injection |
| `/prompt-gen "objective"` | Convert vague intent into precision prompt |
| `/ralph-loop "task"` | Autonomous loop until COMPLETE |
| `/orchestrate <workflow> "task"` | Multi-agent workflow with HANDOFF protocol (feature/bugfix/refactor/security/cleanup) |
| `/security-scan` | Agent007 security audit (OWASP + codebase scan) |

> Note: `/instinct-status` and `/evolve` were archived in Ola 24 (subsystem dormant). See `.sdlc/archive/v7-claude/instincts-subsystem/`.

---

## Migrated to /skills (v6)

| Old command | New location |
|---|---|
| `/commit` | `Skill('commit')` → `skills/commit/SKILL.md` |
| `/pull-request` | `Skill('pull-request')` → `skills/pull-request/SKILL.md` |
| `/changelog` | `Skill('changelog')` → `skills/changelog/SKILL.md` |
| `/deep-research` | `Skill('deep-research')` → `skills/deep-research/SKILL.md` |

Single source of truth in `/skills`. Use `Skill('<name>')` to invoke.
