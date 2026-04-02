---
name: dev
version: 2.0
description: "Master development command. Classifies the task, selects the optimal workflow path, and executes autonomously using all ecosystem elements (brainstorming, worktrees, plans, subagents, ralph, TDD, review)."
accepts_args: true
---

# /dev — Master Autonomous Development Command

**Invocation**: `/dev "<task description>"` · `/dev "<task>" --simple` · `/dev "<task>" --ralph` · `/dev "<task>" --max-iterations N`

---

## Step 1 — Classify Task

Analyze `$ARGUMENTS` and current project context to determine:

### Complexity Assessment

| Complexity | Signals | Workflow |
|-----------|---------|----------|
| **Simple** | Single file change, bug fix, < 30 min, no design decisions | Direct implementation |
| **Medium** | Multiple files, new feature, 30 min–2 hrs, clear requirements | Plan → Subagent execution |
| **Complex** | Architecture change, unclear requirements, > 2 hrs, multiple domains | Brainstorm → Worktree → Plan → Subagent execution |

### Ralph Mode Detection (auto-activates if ANY):
- Explicit `--ralph` flag
- Explicit `--persist` flag
- Task mentions "loop until", "until tests pass", "autonomous", "run overnight"
- Task is TDD-oriented with a clear verification command

### Risk Level
- **Low**: UI changes, documentation, new isolated features
- **Medium**: New API endpoints, DB queries, state changes
- **High/Critical**: Auth, payments, migrations, breaking changes → require explicit confirmation before proceeding

---

## Step 2 — Show Routing Decision

Always display before proceeding:

```
🎯 dev → [WORKFLOW PATH]
Complexity: [simple|medium|complex] | Risk: [low|medium|high|critical]
Ralph: [active --max-iterations N | inactive]
Stack: [detected technologies]
```

For High/Critical risk → ask confirmation:
```
⚠️ High-risk task detected: [auth/payment/migration/etc]
Proceeding will affect [describe impact].
Continue? [yes/no]
```

---

## Step 3 — Execute Workflow

### Path A — Simple (direct implementation)

```
1. Read relevant files (Glob + Grep before editing)
2. Implement with enforcement active (no "should work", etc.)
3. Run verification: npm test / npm run build / npm run lint
4. Show actual output — no claims without evidence
5. Done ✅
```

### Path B — Medium (plan → subagent execution)

```
1. Skill('plan')
   → Save to: docs/changes/<feature>/spec.md
   → Tasks: 2-5 min chunks, exact file paths, TDD steps

2. Skill('subagent-driven-development')
   → Per task: implementer subagent → spec review → quality review → commit
   → Ralph wraps each task if --ralph active

3. Skill('finishing-a-development-branch')
   → Tests pass → present 4 options [merge/PR/keep/discard]
```

### Path C — Complex (full autonomous pipeline)

```
1. Skill('brainstorming')
   → One question at a time (Socratic)
   → Output: design doc with decisions + acceptance criteria

2. Skill('using-git-worktrees')
   → Create feat/<branch-name> in .worktrees/
   → Baseline validation (tests must pass before starting)

3. Skill('plan')
   → Save to: docs/changes/<feature>/spec.md
   → Full TDD task breakdown with exact paths

4. Skill('subagent-driven-development')
   → Expert subagent per task (auto-routed by domain)
   → Ralph loop active per task (if --ralph or auto)
   → Two-stage review after each task
   → Commit after each approved task

5. Final code review (full diff review)

6. Skill('finishing-a-development-branch')
   → Verify tests → [merge/PR/keep/discard]
```

---

## Step 4 — Progress Tracking

Use TaskCreate/TaskUpdate throughout:
- One task per implementation step
- Update to `in_progress` before starting, `completed` after review passes

Show progress banner periodically:
```
📊 Progress: [X/N tasks] | Reviews: [X passed] | Time: [Xmin]
```

---

## Step 5 — Update STATE.md

After completion (silently):
- Branch: current branch
- Tarea Activa: ninguna (or next pending)
- Tareas Completadas: prepend with timestamp
- Decisiones Tomadas: any significant design decisions made

---

## Flags Reference

| Flag | Effect |
|------|--------|
| `--simple` | Skip brainstorm + worktree, implement directly |
| `--full` | Force Path C regardless of complexity |
| `--ralph` | Wrap execution in ralph loop |
| `--max-iterations N` | Ralph max iterations (default: 20, max: 50) |
| `--verify "cmd"` | Verification command for ralph (e.g., "npm test") |
| `--no-review` | Skip code review stages (use only for prototypes) |

---

## Examples

**Simple bug fix:**
```
/dev "Fix the null pointer error in UserService.findById()"
```

**New feature (medium):**
```
/dev "Add pagination to the /users endpoint using cursor-based pagination"
```

**Complex feature with ralph:**
```
/dev "Build the kanban board with NextJS/Tailwind and localStorage" --ralph --max-iterations 30 --verify "npm test"
```

**Autonomous overnight run:**
```
/dev "Implement the complete auth module (JWT + refresh tokens + RBAC)" --full --ralph --max-iterations 50
```

---

## Ecosystem Integration Map

```
/dev
 ├── Skill('brainstorming')                    (complex tasks, unclear requirements)
 ├── Skill('using-git-worktrees')             (medium + complex: isolated branch)
 ├── Skill('plan')                            (medium + complex: task breakdown)
 ├── Skill('subagent-driven-development')     (execution engine)
 │    ├── backend-db-expert                   (API, DB, NestJS tasks)
 │    ├── frontend-ux-expert                  (React, Next.js tasks)
 │    ├── platform-expert                     (CI/CD, tests, infra tasks)
 │    ├── security-expert                     (auth, permissions tasks)
 │    ├── Skill('generate')                   (TDD cycle via RED→GREEN→REFACTOR)
 │    ├── /ralph-loop                         (autonomous iteration per task)
 │    └── Skill('verify')                     (after each task)
 └── Skill('finishing-a-development-branch')  (merge/PR/cleanup)
```
