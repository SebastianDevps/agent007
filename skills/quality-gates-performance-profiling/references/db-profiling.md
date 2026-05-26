---
name: performance-profiling/db-profiling
description: "Database (PostgreSQL focus) profiling — query plans, index analysis, lock contention, N+1 detection."
---

# DB Profiling — PostgreSQL (and SQL DBs broadly)

## Tooling

| Tool | What it shows | When |
|---|---|---|
| `EXPLAIN ANALYZE` | Actual execution plan + timing per node | Single slow query |
| `EXPLAIN (ANALYZE, BUFFERS)` | Above + buffer hits/misses | Cache effectiveness |
| `pg_stat_statements` | Aggregate query stats over time | "Which queries dominate?" |
| `auto_explain` | Logs plans for slow queries automatically | Production observability |
| ORM debug logs (Prisma `log: ['query']`, TypeORM `logging: true`) | Queries actually emitted | Detect N+1 |
| `pgbench` | Synthetic write/read load | Capacity planning |

## Standard protocol

### 1. Find the offending query

```sql
-- Top queries by total time (requires pg_stat_statements extension)
SELECT
  query,
  calls,
  total_exec_time,
  mean_exec_time,
  rows,
  100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_rate
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

If user comes with a known slow query, skip this and go to step 2.

### 2. Run `EXPLAIN (ANALYZE, BUFFERS)`

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.*, p.permissions
FROM users u
JOIN user_permissions p ON p.user_id = u.id
WHERE u.organization_id = $1
ORDER BY u.created_at DESC
LIMIT 50;
```

Read the plan. Watch for:

| Plan node | Red flag | Fix |
|---|---|---|
| `Seq Scan` on large table | Missing index | `CREATE INDEX ON ... (column)` |
| `Nested Loop` with large outer | Missing FK index | Index on the join column |
| `Sort` with large rows estimate | Missing covering index | Index includes ORDER BY column |
| `Hash Join` with `Buffers: temp written=...` | Sort spilled to disk → `work_mem` too small | Increase `work_mem` for the session, or add index |
| `Rows Removed by Filter: 99000` | Index not selective enough | Add a partial or composite index |
| `Bitmap Heap Scan` huge `Heap Fetches:` | Index-only scan would help | `INCLUDE` columns in index |

### 3. Detect N+1 via ORM logs

Turn on query logging temporarily:

```ts
// Prisma
const prisma = new PrismaClient({ log: ['query'] });

// TypeORM
new DataSource({ ..., logging: true });
```

Run the affected endpoint **once**. If you see:
```
SELECT * FROM users WHERE organization_id = $1
SELECT * FROM permissions WHERE user_id = $1
SELECT * FROM permissions WHERE user_id = $2
SELECT * FROM permissions WHERE user_id = $3
... (50 times)
```

Classic N+1. Fix: `include`/`relations` (Prisma/TypeORM eager) OR a single JOIN.

### 4. Apply fix and re-measure

```sql
-- After CREATE INDEX or query rewrite:
EXPLAIN (ANALYZE, BUFFERS) <same query>;

-- Compare:
--   Execution Time:     Before vs After
--   Buffers shared hit: should increase
--   Buffers shared read: should decrease
```

### 5. Verify under realistic load

Single-query speed isn't enough. Run the endpoint with autocannon and check
the application-level p95.

```bash
npx autocannon -c 50 -d 30 http://localhost:3000/api/users
```

### 6. Report format

```
## DB Profiling Report — GET /api/users (org-scoped, paginated)

### Diagnosis
N+1 confirmed via Prisma query log: 1 outer query + 50 permission lookups
per request.

### Plan before
Nested Loop  (cost=0.42..2840.18 rows=50 width=128) (actual time=0.142..520.4 rows=50 loops=1)
  -> Seq Scan on users  (filter org_id=$1)  Rows Removed by Filter: 99500
  -> Index Scan on permissions_pkey

### Fix
1. Composite index: CREATE INDEX idx_users_org_created ON users (organization_id, created_at DESC);
2. Use Prisma `include: { permissions: true }` to merge into one query.

### Plan after
Index Scan using idx_users_org_created  (cost=0.42..120.18 rows=50 width=128) (actual time=0.082..1.4 rows=50 loops=1)
   -> Hash Join with permissions

### Numbers
| Metric | Before | After | Δ |
|---|---|---|---|
| Query time | 520ms | 1.4ms | -99.7% |
| API p95 | 850ms | 32ms | -96% |
| Queries per request | 51 | 1 | -98% |

Handoff: none — index migration + Prisma query change committed.
```

## Hard rules

- NEVER add an index without confirming the planner uses it (`EXPLAIN` after creation)
- NEVER drop an index without checking `pg_stat_user_indexes` for usage
- NEVER use `SELECT *` in hot paths — wide rows kill cache hit rate
- NEVER measure on a tiny dataset — seed prod-like volume before profiling
- ALWAYS check `Rows Removed by Filter` — high values indicate index selectivity problem
- ALWAYS look at p95 of the API, not just the single-query time

## Anti-patterns

| Anti-pattern | Reality |
|---|---|
| "Just add an index on every WHERE column" | Indexes cost write throughput. Profile first. |
| "Switch to NoSQL because slow" | Almost always a missing index. Profile, don't migrate. |
| Trusting ORM query optimization | ORMs emit naïve queries. Always check the actual SQL. |
| `SELECT *` in API responses | Wider rows, more network, no covering index possible. |
| Running EXPLAIN without ANALYZE | Estimates lie. ANALYZE shows actual rows + time. |

## Locks and contention (advanced)

If queries are intermittently slow under load:

```sql
-- Active locks
SELECT pid, mode, locktype, relation::regclass, granted
FROM pg_locks
WHERE NOT granted;

-- Blocked queries
SELECT
  blocked_locks.pid AS blocked_pid,
  blocking_locks.pid AS blocking_pid,
  blocked_activity.query AS blocked_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
  ON blocking_locks.locktype = blocked_locks.locktype
  AND blocking_locks.pid <> blocked_locks.pid
  AND blocking_locks.granted
WHERE NOT blocked_locks.granted;
```

Common causes:
- Long-running transaction holding row locks
- Autovacuum running on large table (rarely the real cause; check first)
- DDL waiting behind a long SELECT

## When to hand off

| Discovery | Hand off to |
|---|---|
| Schema redesign needed | `backend-db-expert` |
| Migration plan for index in prod | `platform-expert` (deployment, lock-aware migrations) |
| Read replica strategy | `architect` patterns + `backend-db-expert` |
| Fix is in app code, not DB | Stay in `performance-profiling` |
