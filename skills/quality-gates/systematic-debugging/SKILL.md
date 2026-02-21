---
name: systematic-debugging
description: "4-phase mandatory debugging process: Reproduce → Root Cause → Hypothesis → Implementation. NO FIXES WITHOUT ROOT CAUSE. Auto-activated for bug fixes."
invokable: true
accepts_args: bugDescription
auto-activate: bug-fixing (all levels)
required-before: Any bug fix implementation
version: 2.0.0
when:
  - task_type: bug
    risk_level: [low, medium, high, critical]
  - user_mentions: ["bug", "error", "fix", "broken", "not working", "fails"]
---

# Systematic Debugging - NO FIXES WITHOUT ROOT CAUSE

**REGLA FUNDAMENTAL**: ❌ **NO BUG FIXES WITHOUT ROOT CAUSE ANALYSIS**

Este skill enforce un proceso de debugging de 4 fases obligatorias.

---

## 🎯 Por Qué Systematic Debugging

### El Anti-Pattern: Quick Fix Sin Root Cause

```diff
❌ MAL:
User: "Users endpoint returns 500 error"
Agent: "Let me add a try-catch..." [Quick fix]
Result: Bug hidden, no comprensión de causa, reaparece después

✅ BIEN:
User: "Users endpoint returns 500 error"
Agent: [Phase 1: Reproduce with test]
       [Phase 2: Root Cause - N+1 query causing timeout]
       [Phase 3: Hypothesis - eager loading fixes it]
       [Phase 4: Implement + defense-in-depth]
Result: Bug entendido, fix correcto, prevención de recurrencia
```

**Costo de quick fixes**: 10x más caro arreglar el mismo bug múltiples veces.

---

## 📋 The 4 Phases (Mandatory)

### Phase 1: Reproduce ✅

**Objetivo**: Crear un test que DEMUESTRE el bug consistentemente.

**Prohibido proceder** sin reproducción confiable.

```typescript
// Example: N+1 query bug

describe('UsersController', () => {
  it('should not cause N+1 queries when fetching users with orders', async () => {
    // Setup: Create 10 users with 5 orders each
    const users = await createUsersWithOrders(10, 5);

    // Enable query logging
    const queryLogger = new QueryLogger();

    // Trigger the bug
    const response = await request(app.getHttpServer())
      .get('/api/users?include=orders')
      .expect(200);

    // Assert: Should be 1 query (with JOIN), not 11 (1 + 10)
    expect(queryLogger.count()).toBe(1);  // ❌ FAILS with 11 queries
  });
});
```

**Verification**:
```bash
$ npm test -- users.controller.spec.ts
FAIL - Test reproduces bug ✅ (this is expected, we WANT it to fail)
```

**Success Criteria Phase 1**:
- [ ] Test created that demonstrates bug
- [ ] Test fails consistently (not flaky)
- [ ] Test is minimal (no unnecessary complexity)
- [ ] Failure message is clear

**⚠️ CHECKPOINT**: Cannot proceed to Phase 2 without reproducible test.

---

### Phase 2: Root Cause Analysis ✅

**Objetivo**: Identificar la CAUSA RAÍZ del bug, no solo el síntoma.

**Técnicas**:

#### 1. **5 Whys Method**

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

#### 2. **Stack Trace Analysis**

```typescript
// Read the FULL stack trace
Error: Query timeout after 30000ms
    at QueryExecutor.execute (typeorm/query-executor.ts:245)
    at Repository.find (typeorm/repository.ts:89)
    at UsersService.findAll (users.service.ts:42)  // ← SOURCE
    at UsersController.findAll (users.controller.ts:28)
```

**Look for**:
- Where in YOUR code did it start? (not framework code)
- What was the last successful operation?
- Are there patterns in when it fails?

#### 3. **Logging & Inspection**

```typescript
// Add strategic logging
async findAll(): Promise<User[]> {
  console.log('[DEBUG] Starting findAll');
  const users = await this.userRepository.find();
  console.log(`[DEBUG] Found ${users.length} users`);

  // ← BUG: This loops and queries for each user
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

#### 4. **Compare Working vs Broken**

```typescript
// What changed between working version and broken version?

