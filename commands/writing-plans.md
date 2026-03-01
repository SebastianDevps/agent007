---
name: writing-plans
version: 1.0
description: "Decompose a feature/bug/refactor into executable tasks of 2-5 minutes each. Each task must have exact file paths, TDD steps, and a verification command. Saves plan to docs/plans/YYYY-MM-DD-<feature>.md"
accepts_args: true
---

# /writing-plans — Task Decomposition

**Input**: Feature description or brainstorming output
**Output**: `docs/plans/YYYY-MM-DD-<feature>.md` with 2-5 min tasks

---

## Process

### 1. Explore the codebase

Use Glob + Grep to find:
- Existing files that will be modified
- Patterns to follow (naming, structure)
- Tests that need updating

### 2. Write the plan

Save to `docs/plans/YYYY-MM-DD-<feature>.md`:

```markdown
# Plan: <Feature Name>

**Date**: YYYY-MM-DD
**Complexity**: simple|medium|complex
**Estimated time**: X min

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Edge Cases
1. Edge case 1 → handling strategy
2. Edge case 2 → handling strategy

---

## Tasks

### Task 1 — <name>
**Agent**: platform-expert|backend-db-expert|frontend-ux-expert|security-expert
**Files**: exact/path/to/file.ts
**Time**: 3-5 min

Steps:
1. [exact step with code snippet]
2. [exact step]
3. Run: `<verification command>`

TDD:
- Write failing test first
- Implement until test passes
- Commit

Verification: `<command that proves this task is done>`
```

### 3. Validate the plan

Before handing off:
- Every task has a verification command
- Tasks are ordered: dependencies first
- No task > 5 min (split if needed)
- Total estimated time is realistic

---

## Rules

- ❌ No pseudocode — exact file paths and real code snippets only
- ❌ No task without a verification command
- ✅ Tasks are sequential (each builds on previous)
- ✅ TDD steps for every implementation task

**Next step after completion**: `/subagent-driven-development`
