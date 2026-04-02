---
name: pull-request
version: 1.0
description: "Create well-structured GitHub PRs with summary, test plan, and reviewers."
accepts_args: true
---

# pull-request

> Create well-structured GitHub PRs. Ported from ai-framework (Dario-Arcos).

---

## When to invoke

- After `finishing-a-development-branch` selects "Push + PR"
- When user asks to "create PR", "open pull request", "submit for review"

---

## Step 1 — Survey branch

```bash
git status
git log main..HEAD --oneline     # All commits in this branch
git diff main...HEAD --stat       # Files changed vs main
```

---

## Step 2 — Verify tests pass

```bash
npm test  # or pytest / go test / cargo test
# Must see 0 failures before creating PR
```

---

## Step 3 — Push branch

```bash
git push -u origin $(git branch --show-current)
```

---

## Step 4 — Create PR

El título debe derivarse del tipo y descripción del commit principal de la branch:

```
feat/fix/refactor/... — Descripción imperativa en inglés (max 70 chars)
```

Ejemplos:
```
feat — Add user authentication with JWT refresh rotation
fix — Resolve null pointer in UserService.findById
refactor — Extract payment service to shared module
```

```bash
gh pr create --title "tipo — Descripción imperativa" --body "$(cat <<'EOF'
## Summary

- [Bullet 1: qué se implementó y por qué]
- [Bullet 2: decisión clave tomada]
- [Bullet 3: qué se cambió / eliminó]

## Motivation

[Por qué se necesitaba este cambio — link a issue/ticket si aplica]

## Test Plan

- [ ] [Escenario de prueba 1]
- [ ] [Escenario de prueba 2]
- [ ] [Edge case probado]
- [ ] Tests existentes pasan (`npm test`)

## Breaking Changes

[Ninguno / Describir si los hay]

## Rollback Plan

[Cómo revertir si esto rompe producción — e.g. `git revert <sha>`, feature flag off]
EOF
)"
```

---

## Step 5 — Confirm

```bash
gh pr view  # Show PR URL and status
```

Output the PR URL to user.

---

## Checklist before creating

- [ ] Branch pushed to remote
- [ ] Tests passing
- [ ] Title ≤ 70 chars, conventional format
- [ ] Summary bullets are clear (no "changed some files")
- [ ] Test plan is concrete, not "tested manually"
- [ ] No secrets or credentials in diff
