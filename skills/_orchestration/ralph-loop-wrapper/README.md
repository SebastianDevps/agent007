# Ralph Loop Wrapper

**Transforming Agent007 skills into self-correcting iterative loops**

---

## Quick Start

Ralph Loop Wrapper is infrastructure that automatically wraps skills in iterative self-correction loops. When activated, skills execute repeatedly until they reach machine-verifiable success criteria or safety limits.

### Example

```bash
# User says:
"Implement user registration with email validation"

# Orchestrator detects:
- Task type: feature
- Has test suite: yes
- Risk level: medium
- → Auto-activates Ralph Loop

# What happens:
Iteration 1: TDD writes test + implementation → npm test → 3 failures
Iteration 2: TDD reads failures → fixes → npm test → 1 failure
Iteration 3: TDD reads failure → fixes → npm test → ALL PASS
           → Outputs <promise>COMPLETE</promise>
           → Loop exits ✅

# Result: Working, tested feature in 3 autonomous iterations
```

---

## Installation & Setup

Ralph is already integrated into Agent007. No installation needed!

### Configuration

Ralph configuration is in `.claude/settings.json`:

```json
{
  "ralph": {
    "enabled": true,
    "autoActivation": {
      "enabled": true,
      "rules": {
        "tdd": {
          "taskTypes": ["feature"],
          "riskLevels": ["low", "medium"],
          "maxIterations": 20,
          "maxCostUSD": 5.0
        },
        "debugging": {
          "taskTypes": ["bug"],
          "riskLevels": ["low", "medium"],
          "maxIterations": 15,
          "maxCostUSD": 3.0,
          "escalateToDeepDebug": true
        }
      }
    }
  }
}
```

### Enabling/Disabling

```bash
# Disable Ralph globally
# Edit .claude/settings.json:
{
  "ralph": {
    "enabled": false
  }
}

# Disable for specific task
User: "Implement X --no-ralph"
```

---

## How It Works

### The Loop

```
┌──────────────────────────────────────┐
│ 1. Execute Skill                     │
│    Run TDD, debugging, etc.          │
└─────────────┬────────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│ 2. Run Verification                  │
│    npm test, npm run lint, etc.      │
└─────────────┬────────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│ 3. Check Completion                  │
│    <promise>COMPLETE</promise>?      │
└─────────────┬────────────────────────┘
              │
        YES ──┼── NO
              │
    ┌─────────▼─────────┐
    │ 4. Safety Checks  │
    │ - Cost limit?     │
    │ - Stalled?        │
    │ - Same error 5x?  │
    └─────────┬─────────┘
              │
        PASS ─┼─ FAIL (abort)
              │
              ▼
    ┌──────────────────┐
    │ 5. Enrich Prompt │
    │ + Git diff       │
    │ + Test output    │
    │ + Error messages │
    └─────────┬────────┘
              │
              ▼
       Back to Step 1
```

### Prompt Enrichment

**Iteration 1** (first attempt):
```
[Original user prompt - unchanged]
```

**Iteration 2+** (subsequent attempts):
```
[Original user prompt]

---
[Ralph Loop Context - Iteration N]

You are in a Ralph loop. This is attempt #N.

Review your previous work:
- Modified files: src/auth.service.ts, src/auth.spec.ts
- Test output:
  FAIL src/auth.spec.ts
    ● should validate email format
      Expected "invalid@" to fail validation

File changes (last 3 iterations): 2, 1, 0
⚠️ No progress detected. Try a different approach.

When ALL requirements are met, output <promise>COMPLETE</promise>.
```

---

## Auto-Activation Rules

Ralph automatically activates when ALL conditions are true:

| Condition | Check |
|-----------|-------|
| **Machine-verifiable success** | Has `verificationCommand` (npm test, lint) |
| **Well-scoped task** | Task type in [feature, bug, refactor] |
| **Acceptable risk** | Risk level in [low, medium] (not high/critical) |
| **Ralph-ready skill** | Skill supports completion promises |

