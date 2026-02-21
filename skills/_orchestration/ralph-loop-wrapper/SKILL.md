# Ralph Loop Wrapper

**Type**: Infrastructure (not directly invocable)
**Auto-inject**: Via session orchestrator
**Priority**: High
**Invokable**: No (used internally by orchestrator)

## Purpose

Ralph Loop Wrapper is the infrastructure layer that transforms any skill into a self-correcting, iterative execution loop. Inspired by the Ralph Wiggum technique, it enables agents to autonomously improve their work through repeated attempts until machine-verifiable success criteria are met.

**Version**: 1.0.0
**Status**: ✅ Operational

---

## What is Ralph?

Ralph is a development methodology based on **continuous AI agent loops**:

```
Traditional: Human → Agent → Output (done, even if failing)
Ralph:       Human → Agent → Verify → Agent sees failure → Agent tries again → ... → Success
```

**Key Insight**: The agent becomes the loop. The agent has:
- **Persistent memory** (files, git history)
- **Automatic feedback** (test output, build errors)
- **Objective success criteria** (no human judgment needed)

---

## How It Works

```typescript
// User invokes (through orchestrator):
/tdd "Implement user registration" --persist

// Under the hood:
RalphLoopWrapper.run({
  skill: 'tdd',
  maxIterations: 20,
  maxCostUSD: 5.00,
  completionPromise: '<promise>COMPLETE</promise>',
  verificationCommand: 'npm test'
})

// Loop:
Iteration 1: TDD skill → writes test + code → npm test → 3 failures
Iteration 2: TDD skill → reads failures → fixes → npm test → 1 failure
Iteration 3: TDD skill → reads failure → fixes → npm test → ✅ ALL PASS
           → Outputs: <promise>COMPLETE</promise>
           → Loop exits successfully
```

---

## When Ralph Auto-Activates

The session orchestrator automatically wraps skills in Ralph when ALL conditions are true:

### Condition 1: Machine-Verifiable Success Criteria
```javascript
hasVerificationCommand = true
// Examples: 'npm test', 'npm run lint', 'npm run build'
```

### Condition 2: Well-Scoped Task
```javascript
taskType in ['feature', 'bug', 'refactor']
AND scope is specific (not "improve architecture")
```

### Condition 3: Risk Level is Acceptable
```javascript
riskLevel in ['low', 'medium']
// NOT 'high' or 'critical' (those need human oversight)
```

### Condition 4: Skill is Ralph-Ready
```javascript
skill.supportsRalph = true
// Skills: tdd, systematic-debugging, code-cleanup
```

**When NOT to use Ralph**:
- ❌ Subjective decisions (UX design, architecture)
- ❌ High-risk tasks (auth, payments, migrations)
- ❌ Tasks without automated verification
- ❌ Production debugging (needs human judgment)

---

## Configuration Structure

```typescript
interface RalphConfig {
  // Which skill to wrap
  skill: string;  // 'tdd', 'systematic-debugging', etc.

  // Safety limits (REQUIRED)
  maxIterations: number;     // No default - must be explicit
  maxCostUSD: number;        // Kill switch

  // Success detection
  completionPromise: string;      // e.g., '<promise>COMPLETE</promise>'
  verificationCommand?: string;   // e.g., 'npm test'

  // Stall detection
  stallDetectionThreshold: number;  // Default: 5 iterations
  escalateToDeepDebug?: boolean;    // Default: false

  // Context enrichment
  initialPrompt: string;      // Original user request
  contextInjection?: boolean; // Add git diff, test output to prompt
}
```

---

## Safety Mechanisms

### 1. Hard Limits (Non-Negotiable)

```yaml
maxIterations: REQUIRED (no default, user must set)
maxCostUSD: REQUIRED (no default, user must set)
absoluteMaxIterations: 50 (global cap, even if user sets higher)
absoluteMaxCostUSD: 10.00 (global cap)
dailyCostBudget: 50.00 (total across all Ralph loops)
```

### 2. Stall Detection

```typescript
// Stall = 5 consecutive iterations with zero progress
isStalled(): boolean {
  const recent = fileChangesHistory.slice(-5);
  return recent.length >= 5 && recent.every(count => count === 0);
}

// On stall:
if (stalled && config.escalateToDeepDebug) {
  // Inject systematic-debugging template
  return escalateToDeepDebug();
} else {
  return abort('STALL_DETECTED');
}
```

### 3. Same Error Detection

```typescript
// If same error repeats 5 times, abort
if (errorRepeatCount >= 5) {
  return abort('SAME_ERROR_5X', { error: lastError });
}
```

### 4. Prohibited Paths

