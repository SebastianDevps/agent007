# Ralph Loop Integration (v2.0)

This skill is **Ralph-ready** for iterative debugging.

## Completion Signal

When the bug is fixed in Ralph mode, output:

```
<promise>BUG_FIXED</promise>
```

## Completion Criteria

Before outputting completion promise, verify ALL of these:

- [ ] Phase 1 (Reproduce): Test that reproduces bug exists and FAILED initially
- [ ] Phase 2 (Root Cause): Root cause documented with 5 Whys
- [ ] Phase 3 (Hypothesis): Fix approach validated
- [ ] Phase 4 (Implementation): Fix implemented
- [ ] Failing test now PASSES
- [ ] Full test suite still GREEN (no regression)
- [ ] Defense-in-depth added (at least 1 safeguard)

## Self-Correction in Ralph Mode

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

## Stall Prevention

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

## Example Ralph Debugging Flow

```
Iteration 1 (Reproduce):
  → Create test: GET /api/users should not N+1
  → Run test → FAIL (1001 queries detected)
  → Document: Reproduced

Iteration 2 (Root Cause):
  → Apply 5 Whys
  → Root cause: Missing `relations: ['orders']` in find()
  → Document: Root cause found

Iteration 3 (Hypothesis):
  → Hypothesis: Add eager loading
  → Validate: TypeORM docs confirm this fixes N+1
  → Document: Hypothesis validated

Iteration 4 (Implement):
  → Add `relations: ['orders']` to repository.find()
  → Run test → PASS (1 query now)
  → Run full suite → PASS (no regression)
  → Add regression test to prevent re-introduction
  → Output: <promise>BUG_FIXED</promise>
```

## Defense-in-Depth Requirements

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
  expect(queryLogger.count()).toBeLessThan(5); // Safeguard
});
```

## Workflow Auto-Enforcement

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

## Integration with TDD

```typescript
// Systematic debugging integrates with TDD naturally:

// Phase 1 (Reproduce) = TDD RED
test('bug reproduction', () => {
  expect(buggyFunction()).toBe(expected);  // FAILS
});

// Phase 4 (Implementation) = TDD GREEN
// Fix applied
test('bug reproduction', () => {
  expect(fixedFunction()).toBe(expected);  // PASSES
});

// Defense-in-depth = TDD REFACTOR
// Add safeguards, improve code quality
```

## Success Metrics

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
  "regressionRate": "0%"
}
```