### Examples

| User Request | Ralph? | Why |
|--------------|--------|-----|
| "Implement /users endpoint with tests" | ✅ YES | Feature + tests + low risk |
| "Fix N+1 query bug" | ✅ YES | Bug + has test + medium risk |
| "Design database schema" | ❌ NO | Subjective decision, no auto-verification |
| "Add JWT authentication" | ❌ NO | High risk (auth), needs human oversight |
| "Fix all ESLint errors" | ✅ YES | Refactor + lint verification + low risk |

---

## Safety Mechanisms

### 1. Hard Limits

```yaml
maxIterations: REQUIRED (user must set explicitly)
maxCostUSD: REQUIRED (user must set explicitly)
absoluteMaxIterations: 50 (global cap, cannot exceed)
absoluteMaxCostUSD: $10.00 (global cap)
dailyCostBudget: $50.00 (across all Ralph loops today)
```

### 2. Stall Detection

If 5 consecutive iterations produce **zero file changes**, Ralph aborts:

```
❌ Ralph Loop Aborted: STALL_DETECTED

Reason: No file changes in last 5 iterations
Iterations completed: 8/20
Cost spent: $0.67

Suggestion: Try a different approach or review manually.
```

**Escalation**: For bugs, Ralph can escalate to systematic-debugging after stall.

### 3. Same Error Detection

If the exact same error repeats 5 times, Ralph aborts:

```
❌ Ralph Loop Aborted: SAME_ERROR_5X

Repeated error:
  TypeError: Cannot read property 'name' of undefined

Iterations: 5/20
Cost: $0.42

Suggestion: This error suggests a fundamental misunderstanding.
Review the code structure manually.
```

### 4. Prohibited Paths

Ralph aborts if certain sensitive paths are modified:

```yaml
prohibited:
  - src/auth/
  - src/payments/
  - migrations/
  - .env
  - secrets/
```

```
❌ Ralph Loop Aborted: PROHIBITED_PATH_MODIFIED

Files:
  - src/auth/jwt-secret.ts

Ralph is not allowed to modify authentication code.
Please review this change manually.
```

### 5. Cost Warnings

```
💰 Cost at 80% of limit! ($4.00 / $5.00)
⚠️  Next iteration may exceed budget.
```

---

## Ralph-Ready Skills

Current skills that work with Ralph:

| Skill | Completion Promise | Verification | Status |
|-------|-------------------|--------------|--------|
| `workflow/tdd` | `<promise>COMPLETE</promise>` | `npm test` | ✅ Ready |
| `quality-gates/systematic-debugging` | `<promise>BUG_FIXED</promise>` | `npm test` | ✅ Ready |
| `code-cleanup` (future) | `<promise>LINT_CLEAN</promise>` | `npm run lint` | 🚧 Planned |

### Making a Skill Ralph-Ready

Add to your skill's `SKILL.md`:

```markdown
## Ralph Loop Integration

This skill is **Ralph-ready**.

### Completion Signal

When complete, output:
<promise>YOUR_PROMISE</promise>

### Completion Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] All tests pass

### Self-Correction Pattern

In Ralph mode:
1. Read verification output from previous iteration
2. Identify what failed
3. Implement fix
4. If success → output completion promise
5. If failure → try different approach
```

---

## Monitoring & Metrics

### Real-Time Output

```
🔄 RALPH LOOP START
Loop ID: a3f2b1c4-...
Skill: tdd
Max Iterations: 20
Max Cost: $5.00

─────────────────────────────────
📍 Iteration 1/20
─────────────────────────────────

🚀 Executing skill: tdd
💰 Cost this iteration: $0.0521
💰 Total cost: $0.0521 / $5.00
❌ Verification FAILED
📝 Files modified: 2

─────────────────────────────────
📍 Iteration 2/20
─────────────────────────────────

🚀 Executing skill: tdd
💰 Cost this iteration: $0.0498
💰 Total cost: $0.1019 / $5.00
✅ Verification PASSED
✅ Completion promise detected!

════════════════════════════════
✅ RALPH LOOP COMPLETED
════════════════════════════════
Iterations: 2
Cost: $0.1019
Duration: 18s
Verification: PASSED
```

