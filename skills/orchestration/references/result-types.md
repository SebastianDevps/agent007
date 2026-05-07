---
name: ralph-loop-wrapper/result-types
description: TypeScript interfaces for RalphConfig and RalphResult (Success/Abort/Error)
---

# Configuration Structure

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

# Result Types

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
