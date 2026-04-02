# Brainstorming — Domain-Specific Question Templates

Reference material for `skills/pipeline/brainstorming.md`.
Use these templates during Fase 2 (edge cases) and Fase 3 (alternatives).

---

## Feature: Authentication

```markdown
**Core Questions:**
1. What authentication method? (JWT, session, OAuth)
2. Where to store tokens? (localStorage, httpOnly cookie, Redis)
3. Token expiration strategy? (fixed, sliding window, refresh tokens)
4. What happens on token expiration? (auto-logout, refresh, prompt)
5. Role-based access control needed? (yes/no, how many roles)
6. Multi-factor authentication? (yes/no, which factors)

**Edge Cases:**
- Concurrent logins from multiple devices?
- Token revocation strategy?
- Password reset flow?
- Account lockout after failed attempts?
```

---

## Feature: Payment Integration

```markdown
**Core Questions:**
1. Which payment provider? (Stripe, PayPal, etc.)
2. Payment types? (one-time, subscription, both)
3. Currency support? (single, multi-currency)
4. Refund policy? (full, partial, time-limited)
5. Webhook handling? (async processing, retries)
6. Test vs production environments?

**Edge Cases:**
- Partial payments?
- Failed payment handling?
- Subscription cancellation?
- Duplicate payment prevention?
- Webhook replay attacks?
```

---

## Feature: File Upload

```markdown
**Core Questions:**
1. File types allowed? (images, PDFs, all types)
2. Size limits? (per file, total)
3. Storage? (local, S3, CDN)
4. Processing needed? (thumbnails, compression, virus scan)
5. Access control? (public, private, signed URLs)
6. Retention policy? (keep forever, auto-delete after X days)

**Edge Cases:**
- Concurrent uploads?
- Upload progress tracking?
- Resume failed uploads?
- Malicious file detection?
- Storage quota enforcement?
```

---

## Refactor: Bounded Context Separation

```markdown
**Core Questions:**
1. Which modules belong to this context?
2. What are the context boundaries?
3. How should contexts communicate? (events, API calls, shared DB)
4. What data is shared vs isolated?
5. Migration strategy? (big bang, incremental)
6. Rollback plan if issues arise?

**Edge Cases:**
- Circular dependencies between contexts?
- Transaction boundaries across contexts?
- Event ordering guarantees?
- Eventual consistency acceptable?
```

---

## Design Document Output Template

After all 5 phases complete, produce this document:

```markdown
# Feature Design: [Feature Name]

**Date**: YYYY-MM-DD

## Problem Statement
[What problem this solves]

## Requirements

### Functional Requirements
1. Requirement 1
2. Requirement 2

### Non-Functional Requirements
- Performance: [targets]
- Security: [requirements]
- Scalability: [expectations]

## Design Decisions

### Decision 1: [Name]
**Chosen**: Option B
**Rationale**: [Why]
**Trade-offs**: [What we're accepting]

## Edge Cases & Handling

| Edge Case | Handling Strategy |
|-----------|-------------------|
| Case 1 | Strategy 1 |

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies & Impact

### Affected Modules
- Module A (changes needed)

### External Dependencies
- Dependency A (version X)

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Risk 1 | Medium | High | Mitigation 1 |

**Next Step**: Skill('plan')
```
