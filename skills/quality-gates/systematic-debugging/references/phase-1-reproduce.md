# Phase 1: Reproduce

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
    expect(queryLogger.count()).toBe(1);  // FAILS with 11 queries
  });
});
```

**Verification**:
```bash
$ npm test -- users.controller.spec.ts
FAIL - Test reproduces bug (this is expected, we WANT it to fail)
```

**Success Criteria Phase 1**:
- [ ] Test created that demonstrates bug
- [ ] Test fails consistently (not flaky)
- [ ] Test is minimal (no unnecessary complexity)
- [ ] Failure message is clear

**CHECKPOINT**: Cannot proceed to Phase 2 without reproducible test.
