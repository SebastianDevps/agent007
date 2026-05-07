# Phase 2: Root Cause Analysis

**Objetivo**: Identificar la CAUSA RAÍZ del bug, no solo el síntoma.

## Técnicas

### 1. 5 Whys Method

```
Symptom: "API returns 500 error"

Why 1: Why does it return 500?
→ Because database query times out

Why 2: Why does the query timeout?
→ Because it takes 30 seconds to complete

Why 3: Why does it take 30 seconds?
→ Because it runs 1001 queries (1 + 1000)

Why 4: Why does it run 1001 queries?
→ Because each user's orders are fetched in a separate query

Why 5: Why are orders fetched separately?
→ Because `relations: ['orders']` is missing from find()

ROOT CAUSE: Missing eager loading configuration
```

### 2. Stack Trace Analysis

```typescript
// Read the FULL stack trace
Error: Query timeout after 30000ms
    at QueryExecutor.execute (typeorm/query-executor.ts:245)
    at Repository.find (typeorm/repository.ts:89)
    at UsersService.findAll (users.service.ts:42)  // SOURCE
    at UsersController.findAll (users.controller.ts:28)
```

**Look for**:
- Where in YOUR code did it start? (not framework code)
- What was the last successful operation?
- Are there patterns in when it fails?

### 3. Logging & Inspection

```typescript
// Add strategic logging
async findAll(): Promise<User[]> {
  console.log('[DEBUG] Starting findAll');
  const users = await this.userRepository.find();
  console.log(`[DEBUG] Found ${users.length} users`);

  // BUG: This loops and queries for each user
  for (const user of users) {
    console.log(`[DEBUG] Fetching orders for user ${user.id}`);
    user.orders = await this.orderRepository.find({ userId: user.id });
  }

  return users;
}
```

**Output reveals N+1**:
```
[DEBUG] Starting findAll
[DEBUG] Found 1000 users
[DEBUG] Fetching orders for user 1
[DEBUG] Fetching orders for user 2
[DEBUG] Fetching orders for user 3
... (997 more times)
```

### 4. Compare Working vs Broken

```typescript
// What changed between working version and broken version?

// Git diff
$ git diff HEAD~5 src/users/users.service.ts

- return this.userRepository.find({ relations: ['orders'] });  // WORKING
+ return this.userRepository.find();  // BROKEN (removed relations)
```

## Documentation Template

```markdown
## Root Cause Analysis

**Bug**: API endpoint /api/users times out with 500 error

**Symptom**: Request takes 30+ seconds, times out

**Root Cause**: N+1 query problem
- Initial query fetches 1000 users
- Loop fetches orders for each user (1000 additional queries)
- Total: 1001 queries instead of 1

**Why It Happened**:
`relations: ['orders']` was removed in commit abc123,
likely during refactor to "simplify" the query.

**Evidence**:
- Query logs show 1001 SELECT statements
- Performance degraded from 50ms to 30s+
- Test confirms behavior (see Phase 1)

**Impact**:
- Affects all requests to /api/users with >100 users
- Causes timeouts in production
- High database load
```

**Success Criteria Phase 2**:
- [ ] Root cause identified (not just symptom)
- [ ] Evidence documented (logs, traces, diffs)
- [ ] "5 Whys" completed
- [ ] Root cause is actionable (can be fixed)

**CHECKPOINT**: Cannot proceed to Phase 3 without documented root cause.