```typescript
// Never allow Ralph to modify these:
prohibitedPaths = [
  'src/auth/',
  'src/payments/',
  'migrations/',
  '.env'
]

// Before each iteration, check git diff:
const modifiedFiles = await getModifiedFiles();
if (modifiedFiles.some(f => isProhibited(f))) {
  return abort('PROHIBITED_PATH_MODIFIED', { files: modifiedFiles });
}
```

---

## Loop Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ START: RalphLoopWrapper.run(config, prompt)                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Validate Config     │
          │  - maxIterations?    │
          │  - maxCostUSD?       │
          │  - skill exists?     │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │  Initialize State    │
          │  - iteration = 0     │
          │  - costAccum = 0     │
          │  - history = []      │
          └──────────┬───────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│                    LOOP START                               │
│  while (iteration < maxIterations)                         │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ 1. Execute Skill     │
          │    with enriched     │
          │    prompt            │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ 2. Accumulate Cost   │
          │    Check budget      │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ 3. Detect Completion │
          │    <promise>?        │
          └──────────┬───────────┘
                     │
              YES ───┼─── NO
                     │
          ┌──────────▼───────────┐
          │ 4. Run Verification  │
          │    (if command set)  │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ 5. Check Stall       │
          │    (file changes)    │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ 6. Check Same Error  │
          │    (repeat pattern)  │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ 7. Record Iteration  │
          │    history.push()    │
          └──────────┬───────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ 8. iteration++       │
          │    Sleep 500ms       │
          └──────────┬───────────┘
                     │
                     ▼
          Back to LOOP START
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│                    EXIT CONDITIONS                          │
│  - Completion promise detected → SUCCESS                   │
│  - Max iterations reached → ABORT(MAX_ITERATIONS)          │
│  - Cost limit exceeded → ABORT(COST_LIMIT)                 │
│  - Stall detected → ABORT(STALL)                           │
│  - Same error 5x → ABORT(SAME_ERROR_5X)                    │
│  - Prohibited path → ABORT(PROHIBITED_PATH)                │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
          ┌──────────────────────┐
          │ Record Metrics       │
          │ Return Result        │
          └──────────────────────┘
```

---

## Prompt Enrichment

Ralph enriches prompts with context from previous iterations:

### Iteration 1 (First Attempt)
```
[Original user prompt - unchanged]
```

### Iteration 2+ (Subsequent Attempts)
```
[Original user prompt]

---
[Ralph Loop Context - Iteration N]

You are in a Ralph loop. This is attempt #N.

Review your previous work:
- Modified files: `git diff HEAD~1 --name-only`
- Test output:
  ```
  [Last npm test output]
  ```
- Git history: `git log --oneline -5`

Analysis:
- Files changed in iteration N-1: [count]
- Tests status: [X passing, Y failing]
- Last error: [error message if any]

If tests are failing, read the error messages carefully and fix the root cause.
If you're stuck on the same error, try a different approach.

When ALL requirements are met, output <promise>COMPLETE</promise>.
```

---

## Result Types

```typescript
type RalphResult =
  | RalphSuccess
  | RalphAbort
  | RalphError;

interface RalphSuccess {
  status: 'COMPLETED';
  iterations: number;
  costUSD: number;
  durationSeconds: number;
  output: string;
  verificationPassed: boolean;
}

interface RalphAbort {
  status: 'ABORTED';
  reason: 'MAX_ITERATIONS' | 'COST_LIMIT' | 'STALL' | 'SAME_ERROR_5X' | 'PROHIBITED_PATH';
  iterations: number;
  costUSD: number;
  lastOutput: string;
  details: any;
}

interface RalphError {
  status: 'ERROR';
  error: string;
  iterations: number;
}
```

---

## Metrics Collection

Ralph tracks every loop execution:

```typescript
interface RalphMetrics {
  loopId: string;              // UUID
  skill: string;               // 'tdd', 'systematic-debugging'
  taskType: string;            // 'feature', 'bug'

  startTime: Date;
  endTime: Date;

  status: 'COMPLETED' | 'ABORTED' | 'ERROR';
  abortReason?: string;

  iterations: number;
  costUSD: number;
  durationSeconds: number;

  filesModified: number;
  testsFixed: number;          // initial failing - final failing

  completionPromiseDetected: boolean;
  verificationPassed: boolean;
}
```

**Stored in**: `.claude/metrics/ralph-loops.jsonl` (one JSON per line)

**Daily report**: Automatically generated showing:
- Completion rate
- Average iterations to complete
- Average cost per completion
- Stall rate
- Abort reasons breakdown

---

## Integration with Skills

For a skill to be Ralph-ready, it must:

### 1. Support Completion Promise

```markdown
## Ralph Integration

