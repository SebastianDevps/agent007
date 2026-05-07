---
name: ralph-loop-wrapper/flow-diagram
description: Full ASCII flow of Ralph loop execution — validation, iteration body, exit conditions
---

# Ralph Loop Execution Flow

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