### Metrics File

All loops recorded in `.claude/metrics/ralph-loops.jsonl`:

```jsonl
{"loopId":"a3f2b1c4","skill":"tdd","status":"COMPLETED","iterations":2,"costUSD":0.1019,"durationSeconds":18}
{"loopId":"b7e3c2d1","skill":"systematic-debugging","status":"ABORTED","abortReason":"STALL_DETECTED","iterations":5}
```

### Daily Report

Generated automatically:

```markdown
# Ralph Loop Performance Report - 2026-02-20

## Overall Stats
- Total loops: 15
- Completion rate: 80% ✅ (target: >70%)
- Avg iterations: 4.2 (p95: 12)
- Avg cost: $0.87 (p95: $2.30)
- Stall rate: 7% ✅ (target: <20%)

## By Skill

### TDD
- Loops: 12
- Completion: 83%
- Avg iterations: 3.8
- Avg cost: $0.76

### Systematic Debugging
- Loops: 3
- Completion: 67%
- Avg iterations: 6.3
- Avg cost: $1.42

## Top Abort Reasons
1. MAX_ITERATIONS: 2 (13%)
2. STALL_DETECTED: 1 (7%)

## Alerts
✅ All metrics within target ranges
```

---

## Advanced Usage

### Manual Invocation (Future)

```typescript
import { runRalphLoop } from '.claude/skills/_orchestration/ralph-loop-wrapper/wrapper';

const result = await runRalphLoop({
  skill: 'tdd',
  maxIterations: 15,
  maxCostUSD: 3.0,
  completionPromise: '<promise>COMPLETE</promise>',
  verificationCommand: 'npm test',
  stallDetectionThreshold: 5,
  initialPrompt: 'Implement user registration'
});

if (result.status === 'COMPLETED') {
  console.log(`Success! Iterations: ${result.iterations}`);
} else {
  console.log(`Aborted: ${result.abortReason}`);
}
```

### Custom Completion Promises

```typescript
const result = await runRalphLoop({
  skill: 'migration-runner',
  maxIterations: 10,
  maxCostUSD: 2.0,
  completionPromise: '<promise>MIGRATION_SUCCESS</promise>',
  verificationCommand: 'npm run migrate:verify',
  initialPrompt: 'Migrate users table to add email_verified column'
});
```

### Escalation on Stall

```typescript
const result = await runRalphLoop({
  skill: 'tdd',
  maxIterations: 20,
  maxCostUSD: 5.0,
  completionPromise: '<promise>COMPLETE</promise>',
  verificationCommand: 'npm test',
  stallDetectionThreshold: 5,
  escalateToDeepDebug: true, // Auto-switch to systematic-debugging on stall
  initialPrompt: 'Implement feature X'
});
```

---

## Troubleshooting

### Ralph not activating

**Check**:
1. Is Ralph enabled? `.claude/settings.json` → `ralph.enabled: true`
2. Does task have verification command? (npm test, lint)
3. Is risk level acceptable? (low/medium, not high/critical)
4. Is skill Ralph-ready? Check skill's `SKILL.md`

### Loop keeps stalling

**Causes**:
- Agent is hallucinating progress (outputting text but not changing files)
- Agent is stuck on conceptual misunderstanding
- Task is too complex for iterative approach

**Solutions**:
- Enable `escalateToDeepDebug: true` (auto-escalates to systematic debugging)
- Lower `stallDetectionThreshold` to abort sooner
- Disable Ralph for this specific task (`--no-ralph`)
- Break task into smaller sub-tasks

