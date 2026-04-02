# Code Patterns Rules

## Dependency Injection Over Static Imports

- Inject dependencies through constructor, not `import X from` at module level
- This enables testability (swap implementations without file-level mocking)
- NestJS: always use `@Injectable()` + constructor injection

```typescript
// ✅ Correct
constructor(private readonly userRepo: UserRepository) {}

// ❌ Wrong
import { userRepo } from './user.repository'; // static import = untestable
```

## Repository Pattern for Data Access

- All database access must go through a Repository class
- Controllers and services must never use TypeORM EntityManager directly
- Repository is the only place that knows about the ORM

```typescript
// ✅ Correct — service calls repository
class UserService {
  constructor(private readonly users: UserRepository) {}
  async find(id: string) { return this.users.findById(id); }
}

// ❌ Wrong — service knows about ORM
class UserService {
  constructor(@InjectEntityManager() private em: EntityManager) {}
}
```

## DTOs for API Boundaries

- Every API input must have a DTO with `class-validator` decorators
- Every API output must have a response DTO (never expose raw entity)
- DTOs live at the controller boundary — services work with domain objects

```typescript
// ✅ Correct
class CreateUserDto {
  @IsEmail() email: string;
  @MinLength(8) password: string;
}
```

## Guard Clauses Over Nested if/else

- Return or throw early instead of nesting conditions
- Max 2 levels of nesting before extracting a function

```typescript
// ✅ Correct — guard clauses
function process(user: User | null) {
  if (!user) throw new NotFoundException();
  if (!user.isActive) throw new ForbiddenException();
  return doWork(user);
}

// ❌ Wrong — nested
function process(user: User | null) {
  if (user) {
    if (user.isActive) {
      return doWork(user);
    }
  }
}
```

## Composition Over Inheritance

- Prefer composed behavior (inject a service) over class hierarchies
- Extend only for true "is-a" relationships (rare in application code)
- Use interfaces to define contracts, not abstract base classes with logic

## Error Boundaries at Module Edges

- Each module catches its own domain errors and translates to HTTP errors at the controller
- Errors from downstream modules must be wrapped with context
- Never let internal stack traces reach the API response

```typescript
// ✅ Correct — controller translates domain error
try {
  return await this.service.create(dto);
} catch (e) {
  if (e instanceof DuplicateEmailError) throw new ConflictException(e.message);
  throw e;
}
```

## Event-Driven for Cross-Module Communication

- Modules communicate across bounded contexts via events, not direct service injection
- Direct injection between unrelated modules creates circular dependency risk
- Use NestJS EventEmitter or a domain event bus for cross-module side effects

```typescript
// ✅ Correct — module A emits, module B listens
this.events.emit('user.created', { userId: user.id });

// ❌ Wrong — module A injects module B's service
constructor(private readonly notificationService: NotificationService) {}
```
