---
name: pull-request
version: 2.0
description: "Create well-structured GitHub PRs enforcing issue-first discipline"
accepts_args: true
preconditions:
  - linked_issue_exists
  - issue_has_status_approved
  - tests_passing
  - branch_pushed_to_remote
outputs:
  - name: pr_url
    type: url
    format: "https://github.com/{owner}/{repo}/pull/{N}"
  - name: pr_checklist
    type: checklist
    format: "issue_linked | tests_pass | no_secrets | title_under_70_chars"
steps_count: 5
triggers:
  - "create PR"
  - "open pull request"
  - "submit for review"
  - "finishing-a-development-branch → Push + PR"
---

# pull-request

> Create well-structured GitHub PRs. Ported from ai-framework (Dario-Arcos).

---

## When to invoke

- After `finishing-a-development-branch` selects "Push + PR"
- When user asks to "create PR", "open pull request", "submit for review"

---

## Step 0 — Verify linked issue (issue-first gate)

Every PR MUST link an approved issue. Verify before proceeding:

```bash
# Identify the issue number this branch addresses
# If none exists, create one first with /issue-creation
gh issue view <N> --json title,labels -q '{title: .title, labels: [.labels[].name]}'
```

**Gate conditions — STOP if any fail:**
- [ ] Issue exists and is not closed
- [ ] Issue has `status:approved` label (maintainer-only — wait if missing)
- [ ] Issue number is known — you'll add `Closes #<N>` in the PR body

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
## Linked Issue

Closes #<N>

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

- [ ] Linked issue exists and has `status:approved`
- [ ] PR body contains `Closes #<N>`
- [ ] Branch pushed to remote
- [ ] Tests passing
- [ ] Title ≤ 70 chars, conventional format
- [ ] Summary bullets are clear (no "changed some files")
- [ ] Test plan is concrete, not "tested manually"
- [ ] No secrets or credentials in diff
