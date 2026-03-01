---
name: using-git-worktrees
version: 1.0
description: "Creates an isolated git worktree for feature development at .worktrees/<branch-name>. Adds .worktrees/ to .gitignore if missing. Runs baseline validation only if a test suite exists."
accepts_args: true
---

# /using-git-worktrees — Isolated Workspace Setup

**When**: Automatically before `/writing-plans` for medium/complex features.

---

## Process

### 1. Verify .worktrees/ is in .gitignore

```bash
grep -q '\.worktrees/' .gitignore || echo '.worktrees/' >> .gitignore
```

### 2. Create worktree

```bash
# Branch name: feat/<kebab-case-of-task>
git worktree add .worktrees/<branch-name> -b feat/<branch-name>
```

### 3. Detect and run baseline validation

**ONLY run tests if a test suite exists:**

```bash
# Detect test suite
if [ -f package.json ] && grep -q '"test"' package.json; then
  npm test  # Node.js project with test script
elif [ -f Makefile ] && grep -q '^test:' Makefile; then
  make test
elif [ -f pytest.ini ] || [ -f setup.py ]; then
  pytest
else
  echo "⚠️  No test suite detected — skipping baseline validation"
fi
```

If tests exist but **fail** → stop and report. Never proceed with broken baseline.
If no tests exist → continue with a warning, no user permission needed.

### 4. Confirm ready

```
✅ Worktree listo
Branch: feat/<branch-name>
Directory: .worktrees/<branch-name>
Baseline: [X tests passing | no test suite]
→ Ready for /writing-plans
```

---

## Rules

- ❌ Never work directly on `main`/`master`
- ❌ Never proceed if existing tests fail
- ✅ Missing test suite → warn and continue (not a blocker)
- ✅ Cleanup handled by `/finishing-a-development-branch` (options 1 and 4)

**Next step**: `/writing-plans`
