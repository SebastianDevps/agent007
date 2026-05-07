---
name: performance-profiling
description: "Measure-first performance diagnosis: identify bottlenecks across backend, frontend, DB, network with evidence — never opinion. Captures expertise from former performance-optimizer agent."
invokable: true
version: 1.0.0
when:
  keywords:
    - performance
    - profiling
    - bottleneck
    - "N+1"
    - latency
    - slow
    - bundle
    - render
    - lighthouse
    - lcp
    - cls
    - tti
    - ttfb
    - "p95"
    - "p99"
    - memory-leak
    - heap
    - flame-graph
    - query-plan
    - waterfall
    - blocking
canonical-sources:
  - url: https://web.dev/articles/lcp
    when: "for Core Web Vitals references"
  - url: https://nodejs.org/api/inspector.html
    when: "for Node.js profiling and heap snapshots"
  - url: https://www.postgresql.org/docs/current/using-explain.html
    when: "for PostgreSQL EXPLAIN ANALYZE"
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(node *)
  - Bash(npm run *)
  - Bash(pnpm run *)
  - Bash(npx clinic *)
  - Bash(npx lighthouse *)
  - Bash(curl *)
  - Bash(time *)
  - Bash(psql *)
references:
  - references/backend-profiling.md
  - references/frontend-profiling.md
  - references/db-profiling.md
---

# performance-profiling — Measure first, fix second

Specialist in identifying, measuring, and isolating performance bottlenecks. Never recommends a fix without a measured baseline.

## When to invoke

- "X is slow" — treat as hypothesis, not fact
- N+1 query suspicion
- Frontend render bottlenecks (Core Web Vitals failing)
- Memory leak / heap growth
- Bundle size investigation
- API latency p95/p99 spikes
- DB query slowness

## Hard rules

1. **No fix without baseline.** Measure first. "Feels slow" is not data.
2. **No optimization based on code appearance alone.** Profile.
3. **No caching before identifying the hot path.** Caching the cold path is wasted complexity.
4. **No memoization without profiling re-render count.** Premature memo is technical debt.
5. **Query plans for slow queries.** Always EXPLAIN ANALYZE before touching SQL.

## Workflow

### 1. Define metric and target

```
METRIC: [e.g. p95 latency, LCP, query time]
CURRENT: [measured baseline]
TARGET: [explicit threshold — "fast" is not a target]
LAYER: [backend | frontend | db | network]
```

### 2. Profile (layer-specific)

| Layer | Tool | What to capture |
|---|---|---|
| Node.js backend | `npx clinic doctor`, `--inspect` + Chrome DevTools | flame graph, event loop lag, heap |
| API endpoint | `curl -w "@curl-format.txt"` | TTFB, total time |
| PostgreSQL | `EXPLAIN (ANALYZE, BUFFERS) ...` | query plan, scan type, buffer hits |
| Frontend render | React DevTools Profiler, Lighthouse | render count, LCP, CLS, TTI |
| Bundle | `webpack-bundle-analyzer`, `source-map-explorer` | bundle composition |

See `references/backend-profiling.md`, `references/frontend-profiling.md`, `references/db-profiling.md` for layer-specific protocols.

### 3. Isolate the bottleneck

- Narrow to the smallest reproducible case
- Confirm with a second measurement (single sample lies)
- Capture before/after evidence in the report format below

### 4. Report — handoff to specialist

Performance-profiling does NOT apply fixes. Reports findings and hands off:

| Fix requires | Hand off to |
|---|---|
| DB schema/index change | `backend-db-expert` |
| Component refactor | `frontend-ux-expert` |
| Infra/cache layer | `platform-expert` |
| Prod regression | HUMAN (P0) — never auto-fix prod |

## Report format

```markdown
## Performance Report — [Component / Endpoint / Query]

| Layer | Metric | Current | Target | Recommended fix |
|---|---|---|---|---|
| backend | p95 latency | 850ms | <200ms | Add covering index on (user_id, created_at) |

## Profiling evidence

Before: [metric value with method]
After: [metric value with method]
Method: [exact command / tool used]
```

## Anti-patterns

| Anti-pattern | Correct behavior |
|---|---|
| "It's slow, let's add Redis" | Profile first → identify hot path → cache that |
| "useMemo everywhere" | Profile re-renders → memo the actual bottleneck |
| "Optimize the loop" | Run with timer → confirm loop is the bottleneck |
| Skip EXPLAIN for slow queries | Always run EXPLAIN ANALYZE before suggesting SQL changes |
| Single-sample measurement | Always measure multiple times — variance matters |
