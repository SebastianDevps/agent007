---
name: anti-rationalization
description: "Reference documentation for anti-rationalization rules. Rules embedded in session-orchestrator."
auto-inject: false
priority: reference
version: 3.0.0
---

# Anti-Rationalization - Reference Documentation

**Note**: This is reference documentation. The actual anti-rationalization rules are embedded in the `session-orchestrator` skill which is auto-loaded and enforces these rules transparently.

**Propósito**: Documenta los patrones de rationalización que deben prevenirse y cómo evitarlos.

---

## 🧠 El Problema: Rationalizations Plausibles

Las racionalizaciones más peligrosas suenan razonables:

```diff
❌ "It's just a typo, no need for tests"
   → Sounds reasonable, but typos in critical files cause outages

❌ "I'm confident this works, verification would be redundant"
   → Sounds reasonable, but confidence ≠ correctness

❌ "This is a trivial change, the full pipeline is overkill"
   → Sounds reasonable, but "trivial" bugs happen

❌ "The code is simple, no need for TDD"
   → Sounds reasonable, but simple code still needs tests
```

**Insight**: The best rationalizations feel smart, not lazy.

---

## 📋 Rationalization Table

| Rationalization | Why It Sounds Good | Why It's Wrong | What To Do Instead |
|-----------------|--------------------|-----------------|--------------------|
| **"Just a typo"** | Typos seem harmless | Typos in config/auth/SQL are catastrophic | Run lint + tests anyway |
| **"I'm confident"** | Expertise feels reliable | Even experts make mistakes | Verify with evidence |
| **"Trivial change"** | Small changes feel safe | 1-line changes cause bugs too | Follow standard gates |
| **"Already tested"** | Avoids redundancy | Code may have changed | Test again fresh |
| **"This should work"** | Logic seems sound | "Should" ≠ "does" | Run actual verification |
| **"Too simple for TDD"** | Seems like overhead | Tests catch simple bugs too | Write tests anyway |
| **"No time for..."** | Pragmatic trade-off | Shortcuts create technical debt | Make time, avoid debt |
| **"Obviously correct"** | Logical certainty | Obvious != tested | Verify the obvious |
| **"Edge case"** | Low probability | Edge cases happen in production | Handle edge cases |
| **"Only dev environment"** | Not production risk | Dev bugs waste time | Treat dev like prod |

---

## 🚩 Red Flags - Rationalization Patterns

### Category 1: Minimization

**Pattern**: Using minimizing language to justify skipping steps.

| Phrase | Red Flag | Correct Response |
|--------|----------|------------------|
| "just a..." | Minimizes risk | NO shortcuts for "just" anything |
| "only..." | Downplays scope | Size doesn't determine gates needed |
| "simply..." | Suggests ease | Simple code still needs verification |
| "trivial..." | Dismisses importance | No change is too trivial to verify |
| "minor..." | Reduces perceived impact | All changes get appropriate gates |

**Example**:
```diff
- ❌ "It's just a typo in a comment, no verification needed"
+ ✅ "Even comment changes get linting" → runs `npm run lint`
```

---

### Category 2: Confidence Claims

**Pattern**: Substituting confidence for evidence.

| Phrase | Red Flag | Correct Response |
|--------|----------|------------------|
| "I'm confident..." | Confidence ≠ proof | Provide evidence, not confidence |
| "I'm sure..." | Certainty ≠ verification | Show test output, not certainty |
| "Obviously..." | Assumption | Verify the "obvious" |
| "Clearly..." | Unexamined belief | Make it explicit with tests |
| "Should work..." | Speculation | Run it and confirm |

**Example**:
```diff
- ❌ "I'm confident this fixes the bug"
+ ✅ "I verified the bug is fixed: [test output showing bug reproduced before, fixed after]"
```

---

### Category 3: Temporal Excuses

**Pattern**: Using time-related reasons to skip steps.

| Phrase | Red Flag | Correct Response |
|--------|----------|------------------|
| "No time for..." | Efficiency fallacy | Fixing bugs takes longer than preventing them |
| "Already..." | Stale verification | Re-verify fresh |
| "Later..." | Deferred quality | Quality gates are not optional |
| "Eventually..." | Postponed rigor | Do it now, not "eventually" |
| "Quick fix..." | Speed over correctness | Quick ≠ skip verification |