### Same error repeating

**Causes**:
- Error message is vague (agent can't extract actionable fix)
- Fix requires understanding context agent doesn't have
- Agent is trying same approach repeatedly

**Solutions**:
- Improve error messages in tests (be specific)
- Provide more context in initial prompt
- Review code manually and guide agent

### Cost exceeds budget

**Solutions**:
- Lower `maxCostUSD` per loop
- Lower `maxIterations` (force earlier completion)
- Use cheaper model for iterations (future enhancement)
- Disable Ralph for complex tasks

---

## Best Practices

### 1. Write Clear Tests

Tests are the "oracle" that guides Ralph. Make them specific:

```typescript
// ❌ Vague test
it('should work', () => {
  expect(result).toBeTruthy();
});

// ✅ Specific test
it('should reject emails without @ symbol', () => {
  const result = validateEmail('invalid-email');
  expect(result.isValid).toBe(false);
  expect(result.error).toBe('Email must contain @ symbol');
});
```

### 2. Set Realistic Limits

```typescript
// ❌ Too high (wasted cost if stuck)
maxIterations: 100
maxCostUSD: 50.0

// ✅ Reasonable (forces efficient iteration)
maxIterations: 15
maxCostUSD: 3.0
```

### 3. Use Escalation for Bugs

```typescript
// Debugging benefits from escalation:
{
  skill: 'systematic-debugging',
  escalateToDeepDebug: true  // After stall → inject 4-phase template
}
```

### 4. Monitor Metrics

```bash
# Review daily metrics
cat .claude/metrics/ralph-loops.jsonl | jq -r 'select(.status=="ABORTED")'

# Check cost trends
cat .claude/metrics/ralph-loops.jsonl | jq '.costUSD' | awk '{sum+=$1} END {print sum}'
```

---

## FAQ

**Q: Does Ralph work without tests?**
A: No. Ralph requires machine-verifiable success criteria (tests, lint, build). Without verification, it can't self-correct.

**Q: Can Ralph handle subjective tasks (UX design)?**
A: No. Ralph is optimized for objective, machine-verifiable tasks. Use normal orchestrator flow for design/architecture.

**Q: Does Ralph replace the orchestrator?**
A: No. Ralph is a layer activated BY the orchestrator when conditions are right. Orchestrator still routes and decides.

**Q: Can I use Ralph for production deployments?**
A: Not recommended. Ralph is best for development/testing. Production changes need human oversight.

**Q: How much does Ralph cost?**
A: Depends on iterations. Average: $0.50-$2.00 per task. Set `maxCostUSD` to control.

**Q: Can Ralph work on multiple features in parallel?**
A: Not yet. Parallel Ralph loops are a future enhancement.

---

## References

- Original Ralph technique: https://ghuntley.com/ralph/
- Claude Code plugin: https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
- Session orchestrator: `.claude/skills/_orchestration/session-orchestrator/SKILL.md`
- TDD skill (Ralph-ready): `.claude/skills/workflow/tdd/SKILL.md`
- Systematic debugging (Ralph-ready): `.claude/skills/quality-gates/systematic-debugging/SKILL.md`

---

## Changelog

### v1.0.0 (2026-02-20)
- ✅ Initial implementation
- ✅ Auto-activation via session orchestrator
- ✅ Safety mechanisms (stall, cost, prohibited paths)
- ✅ Metrics tracking
- ✅ Integration with TDD and systematic-debugging skills

### Roadmap

- [ ] Parallel Ralph loops
- [ ] Cost optimization (use cheaper models for iterations)
- [ ] Learning from history (analyze past loops to improve prompts)
- [ ] Web dashboard for real-time monitoring
- [ ] Multi-agent Ralph (different agents per iteration)

---

**Last Updated**: 2026-02-20
**Status**: ✅ Production Ready
**Maintainer**: Agent007 Team