// Git diff
$ git diff HEAD~5 src/users/users.service.ts

- return this.userRepository.find({ relations: ['orders'] });  // WORKING
+ return this.userRepository.find();  // BROKEN (removed relations)
```

**Documentation Template**:

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

**⚠️ CHECKPOINT**: Cannot proceed to Phase 3 without documented root cause.

---

### Phase 3: Hypothesis & Testing ✅

**Objetivo**: Proponer solución y VALIDAR que realmente arregla el root cause.

**Process**:

#### 1. Form Hypothesis

```markdown
## Hypothesis

**Proposed Fix**: Add eager loading to restore JOIN query

**Expected Outcome**:
- Single query with LEFT JOIN instead of 1001 queries
- Response time: 50ms (down from 30s+)
- Test from Phase 1 will pass

**Code Change**:
```typescript
// Before (broken)
return this.userRepository.find();

// After (fixed)
return this.userRepository.find({
  relations: ['orders']  // Eager load with JOIN
});
```

**Why This Should Work**:
TypeORM `relations` option generates a LEFT JOIN,
fetching users + orders in single query.
```

#### 2. Validate Hypothesis (Without Implementing)

**Check 1: Query Analysis**
```sql
-- Expected query with fix:
SELECT users.*, orders.*
FROM users
LEFT JOIN orders ON orders.user_id = users.id;
-- Result: 1 query
```

**Check 2: TypeORM Documentation**
```
✅ Confirmed: relations option does eager loading
✅ Confirmed: Uses JOIN, not separate queries
```

**Check 3: Similar Code in Project**
```typescript
// Other places using eager loading successfully
const products = await this.productRepository.find({
  relations: ['reviews']  // ← Works fine
});
```

#### 3. Alternative Hypotheses (Consider)

```markdown
## Alternative Solutions Considered

**Alternative 1**: Use QueryBuilder
```typescript
return this.userRepository
  .createQueryBuilder('user')
  .leftJoinAndSelect('user.orders', 'orders')
  .getMany();
```
✅ Pro: More explicit control
❌ Con: More verbose
Decision: Use relations option (simpler, same result)

**Alternative 2**: Lazy loading
```typescript
@OneToMany(() => Order, order => order.user, { lazy: true })
orders: Promise<Order[]>;
```
❌ Con: Still N queries, just async
Decision: Rejected

**Alternative 3**: DataLoader pattern
✅ Pro: Batches queries
❌ Con: Adds complexity, overkill for this
Decision: Rejected for now, consider if performance still issues
```

**Success Criteria Phase 3**:
- [ ] Hypothesis formed with expected outcome
- [ ] Hypothesis validated against documentation
- [ ] Alternative solutions considered
- [ ] Chosen solution justified

**⚠️ CHECKPOINT**: Cannot proceed to Phase 4 without validated hypothesis.

---

### Phase 4: Implementation + Defense-in-Depth ✅

**Objetivo**: Implementar fix + agregar safeguards para prevenir recurrencia.

#### Step 1: Implement Fix

```typescript
// src/users/users.service.ts

async findAll(): Promise<User[]> {
  // FIX: Add eager loading to prevent N+1
  return this.userRepository.find({
    relations: ['orders']
  });
}
```

#### Step 2: Verify Fix Works

```bash
# Run test from Phase 1
$ npm test -- users.controller.spec.ts

PASS - Test now passes ✅
  UsersController
    ✓ should not cause N+1 queries (45 ms)

# Check query logs
Query: SELECT users.*, orders.* FROM users LEFT JOIN orders...
Total queries: 1 ✅ (was 1001)
```

#### Step 3: Defense-in-Depth

**Add safeguards to prevent this bug from happening again:**

##### Safeguard 1: Add Query Logging Test

```typescript
// tests/performance/n-plus-one.spec.ts