**Example**:
```diff
- ❌ "No time for writing tests, I'll add them later"
+ ✅ "TDD is non-negotiable" → writes test first (RED → GREEN → REFACTOR)
```

---

### Category 4: Expertise Appeal

**Pattern**: Using experience/expertise to bypass process.

| Phrase | Red Flag | Correct Response |
|--------|----------|------------------|
| "I know this works..." | Experience ≠ omniscience | Experts make mistakes too, verify |
| "I've done this before..." | Past ≠ future | Context may differ, verify |
| "Trust me..." | Authority argument | Trust, but verify |
| "In my experience..." | Anecdotal | Show data, not anecdotes |
| "I'm an expert..." | Credential argument | Even experts follow process |

**Example**:
```diff
- ❌ "I've implemented auth systems before, I know this is secure"
+ ✅ "Let's run the security audit" → runs `npm run lint:security` + OWASP checklist
```

---

## 🛡️ Defense Mechanisms

### Defense 1: Automatic Red Flag Detection

When user/agent says phrases from the table, AUTO-TRIGGER response:

```typescript
// Pseudo-code
if (message.contains(['just', 'only', 'simply', 'trivial', 'minor'])) {
  respond('⚠️ Minimization detected. All changes require appropriate gates.');
  enforce_standard_gates();
}

if (message.contains(['should work', 'I\'m confident', 'obviously'])) {
  respond('⚠️ Confidence claim without evidence. Verification required.');
  require_verification_evidence();
}

if (message.contains(['no time', 'later', 'quick fix'])) {
  respond('⚠️ Temporal excuse detected. Quality gates are not optional.');
  block_completion_until_gates_pass();
}
```

---

### Defense 2: Counter-Rationalization

For each rationalization, provide a counter-argument:

**Rationalization**: "It's just a typo"
**Counter**: "Typos in SQL cause injection. Typos in auth bypass security. Typos in config cause outages. No typo is 'just' a typo."

**Rationalization**: "I'm confident this works"
**Counter**: "Confidence is not evidence. Show me the test output."

**Rationalization**: "This is too simple for TDD"
**Counter**: "If it's simple, writing a test is simple too. Write it."

**Rationalization**: "No time for tests right now"
**Counter**: "Fixing bugs takes longer than writing tests. Make time."

---

### Defense 3: Required Sub-Skill Enforcement

When rationalization detected, auto-invoke dependent skill:

| Rationalization Type | Auto-Invoke Skill |
|---------------------|-------------------|
| Skip verification | `verification-enforcement` |
| Skip TDD | `test-driven-development` |
| Skip root cause analysis | `systematic-debugging` |
| Skip planning | `writing-plans` |
| Skip review | `two-stage-review` |

---

## 📚 Examples of Rationalization in Action

### Example 1: The "Just" Rationalization

**Scenario**: Typo in auth middleware

**❌ Bad (Rationalization)**:
```
Agent: "I fixed the typo in the auth middleware. It's just a simple typo (changing 'Bearer' to 'Bearer'), so no tests needed."
```

**✅ Good (Anti-Rationalization)**:
```
Agent: "I fixed the typo in the auth middleware. Even though it's a typo, auth is critical. Let me verify:

```bash
$ npm test -- auth.middleware.spec.ts
PASS src/auth/auth.middleware.spec.ts
  ✓ should authenticate with valid Bearer token (18 ms)
  ✓ should reject invalid token format (12 ms)

$ curl -H "Authorization: Bearer test-token" http://localhost:3000/protected
{
  "message": "Authenticated",
  "userId": "123"
}
```

✅ Typo fixed and verified working.
```

---

### Example 2: The Confidence Rationalization

**Scenario**: Bug fix for N+1 query

**❌ Bad (Rationalization)**:
```
Agent: "I added `relations: ['orders']` to the query. I'm confident this fixes the N+1 problem. The solution is standard."
```

