# Brainstorming — Examples and Best Practices

Reference material for `skills/pipeline/brainstorming.md`.

---

## Example: Email Verification Feature

```
User: "Add email verification to user registration"

Q1: Verification Flow
When should verification happen?
  A) Immediately after registration (block access until verified)
  B) After registration (allow limited access)
Which approach?
→ User: "B - allow limited access"

Q2: Token Expiration
How long should the verification token be valid?
  A) 24 hours  B) 7 days  C) No expiration
→ User: "A - 24 hours"

Q3: Resend Strategy
What happens if token expires?
  A) User must re-register
  B) User can request new token
  C) Auto-send new token before expiration
→ User: "B - request new token"

Q4: Limited Access
What features should unverified users have?
  A) Read-only  B) Can create but not publish  C) No access
→ User: "A - read-only"

Q5: Edge Case — Multiple Verifications
What if user clicks verification link multiple times?
  A) All clicks work (idempotent)
  B) Only first click works
  C) Show "already verified" message
→ User: "A - idempotent"

Design Validation:
- User registers → receives email with 24h token
- Can access app read-only while unverified
- Can request new token if expired
- Verification link is idempotent
Correct? → User: "Yes"

✅ Brainstorming complete → Transitioning to Skill('plan')...
```

---

## Red Flags — Premature Implementation

### Red Flag #1: "Obviously" Assumptions
```diff
- ❌ User: "Add payment integration"
     Agent: "Obviously we'll use Stripe with webhooks..."

+ ✅ User: "Add payment integration"
     Agent: "Q1: Which payment provider do you prefer?"
```
"Obvious" to agent ≠ what user wants.

### Red Flag #2: Skipping Edge Cases
```diff
- ❌ Agent: "I understand the happy path, let's start coding"

+ ✅ Agent: "I understand the happy path. Edge case:
     Q: What happens when external API is down?"
```
Edge cases discovered during coding are 10× more expensive.

### Red Flag #3: Single Option Presented
```diff
- ❌ Agent: "I'll implement this using approach X"

+ ✅ Agent: "Option X (pros/cons) or Y (pros/cons). Which fits better?"
```
User may not know alternatives exist.

### Red Flag #4: No Validation
```diff
- ❌ Agent: "OK, starting implementation..."

+ ✅ Agent: "Let me confirm: [summary]. Is this correct?"
```
Misunderstandings discovered mid-implementation waste time.

---

## Best Practices

### Do ✅
1. **One question at a time** — let user think
2. **Present options with trade-offs** — inform decisions
3. **Explore edge cases early** — cheaper than finding in prod
4. **Validate understanding** — confirm before proceeding
5. **Document decisions with rationale** — future-you will thank you

### Don't ❌
1. **Don't assume** — ask, don't guess
2. **Don't overwhelm** — 20 questions at once loses the user
3. **Don't skip validation** — always confirm understanding
4. **Don't rush** — 30 min brainstorming saves hours of rework
5. **Don't ignore constraints** — they'll bite you later
