---
name: ralph-loop-wrapper
description: "Infrastructure skill: wraps task execution in autonomous ralph loop. Not directly invocable — injected by orchestrator."
invokable: false
version: 1.0.0
references:
  - references/flow-diagram.md
  - references/prompt-enrichment.md
  - references/context-compact.md
  - references/metrics-monitoring.md
  - references/result-types.md
  - references/skill-integration.md
---

# Ralph Loop Wrapper

**Type**: Infrastructure (not directly invocable)
**Auto-inject**: Via session orchestrator
**Invokable**: No (used internally by orchestrator)

## Purpose

Transforms any skill into a self-correcting iterative execution loop. Agent attempts → verifies → reads failure → retries → until machine-verifiable success criteria met (or hard limit hits).

**Real implementation** (replaces aspirational spec):
- Stop hook: `context-engine.py` + `state-sync.py` — completion detection + state
- Slash command: `.claude/commands/ralph-loop.md` — activates loop with args
- Runtime state: `.claude/ralph-state.json` (gitignored)
- Completion signal: `.claude/ralph-complete.txt` (Claude writes when done)
- Routing: `ralph →` keyword auto-detection in `.claude/CLAUDE.md`

---

## Hard Rules (non-negotiable)

- `maxIterations` REQUIRED — no default. User MUST set explicitly.
- `maxCostUSD` REQUIRED — no default. Kill switch.
- Global caps override user values: `absoluteMaxIterations: 50`, `absoluteMaxCostUSD: 10.00`, `dailyCostBudget: 50.00`.
- Completion promise format is fixed: `<promise>COMPLETE</promise>` (or skill-specific tag like `<promise>BUG_FIXED</promise>`). The exact tag must match `config.completionPromise`.
- Prohibited paths NEVER modified by Ralph: `src/auth/`, `src/payments/`, `migrations/`, `.env`. If git diff shows any → ABORT(PROHIBITED_PATH).
- Scenarios / verification commands are external — do not modify them mid-loop to make code pass.

---

## Decision Tree — Pending-Work Sentinel (patrón Codex)

Exit condition is NOT "did the test pass?" — it is **"is there pending work?"**

```
pending_work = TRUE  if:
  - <promise>COMPLETE</promise> NOT in output
  - test output contains failures
  - reflected_message generated (prior iteration error)

pending_work = FALSE if:
  - <promise>COMPLETE</promise> detected → SUCCESS (clean exit)
  - maxIterations reached → ABORT(MAX_ITERATIONS)
  - same error 5x → ABORT(SAME_ERROR_5X)
  - cost > maxCostUSD → ABORT(COST_LIMIT)
  - 5 iterations with zero file changes → ABORT(STALL)
  - prohibited path modified → ABORT(PROHIBITED_PATH)
```

Prevents two failures: infinite loop (sentinel detects stall) AND premature exit (only stops when no pending work, not when agent "thinks" it's done).

```
Iter 1: generate → npm test → 3 failures
  → reflected_message = "[output]\nRoot cause: X\nFix: Y"
  → pending_work = TRUE → continue

Iter 2: generate (with reflected_message) → npm test → 0 failures
  → outputs <promise>COMPLETE</promise>
  → pending_work = FALSE → SUCCESS
```

For full execution flow (8-step iteration body) → `references/flow-diagram.md`.

---

## When Ralph Auto-Activates

ALL conditions must be true:

1. **Machine-verifiable success criteria** — `hasVerificationCommand = true` (e.g. `npm test`, `npm run lint`, `npm run build`).
2. **Well-scoped task** — `taskType ∈ {feature, bug, refactor}` AND scope is specific (not "improve architecture").
3. **Risk acceptable** — `riskLevel ∈ {low, medium}`. NEVER high/critical.
4. **Skill is Ralph-ready** — `skill.supportsRalph = true` (currently: `tdd`, `systematic-debugging`, `code-cleanup`).

## Anti-patterns — DO NOT use Ralph for

- Subjective decisions (UX, architecture)
- High-risk tasks (auth, payments, migrations) — those need human oversight
- Tasks without automated verification
- Production debugging (needs human judgment)

---

## Stall & Same-Error Detection

```typescript
// Stall = 5 consecutive iterations with zero file changes
isStalled = fileChangesHistory.slice(-5).every(count => count === 0);

if (stalled && config.escalateToDeepDebug) {
  return escalateToDeepDebug();  // inject systematic-debugging template
} else {
  return abort('STALL_DETECTED');
}

// Same error 5x → abort
if (errorRepeatCount >= 5) abort('SAME_ERROR_5X', { error: lastError });
```

---

## Proactive Context Compaction

Before each iteration, check `.sdlc/state/context-budget.json`. If `percent ≥ 60%` → run `/compact` BEFORE continuing the iteration. Persist state to `.sdlc/state/session.md` so it survives compaction. Full schema → `references/context-compact.md`.

---

## Need → Reference

| You need to… | Read |
|---|---|
| Full 8-step iteration flow + exit conditions diagram | `references/flow-diagram.md` |
| Prompt template for iter 1 vs iter 2+ (with git diff, test output) | `references/prompt-enrichment.md` |
| Pre-iteration compact checkpoint + session.md schema | `references/context-compact.md` |
| `RalphMetrics` interface, JSONL storage, daily report format, alert thresholds | `references/metrics-monitoring.md` |
| `RalphConfig` and `RalphResult` (Success/Abort/Error) TypeScript shapes | `references/result-types.md` |
| Make a skill Ralph-ready, ralph-ready table, example wrapper invocation, error handling, testing, future enhancements | `references/skill-integration.md` |

---

**Last Updated**: 2026-02-20
