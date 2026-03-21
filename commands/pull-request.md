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

```bash
gh pr create --title "Tipo|IdTarea|YYYYMMDD|Brief description" --body "$(cat <<'EOF'
## Summary

- [Bullet 1: what was implemented]
- [Bullet 2: key decision made]
- [Bullet 3: what was changed / removed]

## Motivation

[Why this change was needed — link to issue if applicable]

## Test Plan

- [ ] [Test scenario 1]
- [ ] [Test scenario 2]
- [ ] [Edge case tested]
- [ ] Existing tests pass (`npm test`)

## Breaking Changes

[None / Describe if any]

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## PR Title Format

Follow the project pipe-delimited standard (same as commit format):

```
Tipo|IdTarea|YYYYMMDD|Brief description
```

Examples:
- `feat|LIQUI|20260321|Add user authentication`
- `fix|LIQUI|20260321|Resolve token expiry race condition`
- `refactor|20260321|Extract payment service`

Max 70 characters total. IdTarea omitted when no ticket — leave empty between pipes.

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
