---
name: performance-profiling/backend-profiling
description: "Node.js / API backend profiling protocol — flame graphs, event-loop lag, heap snapshots, p95/p99 latency."
---

# Backend Profiling — Node.js / API

## Tooling

| Tool | What it shows | When to use |
|---|---|---|
| `clinic doctor` | Event-loop lag, GC pressure, async I/O | First diagnostic — points to which deep tool |
| `clinic flame` | CPU flame graph | Synchronous CPU bottleneck |
| `clinic bubbleprof` | Async ops timeline | Async bottleneck — promises piled up |
| `clinic heapprofiler` | Heap allocation per stack | Memory leaks, allocation hot paths |
| `node --inspect` + Chrome DevTools | Live debugging, manual heap snapshots | Reproduce-on-demand bugs |
| `autocannon` | Synthetic load (req/s, p50/p95/p99) | Establish baseline before optimization |
| `0x` | Single-binary flame graph | When clinic isn't installed |

## Standard protocol — measure, isolate, hand off

### 1. Establish baseline

```bash
# Synthetic load against the endpoint under suspicion
npx autocannon -c 50 -d 30 http://localhost:3000/api/users

# Capture: req/s, p50, p95, p99, errors. Record numbers.
```

```
BASELINE
  Endpoint:    GET /api/users
  RPS:         142
  p50:         68ms
  p95:         850ms     ← outlier suggests tail latency issue
  p99:         2400ms
  Errors:      0.2%
```

### 2. Run clinic doctor

```bash
npx clinic doctor -- node dist/main.js
# In another terminal: npx autocannon ... (same load as baseline)
# Ctrl+C the server when load is done. clinic generates HTML report.
```

`clinic doctor` flags one of:
- **Event Loop Delay**: synchronous CPU hot — go to `clinic flame`
- **GC Pressure**: too much allocation — go to `clinic heapprofiler`
- **I/O**: external bottleneck (DB, HTTP) — go to DB or downstream service profiling

### 3. Drill in with the right tool

Synchronous CPU hot:
```bash
npx clinic flame -- node dist/main.js
# → flamegraph shows the hot stack. Optimize the leaf with most width.
```

Async bottleneck:
```bash
npx clinic bubbleprof -- node dist/main.js
# → bubble timeline shows async chains piling up.
```

Memory leak suspicion:
```bash
node --inspect dist/main.js
# Chrome DevTools → Memory → Take heap snapshot
# Run load. Take snapshot 2. Take snapshot 3.
# Comparison view → look for objects that grow unbounded.
```

### 4. Verify with a SECOND measurement

Single sample lies. After applying a fix:
- Re-run `autocannon` with same params
- Compare p95/p99 (not just p50)
- A 5% improvement in p95 may be within variance — require ≥20% for "fix confirmed"

### 5. Report format

```
## Backend Profiling Report — GET /api/users

| Metric | Baseline | After fix | Δ | Method |
|---|---|---|---|---|
| RPS | 142 | 198 | +39% | autocannon -c50 -d30 |
| p50 | 68ms | 42ms | -38% | same |
| p95 | 850ms | 180ms | -79% | same |
| p99 | 2400ms | 290ms | -88% | same |

Root cause (from clinic flame): JSON.stringify of full user list including
nested permissions on every response. Hot path: routes/users.ts:42.

Fix: select only required fields server-side (Prisma `select:`), p95 dropped
from 850ms to 180ms.

Handoff: backend-db-expert if DB query plan analysis would unlock more.
```

## Hard rules

- NEVER optimize from code appearance alone. Profile first.
- NEVER trust a single sample. Variance >20% → take 3+ samples.
- NEVER conflate p50 with p95. Tail latency is where users feel pain.
- NEVER add caching before identifying the hot path. Caching cold paths is wasted complexity.
- ALWAYS record both before and after numbers in the report. Without before, "after" is a story.

## Anti-patterns

| Anti-pattern | Reality |
|---|---|
| "Endpoint feels slow" | Not data. Run autocannon. |
| "Add Redis cache" | Profile first. The hot path may not be cacheable. |
| "Add more instances" | Vertical scaling masks a code bug. Profile, fix, then scale. |
| "Async-ify everything" | Wrong async pattern can be slower than sync. Measure. |

## When to hand off

| Discovery | Hand off to |
|---|---|
| Slow query revealed in flame graph | `Skill('db-profiling')` then `backend-db-expert` |
| External HTTP call dominates | Investigate that service or add circuit breaker (`resilience-patterns`) |
| Bundle / cold-start issue | `platform-expert` (deployment, runtime config) |
| Memory leak confirmed by snapshots | Stay in this skill — no handoff, fix in code |
