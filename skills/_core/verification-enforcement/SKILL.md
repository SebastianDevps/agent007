---
name: verification-enforcement
description: "Reference documentation for verification enforcement rules. Rules embedded in session-orchestrator."
auto-inject: false
priority: reference
version: 3.0.0
---

# Verification Enforcement - Reference Documentation

**Note**: This is reference documentation. The actual verification enforcement rules are embedded in the `session-orchestrator` skill which is auto-loaded and enforces these rules transparently.

**REGLA DE ORO**: ❌ **NO CLAIMS OF COMPLETION WITHOUT RUNNING THE ACTUAL VERIFICATION COMMAND AND READING THE OUTPUT**

---

## 🎯 Propósito

Prevenir el anti-pattern más común en desarrollo asistido por AI:

```diff
- ❌ "This should work now"
- ❌ "The tests should pass"
- ❌ "This will fix the issue"
+ ✅ "I ran `npm test` and here's the output: [actual output]"
+ ✅ "I verified with `curl localhost:3000/api/users` and got: [actual response]"
+ ✅ "The build succeeded: [actual build log]"
```

---

## 🚫 Prohibited Claims Without Evidence

### ❌ NEVER Say Without Verification:

1. **"The tests pass"** → RUN `npm test` and show output
2. **"The build works"** → RUN `npm run build` and show output
3. **"The API works"** → RUN actual request and show response
4. **"This fixes the bug"** → RUN reproduction steps and show it's fixed
5. **"The migration ran"** → RUN migration and show DB state
6. **"Coverage is good"** → RUN `npm run test:cov` and show actual %
7. **"No linting errors"** → RUN `npm run lint` and show output
8. **"The feature works"** → RUN actual feature and show it working

---

## ✅ Verification Requirements

### For Code Changes

**BEFORE claiming completion, run ALL applicable:**

```bash
# 1. TypeScript compilation
npm run build
# → Must show: "Successfully compiled X files"

# 2. Linting
npm run lint
# → Must show: "No linting errors"

# 3. Tests
npm test
# → Must show: "Tests passed: X/X"

# 4. Coverage (if test changes)
npm run test:cov
# → Must show: Actual coverage % and trend

# 5. Application start (if runtime changes)
npm run start:dev
# → Must show: "Application successfully started"

# 6. Actual feature verification
# Run the ACTUAL command/request that uses the feature
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Test"}'
# → Must show: Actual response
```

---

### For Bug Fixes

**MANDATORY verification sequence:**

```bash
# 1. Reproduce bug BEFORE fix
[Run command that triggers bug]
# → Must show: Bug actually happens

# 2. Apply fix

# 3. Verify bug is gone
[Run same command]
# → Must show: Bug no longer happens

# 4. Regression tests
npm test
# → Must show: All tests pass including new test for bug
```

---

### For Refactors

**NO BEHAVIOR CHANGE verification:**

```bash
# 1. Tests pass BEFORE refactor
npm test
# → Must record: "X tests passed"

# 2. Refactor code

# 3. Tests pass AFTER refactor
npm test
# → Must show: SAME X tests passed

# 4. Coverage not decreased
npm run test:cov
# → Must show: Coverage >= previous %
```

---

## 🔍 Verification Checklist

Before claiming ANY task is complete, verify:

- [ ] **Compiled**: TypeScript compiles without errors
- [ ] **Linted**: No linting errors
- [ ] **Tested**: All tests pass (unit + integration)
- [ ] **Coverage**: Coverage meets threshold (>70% for new code)
- [ ] **Runs**: Application starts without errors
- [ ] **Functional**: Actual feature/fix works (manual test)
- [ ] **Documented**: Changes documented if non-trivial
- [ ] **Committed**: Changes committed (if applicable)

### Risk-Based Checklist

**Low Risk** (typo, docs):
- [ ] Linted
- [ ] Committed

**Medium Risk** (new feature):
- [ ] All above +
- [ ] All tests pass
- [ ] Feature manually verified

**High Risk** (refactor, critical feature):
- [ ] All above +
- [ ] Coverage check
- [ ] Integration tests pass
- [ ] Performance check

**Critical Risk** (auth, payments, migrations):
- [ ] All above +
- [ ] Security audit
- [ ] E2E tests pass
- [ ] Manual approval

---

## 🎯 Enforcement Rules

### Rule 1: Fresh Evidence Only

**NEVER reuse old verification output.**

```diff
- ❌ "The tests passed earlier, so they should still pass"
+ ✅ [Runs tests NOW] "Tests pass: [fresh output]"
```

---

### Rule 2: Read Actual Output

**Don't assume, READ the output.**

```diff
- ❌ "I ran the tests" (without showing output)
+ ✅ "I ran `npm test` and got:
      PASS src/users/users.service.spec.ts
      ✓ should create user (15 ms)
      ✓ should find user by id (8 ms)
      Tests: 2 passed, 2 total"
```

---

### Rule 3: Verify in Context

**Run verification in the actual environment.**

```diff
- ❌ "This should work in production"
+ ✅ [Runs in staging] "Verified in staging: [output]"
```

---

### Rule 4: Multiple Verification Layers

**For critical changes, verify at multiple levels:**

```typescript
// Example: New API endpoint

// Layer 1: Unit tests
npm test users.controller.spec.ts
// → ✅ Mocked tests pass

// Layer 2: Integration tests
npm run test:e2e
// → ✅ Real DB tests pass

// Layer 3: Manual API test
curl -X POST http://localhost:3000/api/users \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Test"}'
// → ✅ Actual endpoint works

// Layer 4: Security check
npm run lint:security
// → ✅ No OWASP issues
```

