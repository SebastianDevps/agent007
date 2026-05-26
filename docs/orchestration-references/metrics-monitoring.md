---
name: ralph-loop-wrapper/metrics-monitoring
description: Ralph metrics collection, JSONL storage, daily reports, real-time alerts
---

# Metrics Collection

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
