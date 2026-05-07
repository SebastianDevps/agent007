# Examples by Bug Type

## Example 1: Performance Bug (N+1 Query)

- **Phase 1**: Create test showing 1001 queries
- **Phase 2**: Root cause = missing eager loading
- **Phase 3**: Hypothesis = add relations option
- **Phase 4**: Implement + add query count assertions

## Example 2: Security Bug (SQL Injection)

- **Phase 1**: Create test with malicious input
- **Phase 2**: Root cause = string concatenation in query
- **Phase 3**: Hypothesis = use parameterized queries
- **Phase 4**: Implement + add security tests + OWASP check

## Example 3: Logic Bug (Incorrect Calculation)

- **Phase 1**: Create test with known inputs/outputs
- **Phase 2**: Root cause = off-by-one error in loop
- **Phase 3**: Hypothesis = fix loop bounds
- **Phase 4**: Implement + add edge case tests + documentation

## Example 4: Race Condition

- **Phase 1**: Create test that triggers concurrent requests
- **Phase 2**: Root cause = missing transaction isolation
- **Phase 3**: Hypothesis = use database transactions
- **Phase 4**: Implement + add concurrency tests + defense-in-depth
