---
name: commit
description: "Generate pipe-delimited commits: Tipo|IdTarea|YYYYMMDD|Descripción. Single source of truth — no /commands wrapper."
version: 3.0.0
preconditions:
  - changes_staged_or_unstaged
  - no_linting_errors
outputs:
  - name: commit_hash
    type: string
    format: "git log --oneline -1 output"
  - name: commit_message
    type: string
    format: "Tipo|IdTarea|YYYYMMDD|Descripción — max 72 chars total"
steps_count: 4
when:
  keywords: ["commit", "save changes", "checkpoint", "git commit", "end of task"]
format:
  pattern: "Tipo|IdTarea|YYYYMMDD|Descripción"
  types: [feat, fix, refactor, review, test, docs, chore, perf, ci, build, revert, wip]
  example: "feat|PROJ-42|20260428|Add issue-first gate to pull-request flow"
---

# commit

Generate commits following the pipe-delimited standard format. Strict — no Co-Authored-By, no tool attribution, no emojis.

## When to invoke

- After completing a task or feature
- When user asks to "commit", "save", "checkpoint"
- At the end of each subagent-driven-development task

## Format

```
Tipo|IdTarea|YYYYMMDD|Descripción
```

| Component | Description |
|-----------|-------------|
| `Tipo` | Nature of the change (see types below) |
| `IdTarea` | Ticket/board ID (omit between pipes if none) |
| `YYYYMMDD` | Date — always run `date +%Y%m%d` |
| `Descripción` | English, imperative mood, max 60 chars |

## Valid types

| Type | When to use |
|------|-------------|
| `feat` | New functionality |
| `fix` | Bug correction |
| `refactor` | Restructure without behavior change |
| `review` | Code review adjustments |
| `test` | Tests added or adjusted |
| `docs` | Documentation only |
| `chore` | Maintenance, minor tasks |
| `perf` | Performance improvement |
| `ci` | CI/CD pipeline changes |
| `build` | Build system changes |
| `revert` | Revert previous commit |
| `wip` | Work-in-progress (avoid in main branches) |

## Protocol

### 1. Survey

```bash
git status
git diff --staged
git log --oneline -5
date +%Y%m%d
```

### 2. Stage by name

```bash
git add src/auth/auth.service.ts src/auth/auth.controller.ts
```

Never stage: `.env`, credential files, large binaries.

### 3. Commit (HEREDOC)

```bash
git commit -m "$(cat <<'EOF'
feat|PROJ-042|20260428|Add JWT refresh token rotation
EOF
)"
```

### 4. Verify

```bash
git log --oneline -1
git show --stat HEAD
```

## Canonical examples

```
feat|LIQUI|20260428|Implement complete CRUD for cargos module
fix|LIQUI|20260428|Fix regex validation in CreateCargoDto
refactor|20260428|Optimize queries in CargosService
test|LIQUI|20260428|Add unit tests for cargos module
docs|LIQUI|20260428|Update API documentation for cargos endpoints
chore|20260428|Configure linting rules for DTOs
review|LIQUI|20260428|Apply code review suggestions to cargos module
```

## Pre-commit checklist

- [ ] Format: `Tipo|IdTarea|YYYYMMDD|Descripción`
- [ ] Description ≤ 60 chars, English imperative
- [ ] Code tested
- [ ] No linting errors
- [ ] No `.env` / credentials staged
- [ ] One logical change per commit

## Hard rules

- NEVER commit message in plain English without pipe format
- NEVER add Co-Authored-By, Generated-with, or any tool attribution
- NEVER stage `.env` / `secrets/` / credentials
- ALWAYS one logical change per commit