describe('N+1 Query Prevention', () => {
  it('all user queries should use eager loading', async () => {
    const queryLogger = new QueryLogger();

    // Test all user-related endpoints
    await request(app).get('/api/users');
    await request(app).get('/api/users/123');
    await request(app).get('/api/users?filter=active');

    // Assert: No endpoint should cause > 5 queries
    expect(queryLogger.maxQueriesPerRequest()).toBeLessThan(5);
  });
});
```

##### Safeguard 2: Add ESLint Rule

```javascript
// .eslintrc.js

module.exports = {
  rules: {
    // Custom rule: Warn if find() called without relations on entities with relationships
    'typeorm/require-relations': 'warn'
  }
};
```

##### Safeguard 3: Add Documentation

```typescript
// src/users/users.service.ts

/**
 * Fetch all users with their orders.
 *
 * IMPORTANT: Always use `relations: ['orders']` to avoid N+1 queries.
 * See: docs/performance/n-plus-one-prevention.md
 *
 * @returns Promise<User[]> Users with eager-loaded orders
 */
async findAll(): Promise<User[]> {
  return this.userRepository.find({
    relations: ['orders']  // Required to prevent N+1
  });
}
```

##### Safeguard 4: Add Performance Budget

```typescript
// tests/performance/budgets.spec.ts

describe('Performance Budgets', () => {
  it('/api/users should respond in <100ms', async () => {
    const start = Date.now();
    await request(app).get('/api/users');
    const duration = Date.now() - start;

    expect(duration).toBeLessThan(100);  // Budget: 100ms
  });
});
```

##### Safeguard 5: Update Knowledge Base

```markdown
# knowledge/lessons/n-plus-one-prevention.md

## Lesson: N+1 Query in Users Endpoint

**Date**: 2026-02-06
**Bug**: /api/users timeout due to N+1 queries

**Root Cause**: Missing `relations: ['orders']` in find()

**Fix**: Always use eager loading for relationships:
```typescript
// ✅ CORRECT
repo.find({ relations: ['orders'] })

// ❌ INCORRECT
repo.find()  // Missing relations, causes N+1
```

**Prevention**:
- Add query count assertions in tests
- Use ESLint rule to warn on missing relations
- Document all relationship-loading patterns
```

#### Step 4: Regression Test

```typescript
// Add regression test to prevent re-introduction