---

## 🚨 Red Flags - Rationalization Detection

Watch for these rationalizations that bypass verification:

### 🚩 Red Flag #1: "Should" Language

```diff
- ❌ "This should fix it"
- ❌ "The tests should pass now"
- ❌ "This should work"
+ ✅ "I verified it works: [evidence]"
```

**Why it's a problem**: "Should" = assumption without evidence.

---

### 🚩 Red Flag #2: "Looks good"

```diff
- ❌ "The code looks good"
- ❌ "This looks correct"
+ ✅ "I verified the code works: [test output]"
```

**Why it's a problem**: Visual inspection ≠ functional verification.

---

### 🚩 Red Flag #3: "Trivial change"

```diff
- ❌ "It's a trivial change, no need to test"
+ ✅ [Runs tests anyway] "Tests confirm it works"
```

**Why it's a problem**: "Trivial" bugs happen. ALWAYS verify.

---

### 🚩 Red Flag #4: "Already tested"

```diff
- ❌ "I tested this earlier"
+ ✅ [Tests again NOW] "Fresh test confirms: [output]"
```

**Why it's a problem**: Code may have changed since "earlier".

---

### 🚩 Red Flag #5: "Just a..."

```diff
- ❌ "Just a typo fix, no verification needed"
- ❌ "Just renaming, tests aren't necessary"
+ ✅ [Verifies anyway] "Typo fixed and verified: [lint output]"
```

**Why it's a problem**: "Just" minimizes risk incorrectly.

---

## 📋 Verification Templates

### For Features

```markdown
## Verification Evidence

### 1. Compilation
```bash
$ npm run build
Successfully compiled 42 files with TypeScript
```

### 2. Tests
```bash
$ npm test -- users.service.spec.ts
PASS src/users/users.service.spec.ts
  UsersService
    ✓ should create user (23 ms)
    ✓ should find user by id (12 ms)
    ✓ should update user (18 ms)
    ✓ should delete user (15 ms)

Tests: 4 passed, 4 total
Time: 2.341 s
```

### 3. Functional Test
```bash
$ curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'

{
  "status": 201,
  "message": "User created successfully",
  "data": {
    "id": "uuid-123",
    "name": "John",
    "email": "john@example.com"
  }
}
```

### 4. Coverage
```bash
$ npm run test:cov

File                | % Stmts | % Branch | % Funcs | % Lines |
--------------------|---------|----------|---------|---------|
users.service.ts    |   92.5  |   87.5   |   100   |   94.2  |
```

✅ All verifications passed. Feature confirmed working.
```

---

### For Bug Fixes

```markdown
## Bug Fix Verification

### 1. Reproduce Bug (BEFORE fix)
```bash
$ curl http://localhost:3000/api/users/invalid-id
{
  "statusCode": 500,
  "message": "Internal server error"  ← BUG
}
```

### 2. Apply Fix
[Fix code]

### 3. Verify Bug Fixed (AFTER fix)
```bash
$ curl http://localhost:3000/api/users/invalid-id
{
  "statusCode": 404,
  "message": "User with ID invalid-id not found"  ← FIXED
}
```

### 4. Regression Test Added
```typescript
it('should return 404 for invalid user id', async () => {
  const response = await request(app.getHttpServer())
    .get('/api/users/invalid-id')
    .expect(404);

  expect(response.body.message).toContain('not found');
});
```

### 5. All Tests Pass
```bash
$ npm test
Tests: 15 passed, 15 total (including new test)
```

✅ Bug confirmed fixed with regression test.
```

---

## ⚡ Integration with Workflows

### Auto-Enforcement Points

This skill is automatically enforced at:

1. **End of executing-plans**: Before claiming task complete
2. **Before two-stage-review**: Must have verification evidence
3. **Before finish**: Final verification checkpoint
4. **After any fix**: Must verify fix works
5. **After refactor**: Must verify behavior unchanged

---

## 🎓 Training Examples

### Example 1: Good Verification

**User**: "Add validation to CreateUserDto"

**Agent**:
```markdown
I've added validation to CreateUserDto:

```typescript
export class CreateUserDto {
  @IsString()
  @MinLength(2)
  name: string;

  @IsEmail()
  email: string;
}
```

Let me verify this works:

```bash
$ npm test -- users.controller.spec.ts
PASS src/users/users.controller.spec.ts
  ✓ should reject invalid email (12 ms)
  ✓ should reject name too short (8 ms)
  ✓ should accept valid user (15 ms)

Tests: 3 passed, 3 total
```

```bash
$ curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "A", "email": "invalid"}'

{
  "statusCode": 400,
  "message": ["name must be at least 2 characters", "email must be valid"],
  "error": "Bad Request"
}
```

✅ Validation confirmed working.
```

---

### Example 2: Bad (Avoided)

**User**: "Add validation to CreateUserDto"

**Agent**: ❌
```markdown
I've added validation decorators. This should validate the email and name length.
The validation should work when you make a request.
```

**Problem**: No actual verification ran. "Should" language used.

---

## 📊 Success Metrics

Track verification compliance:

```json
{
  "sessionId": "abc123",
  "tasksCompleted": 8,
  "verificationsRun": 8,
  "complianceRate": "100%",
  "skipAttempts": 0
}
```

---

## 🎯 Summary

**The Non-Negotiable Rule**:

```
IF you claim something works
THEN you MUST have run the verification command
  AND read the actual output
  AND shown that output as evidence
```

**No exceptions. No shortcuts. Evidence required.**

---

**Auto-injected in**: ALL sessions, ALL workflows
**Can be disabled**: NO (critical skill)
**Override allowed**: NO