**✅ Good (Anti-Rationalization)**:
```
Agent: "I added eager loading to fix the N+1 problem. Let me verify it actually fixes it:

BEFORE (with query logging):
```sql
SELECT * FROM users;  -- 1 query
SELECT * FROM orders WHERE user_id = 1;  -- N queries
SELECT * FROM orders WHERE user_id = 2;
...
-- Total: 1 + N queries
```

Code change:
```typescript
const users = await this.userRepository.find({
  relations: ['orders']  // ← Added eager loading
});
```

AFTER:
```sql
SELECT users.*, orders.*
FROM users
LEFT JOIN orders ON orders.user_id = users.id;
-- Total: 1 query
```

Test verification:
```bash
$ npm test -- users.service.spec.ts
✓ should load users with orders in single query (24 ms)
```

✅ N+1 problem confirmed fixed with evidence.
```

---

### Example 3: The "No Time" Rationalization

**Scenario**: New API endpoint without tests

**❌ Bad (Rationalization)**:
```
Agent: "I implemented the /api/products endpoint. No time to write tests right now, I'll add them later. The code is straightforward."
```

**✅ Good (Anti-Rationalization)**:
```
Agent: "⚠️ TDD enforcement: Cannot proceed without tests.

Let me follow RED-GREEN-REFACTOR:

RED (test fails):
```typescript
describe('ProductsController', () => {
  it('should create product', async () => {
    const dto = { name: 'Test Product', price: 100 };
    const result = await controller.create(dto);
    expect(result.data.name).toBe('Test Product');
  });
});
```
$ npm test
FAIL - Test fails (no implementation yet) ✅

GREEN (implement to pass):
```typescript
@Post()
async create(@Body() dto: CreateProductDto) {
  return this.productsService.create(dto);
}
```
$ npm test
PASS - Test passes ✅

REFACTOR (if needed):
[Check for improvements]

✅ Endpoint implemented with TDD.
```

---

## 🎯 Enforcement Matrix

| Workflow Stage | Rationalization Risk | Defense |
|----------------|---------------------|---------|
| **Planning** | "Skip planning, code is simple" | REQUIRE `writing-plans` for medium+ risk |
| **Implementation** | "Skip TDD, add tests later" | ENFORCE `test-driven-development` |
| **Verification** | "Should work, no need to test" | ENFORCE `verification-enforcement` |
| **Debugging** | "Quick fix without root cause" | ENFORCE `systematic-debugging` |
| **Review** | "Self-review is enough" | ENFORCE `two-stage-review` for high+ risk |
| **Finish** | "Good enough for now" | ENFORCE quality gates before merge |

---

## 📊 Rationalization Detection Metrics

Track how often rationalizations are detected and blocked:

```json
{
  "session": "abc123",
  "rationalizationsDetected": 3,
  "rationalizationsBlocked": 3,
  "gatesEnforced": ["TDD", "verification", "two-stage-review"],
  "complianceRate": "100%"
}
```

---

## 🧪 Self-Test: Am I Rationalizing?

Ask yourself before skipping a step:

1. **Would I accept this shortcut from a junior developer?**
   - If NO → Don't take the shortcut

2. **Would this pass code review?**
   - If NO → Don't skip the step

3. **Am I using minimizing language?** ("just", "simply", "trivial")
   - If YES → Red flag, proceed with caution

4. **Am I confident because I verified, or just because it seems right?**
   - If "seems right" → Verify it

5. **Would I do this if I knew it would be audited?**
   - If NO → Don't do it

---

## ✅ Summary

**The Rule**:
```
IF a phrase from the Rationalization Table is detected
THEN auto-trigger the appropriate defense mechanism
  AND enforce the skipped quality gate
  AND document the rationalization attempt
```

**Common Rationalizations to Block**:
1. ❌ "Just a..." → NO, all changes get appropriate gates
2. ❌ "I'm confident..." → NO, confidence ≠ evidence
3. ❌ "No time for..." → NO, quality gates are mandatory
4. ❌ "Too simple for..." → NO, simplicity doesn't bypass process
5. ❌ "Should work..." → NO, verify it actually works

**Remember**: The best rationalizations sound smart. That's why they're dangerous.

---

**Auto-injected in**: ALL sessions, ALL workflows
**Can be disabled**: NO (critical skill)
**Override allowed**: NO