describe('Regression: N+1 Query Bug', () => {
  it('should not regress to N+1 queries (Issue #123)', async () => {
    // This test was added after fixing N+1 bug in users endpoint
    // See: https://github.com/company/project/issues/123

    const queryLogger = new QueryLogger();
    await request(app).get('/api/users');

    expect(queryLogger.count()).toBe(1);  // Must stay at 1 query
  });
});
```

**Success Criteria Phase 4**:
- [ ] Fix implemented
- [ ] Original test (Phase 1) now passes
- [ ] Defense-in-depth measures added (at least 2)
- [ ] Regression test added
- [ ] Knowledge base updated
- [ ] Performance verified (before vs after)

---

## 🚫 Red Flags - Skipping Systematic Debugging

### 🚩 Red Flag #1: "I Know What the Problem Is"

```diff
- ❌ "I know it's a database issue, let me add an index"
+ ✅ "Let me reproduce it first, then analyze root cause"
```

**Problem**: Assumptions without evidence lead to wrong fixes.

---

### 🚩 Red Flag #2: "Quick Fix First, Investigate Later"

```diff
- ❌ "Let me wrap it in try-catch for now, we'll debug later"
+ ✅ "No fixes until root cause identified"
```

**Problem**: "Later" never comes, bug remains hidden.

---

### 🚩 Red Flag #3: "It's Too Complex to Reproduce"

```diff
- ❌ "The bug is intermittent, I'll just add more logging"
+ ✅ "I'll create conditions that make it reproducible"
```

**Problem**: Can't fix what you can't reproduce.

---

### 🚩 Red Flag #4: "The Fix Looks Good"

```diff
- ❌ "This should fix it" (without running test)
+ ✅ "Test passes, bug confirmed fixed: [output]"
```

**Problem**: verification-enforcement should catch this.

---

## 📊 Systematic Debugging Checklist

Before claiming bug is fixed:

**Phase 1: Reproduce**
- [ ] Test created that demonstrates bug
- [ ] Test fails reliably
- [ ] Failure is clear and specific

**Phase 2: Root Cause**
- [ ] Root cause identified (not symptom)
- [ ] 5 Whys completed
- [ ] Evidence documented
- [ ] Root cause is actionable

**Phase 3: Hypothesis**
- [ ] Solution proposed
- [ ] Expected outcome defined
- [ ] Hypothesis validated
- [ ] Alternatives considered

**Phase 4: Implementation**
- [ ] Fix implemented
- [ ] Test passes
- [ ] Defense-in-depth added (2+ safeguards)
- [ ] Regression test added
- [ ] Performance verified
- [ ] Knowledge base updated

---

## 🎓 Examples by Bug Type

### Example 1: Performance Bug (N+1 Query)

**Phase 1**: Create test showing 1001 queries
**Phase 2**: Root cause = missing eager loading
**Phase 3**: Hypothesis = add relations option
**Phase 4**: Implement + add query count assertions

---

### Example 2: Security Bug (SQL Injection)

**Phase 1**: Create test with malicious input
**Phase 2**: Root cause = string concatenation in query
**Phase 3**: Hypothesis = use parameterized queries
**Phase 4**: Implement + add security tests + OWASP check

---

### Example 3: Logic Bug (Incorrect Calculation)

**Phase 1**: Create test with known inputs/outputs
**Phase 2**: Root cause = off-by-one error in loop
**Phase 3**: Hypothesis = fix loop bounds
**Phase 4**: Implement + add edge case tests + documentation

---

### Example 4: Race Condition

**Phase 1**: Create test that triggers concurrent requests
**Phase 2**: Root cause = missing transaction isolation
**Phase 3**: Hypothesis = use database transactions
**Phase 4**: Implement + add concurrency tests + defense-in-depth

---

## 🔄 Integration with Workflow

### Auto-Enforcement

```typescript
if (taskType === 'bug' && riskLevel >= 'medium') {
  enforce('systematic-debugging');

  // Block any fix implementation until all 4 phases complete
  phases = ['reproduce', 'root-cause', 'hypothesis', 'implementation'];

  for (phase of phases) {
    await completePhase(phase);
    await verifyPhaseComplete(phase);  // Checkpoint
  }
}
```

### Integration with TDD

```typescript
// Systematic debugging integrates with TDD naturally:

// Phase 1 (Reproduce) = TDD RED
test('bug reproduction', () => {
  expect(buggyFunction()).toBe(expected);  // FAILS ✅
});

// Phase 4 (Implementation) = TDD GREEN
// Fix applied
test('bug reproduction', () => {
  expect(fixedFunction()).toBe(expected);  // PASSES ✅
});

// Defense-in-depth = TDD REFACTOR
// Add safeguards, improve code quality
```

---

## 📈 Success Metrics

Track debugging quality:

```json
{
  "bugFixes": 15,
  "systematicDebuggingCompliance": "100%",
  "phasesCompleted": {
    "reproduce": 15,
    "rootCause": 15,
    "hypothesis": 15,
    "implementation": 15
  },
  "defenseInDepthAdded": {
    "tests": 15,
    "documentation": 12,
    "lintRules": 5,
    "performanceBudgets": 8
  },
  "regressionRate": "0%"  // No bugs returned after fix
}
```

---

## 🎯 Summary

**Systematic Debugging Rule**:
```
FOR every bug fix:
  PHASE 1: Create test that reproduces bug (must fail)
  PHASE 2: Identify root cause (not symptom)
  PHASE 3: Form hypothesis and validate
  PHASE 4: Implement + defense-in-depth + regression test

