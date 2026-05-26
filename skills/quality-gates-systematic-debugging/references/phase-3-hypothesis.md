# Phase 3: Hypothesis & Testing

**Objetivo**: Proponer solución y VALIDAR que realmente arregla el root cause.

## Process

### 1. Form Hypothesis

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

### 2. Validate Hypothesis (Without Implementing)

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
Confirmed: relations option does eager loading
Confirmed: Uses JOIN, not separate queries
```

**Check 3: Similar Code in Project**
```typescript
// Other places using eager loading successfully
const products = await this.productRepository.find({
  relations: ['reviews']  // Works fine
});
```

### 3. Alternative Hypotheses (Consider)

```markdown
## Alternative Solutions Considered

**Alternative 1**: Use QueryBuilder
```typescript
return this.userRepository
  .createQueryBuilder('user')
  .leftJoinAndSelect('user.orders', 'orders')
  .getMany();
```
Pro: More explicit control
Con: More verbose
Decision: Use relations option (simpler, same result)

**Alternative 2**: Lazy loading
```typescript
@OneToMany(() => Order, order => order.user, { lazy: true })
orders: Promise<Order[]>;
```
Con: Still N queries, just async
Decision: Rejected

**Alternative 3**: DataLoader pattern
Pro: Batches queries
Con: Adds complexity, overkill for this
Decision: Rejected for now, consider if performance still issues
```

**Success Criteria Phase 3**:
- [ ] Hypothesis formed with expected outcome
- [ ] Hypothesis validated against documentation
- [ ] Alternative solutions considered
- [ ] Chosen solution justified

**CHECKPOINT**: Cannot proceed to Phase 4 without validated hypothesis.
