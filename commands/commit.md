---
name: commit
version: 1.0
description: "Generate conventional commits with semantic versioning signals. Enforces commit message standards."
accepts_args: true
---

# commit

> Generate conventional commits with semantic versioning signals. Ported from ai-framework (Dario-Arcos).

---

## When to invoke

- After completing a task or feature
- When user asks to "commit", "save", "checkpoint"
- At the end of each subagent-driven-development task

---

## Conventional Commit Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

### Types

| Type | When to use | Semver signal |
|------|-------------|---------------|
| `feat` | New feature | MINOR |
| `fix` | Bug fix | PATCH |
| `refactor` | Code change without behavior change | PATCH |
| `test` | Adding or updating tests | PATCH |
| `docs` | Documentation only | PATCH |
| `chore` | Build, CI, tooling | PATCH |
| `perf` | Performance improvement | PATCH |
| `ci` | CI/CD changes | PATCH |
| `style` | Formatting, not logic | PATCH |
| `revert` | Reverts a commit | PATCH |
| `BREAKING CHANGE` | Breaking API change (in footer) | MAJOR |

### Scope examples
- `auth`, `users`, `api`, `db`, `hooks`, `skills`, `ui`
- Omit scope when change is broad/cross-cutting

---

## Step 1 — Survey changes

```bash
git status          # Untracked files
git diff --staged   # What's staged
git diff            # Unstaged changes
git log --oneline -5  # Recent commits (match style)
```

---

## Step 2 — Stage relevant files

```bash
# Prefer specific files over git add -A
git add src/auth/auth.service.ts src/auth/auth.module.ts
```

Never stage: `.env`, `secrets/`, credential files, large binaries.

---

## Step 3 — Write commit message

Rules:
- Description: ≤72 characters, imperative mood ("add" not "added" or "adding")
- Body: explain WHY, not what (the diff shows what)
- Breaking changes: add `BREAKING CHANGE:` footer

```bash
git commit -m "$(cat <<'EOF'
feat(auth): add JWT refresh token rotation

Tokens invalidated on each rotation to prevent theft.
Expiry reduced from 7d to 15min with refresh flow.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Step 4 — Verify

```bash
git log --oneline -1  # Confirm commit exists
git show --stat HEAD   # Confirm correct files
```

---

## Anti-patterns

| Bad | Good |
|-----|------|
| "Update files" | "fix(auth): resolve token expiry race condition" |
| "WIP" | Create a proper commit with description |
| `git add .` blindly | Stage specific files |
| Skip Co-Authored-By | Always include attribution |
| Commit secrets | Verify with `git diff --staged` before committing |