When executed in Ralph mode, this skill outputs:

<promise>COMPLETE</promise>

when ALL acceptance criteria are met.
```

### 2. Define Success Criteria

```markdown
## Completion Criteria

- [ ] All tests pass (npm test exit code 0)
- [ ] Coverage >= 80%
- [ ] No TypeScript errors
- [ ] No `any` types in new code
```

### 3. Self-Correction Pattern

```markdown
## Self-Correction

In Ralph mode, this skill:
1. Reads test output from previous iteration
2. Identifies what's failing
3. Implements minimal fix
4. Runs verification
5. If success → outputs completion promise
6. If failure → analyzes and tries different approach
```

---

## Ralph-Ready Skills

Current skills that support Ralph:

| Skill | Completion Promise | Verification | Status |
|-------|-------------------|--------------|--------|
| `workflow/tdd` | `<promise>COMPLETE</promise>` | `npm test` | ✅ Ready |
| `quality-gates/systematic-debugging` | `<promise>BUG_FIXED</promise>` | `npm test` | ✅ Ready |
| `code-cleanup` | `<promise>LINT_CLEAN</promise>` | `npm run lint` | 🚧 TODO |

---

## Example Usage (Internal)

```typescript
// In session orchestrator:

const context = detectContext(userInput);

if (shouldActivateRalph(context)) {
  const wrapper = new RalphLoopWrapper();

  const result = await wrapper.run({
    skill: 'tdd',
    maxIterations: 20,
    maxCostUSD: 5.00,
    completionPromise: '<promise>COMPLETE</promise>',
    verificationCommand: 'npm test',
    stallDetectionThreshold: 5,
    initialPrompt: userInput
  });

  handleRalphResult(result);
}
```

---

## Monitoring & Alerts

### Real-Time Alerts

```typescript
// Alert if:
if (costAccumulator > maxCostUSD * 0.8) {
  console.warn(`[Ralph] Cost at 80% of limit: $${costAccumulator.toFixed(2)} / $${maxCostUSD}`);
}

if (iteration > maxIterations * 0.9) {
  console.warn(`[Ralph] Iteration at 90% of limit: ${iteration} / ${maxIterations}`);
}
```

### Daily Report

Generated in `.claude/metrics/ralph-report-[date].md`:

```markdown
# Ralph Loop Performance Report - 2026-02-20

## Overall Stats
- Total loops: 15
- Completion rate: 73% ✅ (target: >70%)
- Avg iterations: 8.4 (p95: 18)
- Avg cost: $1.23 (p95: $3.50)
- Stall rate: 13% ✅ (target: <20%)

## By Skill
### TDD
- Loops: 12
- Completion: 75%
- Avg iterations: 9.2

### Systematic Debugging
- Loops: 3
- Completion: 67%
- Avg iterations: 11.0

## Alerts
⚠️ None today
```

---

## Error Handling

```typescript
// Graceful degradation:
try {
  return await wrapper.run(config);
} catch (error) {
  console.error('[Ralph] Wrapper failed:', error);

  // Fallback to normal (non-loop) execution
  console.log('[Ralph] Falling back to normal execution...');
  return await executeSkillNormally(config.skill, config.initialPrompt);
}
```

**Philosophy**: Ralph should never break the system. If it fails, gracefully fall back to traditional single-pass execution.

---

## Testing Ralph

```bash
# Unit tests
npm test -- ralph-loop-wrapper.spec.ts

# Integration tests with fixtures
npm test -- test-fixtures/ralph/

# Test with real TDD skill
cd test-fixtures/ralph/fixable-bug
npm test  # Should fail
# Run Ralph loop manually
# npm test  # Should now pass
```

---

## Implementation Details

See: `.claude/skills/_orchestration/ralph-loop-wrapper/wrapper.ts`

**Dependencies**: None (pure TypeScript, runs in Claude Code context)

**File Size**: ~500 lines

**Performance**: Negligible overhead (<100ms per iteration)

---

## Future Enhancements

- [ ] Parallel loops (multiple features simultaneously)
- [ ] Cost optimization (use cheaper models for iterations)
- [ ] Learning from history (analyze past loops to improve prompts)
- [ ] Multi-agent Ralph (different agents per iteration)
- [ ] Real-time dashboard (web UI showing loop progress)

---

## References

- Original Ralph technique: https://ghuntley.com/ralph/
- Claude Code plugin: https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
- Session orchestrator integration: `.claude/skills/_orchestration/session-orchestrator/SKILL.md`

---

**Last Updated**: 2026-02-20
**Maintainer**: Agent007 Team
