---
name: commit
version: 2.0
description: "Generate pipe-delimited commits: Tipo|IdTarea|YYYYMMDD|Descripción"
accepts_args: true
---

# commit

> Generate commits following the pipe-delimited standard format.

---

## When to invoke

- After completing a task or feature
- When user asks to "commit", "save", "checkpoint"
- At the end of each subagent-driven-development task

---

## Commit Format

```
Tipo|IdTarea|YYYYMMDD|Descripción breve
```

### Components

| Component | Description |
|-----------|-------------|
| `Tipo` | Nature of the change (see types below) |
| `IdTarea` | Ticket number / task board ID (omit between pipes if none) |
| `YYYYMMDD` | Commit date — always run `date +%Y%m%d` to get it |
| `Descripción` | Action in English, imperative mood, max 60 characters |

### Types (7 valid)

| Type | When to use |
|------|-------------|
| `feat` | New functionality |
| `fix` | Bug correction |
| `refactor` | Code restructuring / improvement |
| `review` | Code review adjustments |
| `test` | Tests implementation or adjustment |
| `docs` | Documentation changes |
| `chore` | Maintenance or minor tasks |

---

## Step 1 — Survey changes

```bash
git status              # Untracked files
git diff --staged       # What's staged
git diff                # Unstaged changes
git log --oneline -5    # Recent commits (match style)
date +%Y%m%d            # Get today's date for the commit
```

---

## Step 2 — Stage relevant files

```bash
# Always prefer specific files over git add -A
git add src/cargos/cargos.service.ts src/cargos/cargos.controller.ts
```

Never stage: `.env`, `secrets/`, credential files, large binaries.

---

## Step 3 — Write commit message

Rules:
- Description in English, imperative mood ("add" not "added")
- Max 60 characters for description
- IdTarea omitted when no ticket — leave empty between pipes

```bash
git commit -m "$(cat <<'EOF'
feat|PROJ|20260320|Implement complete CRUD for cargos module
EOF
)"
```

### Canonical examples

```bash
feat|LIQUI|20251022|Implement complete CRUD for cargos module
fix|LIQUI|20251022|Fix regex validation in CreateCargoDto
refactor|20251022|Optimize queries in CargosService
test|LIQUI|20251022|Add unit tests for cargos module
docs|LIQUI|20251022|Update API documentation for cargos endpoints
chore|LIQUI|20251022|Configure linting rules for DTOs
review|LIQUI|20251022|Apply code review suggestions to cargos module
```

---

## Step 4 — Verify

```bash
git log --oneline -1    # Confirm commit exists
git show --stat HEAD    # Confirm correct files included
```

---

## Pre-Commit Checklist

Before committing, verify:

- [ ] Format follows: `Tipo|IdTarea|YYYYMMDD|Descripción`
- [ ] Description is clear and concise (max 60 characters)
- [ ] Code is tested
- [ ] No linting errors
- [ ] Functionality is documented if applicable
- [ ] Tests updated if applicable

---

## Recommended Workflow (7 steps)

1. **Development** → Implement the functionality
2. **Testing** → Verify it works correctly
3. **Documentation** → Update docs if necessary
4. **Commit** → Use the standard format above
5. **Evidence** → Document in the task board (screenshot, logs, PR link)
6. **PR** → Create pull request with detailed description and review checklist
7. **Review** → Wait for team review
