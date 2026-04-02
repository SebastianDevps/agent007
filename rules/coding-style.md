# Coding Style Rules

## Exports

- Named exports only — never `export default`
- This enables consistent auto-import and prevents aliasing confusion

```typescript
// ✅ Correct
export function createUser() {}
export class UserService {}

// ❌ Wrong
export default function createUser() {}
```

## Return Types

- Explicit return types on all public functions and methods
- `async` functions: explicit `Promise<T>` return type
- Private helper functions: inferred types are acceptable

```typescript
// ✅ Correct
export async function findUser(id: string): Promise<User | null> {}
export function validate(dto: CreateUserDto): ValidationResult {}

// ❌ Wrong
export async function findUser(id: string) {} // inferred on public API
```

## No Magic Numbers

- Every numeric literal with business meaning must be a named constant
- Exceptions: 0, 1, -1, and HTTP status codes in response construction

```typescript
// ✅ Correct
const MAX_LOGIN_ATTEMPTS = 5;
const SESSION_TTL_SECONDS = 15 * 60;

// ❌ Wrong
if (attempts > 5) lockAccount();
setTTL(900);
```

## File Length

- Max 200 lines per file — split at logical boundaries if exceeded
- A file over 200 lines is a signal that it has more than one responsibility
- Exception: generated files, migration files, test data fixtures

## Function Length

- Max 20 lines per function body — extract helpers if exceeded
- Count only logic lines (not blank lines, not opening/closing braces)
- A function over 20 lines usually has multiple responsibilities

## Naming

- Descriptive names that explain intent: `getUserByEmail` not `getUser`
- Boolean variables/functions: `is`, `has`, `can`, `should` prefix
- No single-letter variables except in trivial `map/filter` callbacks (`x`, `i`)
- No abbreviations in public names: `repository` not `repo`, `configuration` not `config`
- Exception: widely-understood acronyms: `dto`, `id`, `url`, `api`, `http`

```typescript
// ✅ Correct
const isEmailVerified = user.verifiedAt !== null;
async function findActiveUserByEmail(email: string): Promise<User | null> {}

// ❌ Wrong
const ver = user.verifiedAt !== null;
async function getUser(e: string) {}
```

## Comments

- Descriptive names > comments: rename the function instead of adding a comment
- Add a comment only when the *why* is not obvious from the code
- Never comment what the code does — comment why it does it that way
- Remove commented-out code before committing (use git history instead)

```typescript
// ✅ Correct — explains why, not what
// Rate limiting is applied at the service layer, not the controller,
// because we need to count across multiple endpoints for the same operation.
await this.rateLimiter.check(userId, 'password-reset');

// ❌ Wrong — explains what (obvious from the code)
// Check the rate limit
await this.rateLimiter.check(userId, 'password-reset');
```
