# Git Workflow Rules

## Commit Format (Agent007 pipe-delimited)

```
tipo|TASK-ID|YYYYMMDD|descripción
```

**tipos válidos:** `feat` · `fix` · `refactor` · `docs` · `test` · `chore` · `perf` · `style` · `ci` · `build` · `revert` · `wip`

**Ejemplos:**
```
feat|GAP-007|20260329|Add pre-commit quality guard
fix|TASK-042|20260329|Resolve null deref in UserService.findById
refactor|TASK-015|20260329|Extract auth middleware to shared module
```

- TASK-ID must reference a real task (e.g. from TaskCreate, Linear, or GitHub issue)
- Description must be imperative mood: "Add", "Fix", "Remove" — not "Added", "Fixed"
- Max 72 characters for the full message
- NEVER write a commit message in plain English without the pipe format

## Branch Naming

```
feat/<short-description>     # new features
fix/<issue-or-description>   # bug fixes
refactor/<scope>             # refactors with no behavior change
docs/<scope>                 # documentation-only changes
```

**Ejemplos:**
```
feat/gap-007-pre-commit-guard
fix/null-deref-user-service
refactor/auth-middleware-extraction
```

- Use kebab-case — no spaces, no underscores
- Branch name must match the work being done (no `temp`, `test2`, `my-branch`)
- Delete feature branches after merging

## Merge Strategy

- **Feature branches** → squash merge into main/develop (clean linear history)
- **Hotfixes** → merge commit (preserve exact fix history for forensics)
- **Refactors** → squash merge (implementation details irrelevant to history)

## PR Title Format

```
tipo — Descripción imperativa en inglés (max 70 chars)
```

**Ejemplos:**
```
feat — Add user authentication with JWT refresh rotation
fix — Resolve null pointer in UserService.findById
refactor — Extract payment service to shared module
```

- `tipo` is the same set as commit types
- Description in imperative mood, English
- NEVER include ticket IDs, tool names, or branding in the title

## PR Template Requirements

Every PR must include (in this order):
1. **Summary**: What was built and why (1–3 bullets)
2. **Motivation**: Why this change was needed (link to issue/ticket)
3. **Test plan**: Concrete checklist of verification steps
4. **Breaking Changes**: None / description
5. **Rollback plan**: How to revert if this breaks production

NEVER include:
- `Co-Authored-By:` footers
- Tool attribution lines (`Generated with ...`, `🤖 ...`)
- External links or branding of any kind

## Immutable Rules

- NEVER force push to `main` or `develop`
- NEVER commit without tests passing (pre-commit guard enforces this)
- NEVER use `--no-verify` — fix the underlying problem instead
- NEVER commit `.env`, secrets, or credentials (pre-commit guard blocks this)
- NEVER add `Co-Authored-By` or tool attribution to commits or PRs
- ALWAYS commit atomically: one logical change per commit
- ALWAYS commit after each completed task in a multi-task workflow
