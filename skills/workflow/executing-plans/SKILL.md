---
name: executing-plans
description: "Execute task plans systematically with verification at each step. Use when user has a detailed task plan ready for implementation."
version: 1.0.0
invokable: true
accepts_args: true
allowed-tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
when:
  - previous_skill: writing-plans
    status: completed
  - user_mentions: ["execute plan", "implement tasks", "run the plan"]
---

# Executing Plans - Systematic Task Execution

**Purpose**: Execute tasks from a detailed plan systematically, verifying each step before proceeding to the next.

**When to use**:
- After `writing-plans` generates a task breakdown
- When user has a detailed plan with file paths and verification commands
- For systematic implementation of complex features

---

## Execution Process

### Phase 1: Plan Review

Before starting execution:

1. **Read the plan** completely
2. **Verify prerequisites**:
   - Required dependencies installed
   - Database/services running if needed
   - Branch is clean or changes are stashed
3. **Estimate total time**: Sum of all task estimates
4. **Confirm with user**: Show plan summary and get approval

```markdown
## Plan Summary
- Total tasks: [N]
- Estimated time: [X] minutes
- Files to modify: [list]
- New files: [list]

Ready to proceed? [Y/n]
```

---

### Phase 2: Task-by-Task Execution

For each task in the plan:

```
Task [N]/[Total]: [Task Name] (Est: [X] min)

1. READ: Check current state
   → Read affected files
   → Verify assumptions in plan are still valid

2. IMPLEMENT: Execute the task
   → Create/modify files as specified
   → Follow exact code in plan (or adapt if context changed)

3. VERIFY: Run verification command
   → Execute verification command from plan
   → Ensure it passes before continuing

4. STATUS: Report progress
   ✅ Task [N] completed in [actual time]
   → [Brief summary of what was done]
```

**Critical Rule**: If verification fails, STOP. Do not proceed to next task.

---

### Phase 3: Verification Failure Handling

When a verification command fails:

```markdown
❌ Verification failed for Task [N]

**Error**: [error output]

**Options**:
A) Fix the issue and retry verification
B) Skip this task (mark as pending, continue with next)
C) Abort execution (stop entire plan)

Which option? [A/B/C]
```

**Default**: Option A (fix and retry)

---

### Phase 4: Post-Execution Summary

After completing all tasks (or aborting):

```markdown
## Execution Summary

**Completed**: [N]/[Total] tasks
**Time**: [actual] min (estimated: [X] min)
**Status**: ✅ All verified | ⚠️ Some pending | ❌ Aborted

### Tasks Completed
- Task 1: [name] ✅
- Task 2: [name] ✅
- ...

### Tasks Pending (if any)
- Task 5: [name] ⚠️ (Reason: [why skipped])

### Next Steps
[What should happen next - tests to run, deployment, etc.]
```

---

## Integration with Workflow

### writing-plans → executing-plans

```
writing-plans
  → Generates detailed task breakdown
  → Output: Task list with file paths, code, verification commands
  
executing-plans (this skill)
  → Takes the task list
  → Executes each task systematically
  → Verifies at each step
  → Output: Implemented feature with all tasks verified
```

---

## Quality Gates

### Before Starting
- [ ] Plan has complete file paths (no relative or ambiguous paths)
- [ ] Plan has verification commands for each task
- [ ] Plan tasks are 2-5 minutes each
- [ ] Prerequisites are met (dependencies, environment)

### During Execution
- [ ] Each task passes its verification before next task starts
- [ ] Actual state matches plan assumptions (or plan is adapted)
- [ ] Changes are incremental (commit or checkpoint per task if long)

### After Execution
- [ ] All verification commands pass
- [ ] Integration test passes (if applicable)
- [ ] No uncommitted changes (or ready to commit)

---

## Example: Executing JWT Auth Plan

```markdown
Plan: Implement JWT Authentication (15 tasks, 45 min)

Execution:

Task 1/15: Create User entity (3 min)
  → Read: Check if src/users/entities/ exists ✅
  → Write: src/users/entities/user.entity.ts
  → Verify: npm run build
  ✅ Passed (2.5 min actual)

Task 2/15: Create CreateUserDto (2 min)
  → Read: Check User entity structure ✅
  → Write: src/users/dto/create-user.dto.ts
  → Verify: npm test -- create-user.dto.spec.ts
  ❌ Failed: "class-validator not found"
  
  Fixing: npm install class-validator class-transformer
  Retry verify: npm test -- create-user.dto.spec.ts
  ✅ Passed (4 min actual - included fix)

Task 3/15: Implement UsersService.create()
  → Read: src/users/users.service.ts ✅
  → Edit: Add create() method
  → Verify: npm test -- users.service.spec.ts
  ✅ Passed (3 min actual)

[Continue for remaining 12 tasks...]

---

Summary:
✅ 15/15 tasks completed
⏱️  48 min actual (45 min estimated)
🎯 All verification passed
```

---

## Transition to Next Skill

After successful execution:

```markdown
**Execution complete!** ✅

Next recommended actions:
1. Run full test suite: `npm test`
2. Manual testing if applicable
3. Create commit: `git add . && git commit -m "..."`
4. Consider code review if significant changes

[P]attern [L]esson [D]ecision [N]o
```

---

## Anti-Patterns

### ❌ Skipping Verification
```diff
- Task 1: Write code
- Task 2: Write more code
- Task 3: Test everything at the end
```
**Problem**: Errors compound, hard to debug.

### ✅ Verify Each Step
```diff
+ Task 1: Write code → Verify
+ Task 2: Write code → Verify  
+ Task 3: Write code → Verify
```
**Benefit**: Catch errors immediately, easy to pinpoint.

---

### ❌ Continuing After Failure
```diff
- Task 5 verification failed → Skip to Task 6
```
**Problem**: Downstream tasks may depend on Task 5.

### ✅ Stop and Fix
```diff
+ Task 5 verification failed → Fix before continuing
```
**Benefit**: Ensures solid foundation.

---

## Configuration

### Execution Modes

**Normal** (default): Stop on any verification failure  
**Lenient**: Mark failed tasks as pending, continue with independent tasks  
**Strict**: Abort on first failure (no retry)

Set mode via argument:
```
/executing-plans --mode=lenient
```

---

**Required previous skill**: writing-plans (task decomposition)  
**Optional next skill**: code-review (for significant changes)