NO shortcuts. NO quick fixes. NO "I know what it is."
```

**Remember**: The most expensive bug is the one that comes back.

---

## Ralph Loop Integration (v2.0)

This skill is **Ralph-ready** for iterative debugging.

### Completion Signal

When the bug is fixed in Ralph mode, output:

```
<promise>BUG_FIXED</promise>
```

### Completion Criteria

Before outputting completion promise, verify ALL of these:

- [ ] Phase 1 (Reproduce): Test that reproduces bug exists and FAILED initially
- [ ] Phase 2 (Root Cause): Root cause documented with 5 Whys
- [ ] Phase 3 (Hypothesis): Fix approach validated
- [ ] Phase 4 (Implementation): Fix implemented
- [ ] Failing test now PASSES
- [ ] Full test suite still GREEN (no regression)
- [ ] Defense-in-depth added (at least 1 safeguard)

### Self-Correction in Ralph Mode

**Iteration 1 (Reproduce Phase)**:
- Create test that demonstrates the bug
- Run test → MUST fail
- If test passes, bug not reproduced yet
- No completion promise

**Iterations 2-3 (Root Cause Phase)**:
- Apply 5 Whys to find root cause
- Use stack traces, logs, git diff
- Document actual cause (not symptom)
- No completion promise (diagnosis only)

**Iterations 4-N (Fix Phase)**:
- Implement hypothesis
- Run failing test → Check if passes
- Run full suite → Check no regression
- If test passes + suite green + defense added → `<promise>BUG_FIXED</promise>`
- If test still fails → re-analyze, try different fix

### Stall Prevention

If stalled (same error 5+ iterations), Ralph will escalate by injecting:

```
SYSTEMATIC DEBUGGING TEMPLATE INJECTION

You are stuck on the same error. Apply the 4-phase process rigorously:

Phase 1: REPRODUCE
- Write a test that FAILS consistently
- Show actual test output (not "it fails")

Phase 2: ROOT CAUSE (5 Whys)
- Why 1: [surface symptom]
- Why 2: [deeper cause]
- Why 3: [technical cause]
- Why 4: [code-level cause]
- Why 5: [root cause]

Phase 3: HYPOTHESIS
- Proposed fix: [specific code change]
- Why this should work: [explanation]
- Alternatives considered: [what else you thought of]

Phase 4: IMPLEMENT
- Apply fix
- Run test → Show output
- Add safeguard (regression test, validation, etc.)
```

### Example Ralph Debugging Flow

```
Iteration 1 (Reproduce):
  → Create test: GET /api/users should not N+1
  → Run test → FAIL (1001 queries detected)
  → Document: Reproduced ✅

Iteration 2 (Root Cause):
  → Apply 5 Whys
  → Root cause: Missing `relations: ['orders']` in find()
  → Document: Root cause found ✅

Iteration 3 (Hypothesis):
  → Hypothesis: Add eager loading
  → Validate: TypeORM docs confirm this fixes N+1
  → Document: Hypothesis validated ✅

Iteration 4 (Implement):
  → Add `relations: ['orders']` to repository.find()
  → Run test → PASS (1 query now) ✅
  → Run full suite → PASS (no regression) ✅
  → Add regression test to prevent re-introduction
  → Output: <promise>BUG_FIXED</promise> ✅
```

### Defense-in-Depth Requirements

Don't output completion promise without at least ONE safeguard:

1. **Regression Test**: Test that prevents bug re-introduction
2. **Performance Budget**: Assertion on query count/response time
3. **Linting Rule**: ESLint/custom rule that catches pattern
4. **Documentation**: Code comment explaining the gotcha
5. **Type Safety**: TypeScript type that prevents misuse

Example:
```typescript
// After fixing N+1:
it('should not regress to N+1 queries (Issue #123)', async () => {
  const queryLogger = new QueryLogger();
  await request(app).get('/api/users');
  expect(queryLogger.count()).toBeLessThan(5); // Safeguard ✅
});
```

---

**Auto-Activated In**: All bug-fixing workflows (all risk levels)
**Ralph-Ready**: ✅ Yes (v2.0)
**Can Be Skipped**: NO (mandatory for bugs medium+ risk)
**Integrates With**: test-driven-development, verification-enforcement, ralph-loop-wrapper
