# sop-code-assist

> Execute a single task from the task list. SDD-compliant implementation with mandatory verification. Ported from ai-framework (Dario-Arcos).

---

## When to invoke

- When assigned a specific task ID from `sop-planning` output
- Within `subagent-driven-development` per-task dispatch
- Mode: `interactive` (default) or `autonomous` (ralph/subagent context)

---

## Pre-task Checklist

- [ ] Read task file: `docs/changes/<feature>/tasks.md`
- [ ] Identify task ID and dependencies
- [ ] Confirm dependencies are complete (status: completed)
- [ ] Read all files mentioned in task

---

## Execution Protocol

### Step 1 — Scenario First

Write or confirm the scenario BEFORE writing production code:

```markdown
## Scenario: [Task name]
Given: [concrete input from task file]
When: [action from task file]
Then: [expected output from task file]
```

Create test file if it doesn't exist. **The test must FAIL** at this point.

### Step 2 — Minimum Implementation

Write the minimum code to satisfy the scenario:
- Follow existing patterns in the codebase
- No gold-plating
- No features beyond the task scope
- Respect existing types, interfaces, patterns

### Step 3 — Verify Convergence

```bash
# Run the specific test
[verification command from task file]
# Must see: PASS
```

If failing: fix code, not the test.

### Step 4 — Anti-reward-hacking check

- [ ] Test was written BEFORE production code (can verify by reading your own turn history)
- [ ] Test uses concrete assertions, not `toBeDefined()`
- [ ] Assertion count same or higher than initial scenario test

### Step 5 — Code quality check

- [ ] No `any` TypeScript types
- [ ] No hardcoded secrets or credentials
- [ ] No N+1 database queries
- [ ] Error handling present for external calls
- [ ] Existing patterns and naming conventions followed

### Step 6 — Commit

Invoke `commit` skill:
```
Skill("commit")
# Message format: feat(scope): description from task
```

### Step 7 — Update task status

```bash
# Update task file
# Status: pending → completed
sed -i 's/\*\*Status\*\*: pending/\*\*Status\*\*: completed/' docs/changes/<feature>/tasks.md
```

### Step 8 — Invoke verification-before-completion

```
Skill("verification-before-completion")
```

Only AFTER this verification: claim task complete.

---

## Autonomous Mode (subagent/ralph context)

When `mode="autonomous"`:
- Skip all interactive questions
- Never ask for confirmation
- Execute Steps 1-8 without pausing
- Emit status update via TaskUpdate when complete
- Emit `<promise>TASK_COMPLETE</promise>` if in ralph loop

---

## Output

```
Task [TASK-ID] completed.
Evidence: [command] → [output]
Files changed: [list]
Tests: [N passing, 0 failing]
```

---

## Integration

```
sop-planning → [sop-code-assist] → sop-reviewer
                           ↑
                    (per task, in loop)
```
