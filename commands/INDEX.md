# Commands INDEX — Agent007 v6

**Commands** son orquestadores de alto nivel. Para skills invocables (commit, pull-request, changelog, deep-research, etc.) ver `.claude/skills/INDEX.md`.

| Command | Description |
|---------|-------------|
| `/dev "task"` | Master command: classify, route, execute autonomously |
| `/consult "question"` | Expert consultation with skill injection |
| `/prompt-gen "objective"` | Convert vague intent into precision prompt |
| `/ralph-loop "task"` | Autonomous loop until COMPLETE |
| `/orchestrate <workflow> "task"` | Multi-agent workflow with HANDOFF protocol (feature/bugfix/refactor/security/cleanup) |
| `/instinct-status` | Show Instinct Learning System status and active instincts |
| `/evolve` | Promote instincts to permanent skills |
| `/security-scan` | Agent007 security audit (OWASP + codebase scan) |

---

## Migrated to /skills (v6)

| Old command | New location |
|---|---|
| `/commit` | `Skill('commit')` → `skills/workflow-utils/commit.md` |
| `/pull-request` | `Skill('pull-request')` → `skills/workflow-utils/pull-request.md` |
| `/changelog` | `Skill('changelog')` → `skills/workflow-utils/changelog.md` |
| `/deep-research` | `Skill('deep-research')` → `skills/workflow-utils/deep-research.md` |

Single source of truth in `/skills`. Use `Skill('<name>')` to invoke.
