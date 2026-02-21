---
name: writing-plans
description: "Decompose features into executable tasks of 2-5 minutes each with exact file paths, complete code, and verification commands. Use after brainstorming or for complex implementations."
invokable: true
accepts_args: brainstormingOutput
auto-activate: feature-development (all), bug-fixing (medium+), refactor (medium+)
required-sub-skill: executing-plans
version: 2.0.0
when:
  - previous_skill: brainstorming
    status: completed
  - task_type: [feature, bug, refactor]
    risk_level: [medium, high, critical]
  - user_mentions: ["create plan", "break down", "tasks"]
---

# Writing Plans - Task Decomposition for Execution

**Propósito**: Descomponer features/bugs/refactors en tareas ejecutables de **2-5 minutos cada una**, con:
- Rutas exactas de archivos
- Código completo (no pseudocódigo)
- Comandos de verificación
- Orden de ejecución claro

**Cuándo se activa**:
- Después de brainstorming (feature development)
- Para bugs medium+ risk (after systematic debugging)
- Para refactors medium+ risk

---

## 🎯 Por Qué Planes Detallados

### El Anti-Pattern: Planes Vagos

```diff
❌ MAL:
Task 1: "Implement authentication"
Task 2: "Add tests"
Task 3: "Deploy"

✅ BIEN:
Task 1: Create User entity with password field (2 min)
  File: src/users/entities/user.entity.ts
  Code: [complete code]
  Verify: npm run build

Task 2: Create CreateUserDto with validation (3 min)
  File: src/users/dto/create-user.dto.ts
  Code: [complete code]
  Verify: npm test -- create-user.dto.spec.ts

Task 3: Implement UsersService.create() (4 min)
  File: src/users/users.service.ts
  Code: [complete code]
  Verify: npm test -- users.service.spec.ts

[12 more tasks, each 2-5 min...]
```

**Por qué es importante**:
- Tareas de 2-5 min son ejecutables sin decisiones adicionales
- Código completo significa no hay ambigüedad
- Verification commands aseguran que cada paso funciona antes de siguiente

---

## 📏 Tamaño de Tarea Ideal: 2-5 Minutos

### Demasiado Grande (> 5 min)

```diff
- ❌ Task: "Implement JWT authentication system (60 min)"
```

**Problema**: Requiere múltiples decisiones durante ejecución.

**Solución**: Descomponer en 15+ tareas de 2-5 min cada una.

---

### Demasiado Pequeña (< 2 min)

```diff
- ❌ Task 1: "Import NestJS decorators (30 sec)"
- ❌ Task 2: "Add @Injectable decorator (30 sec)"
- ❌ Task 3: "Create constructor (30 sec)"
```

**Problema**: Overhead de switching entre tareas.

**Solución**: Combinar en tarea de 2-3 min.

---

### Tamaño Perfecto (2-5 min)

```diff
+ ✅ Task: "Create AuthService with login method (4 min)"
    - Create file
    - Add dependencies
    - Implement login logic
    - Add basic error handling
    - Verify compilation
```

**Por qué funciona**: Suficiente trabajo para ser meaningful, no tanto que requiera decisiones adicionales.

---

## 📋 Plan Template

### Estructura de Plan

```markdown
# Implementation Plan: [Feature/Bug/Refactor Name]

**Date**: 2026-02-06
**Risk Level**: [low/medium/high/critical]
**Estimated Duration**: [X hours]
**Total Tasks**: [N tasks]

---

## Overview

**Goal**: [What we're building/fixing/refactoring]

**Success Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Design Decisions** (from brainstorming):
- Decision 1: [summary]
- Decision 2: [summary]

---

## Task Breakdown

### Phase 1: [Phase Name] (Tasks 1-5, ~20 min)

**Task 1: [Task Name]** (2 min)
**File**: `src/path/to/file.ts`
**Action**: [What to do]

**Code**:
```typescript
[Complete code, not pseudocode]
```

**Verification**:
```bash
$ npm run build
# Expected: ✅ Compilation successful

$ npm run lint
# Expected: ✅ No linting errors
```

**Dependencies**: None
**Blocks**: Task 2

---

**Task 2: [Task Name]** (3 min)
**File**: `src/path/to/another-file.ts`
**Action**: [What to do]

**Code**:
```typescript
[Complete code]
```

**Verification**:
```bash
$ npm test -- file.spec.ts
# Expected: ✅ Tests pass (1/1)
```

**Dependencies**: Task 1
**Blocks**: Task 3, Task 4

---

[Continue for all tasks...]

---

## Verification Checklist

After completing all tasks:

- [ ] All tests pass (`npm test`)
- [ ] Coverage > 70% for new code (`npm run test:cov`)
- [ ] No linting errors (`npm run lint`)
- [ ] Application starts (`npm run start:dev`)
- [ ] Feature manually tested (happy path + 2 edge cases)
- [ ] No OWASP issues (`npm run lint:security`)

---

## Rollback Plan

If issues arise:

1. **Stop at current task** (don't proceed)
2. **Revert changes**: `git reset --hard HEAD~N` (N = number of commits)
3. **Document issue**: What went wrong, why
4. **Re-plan**: Adjust plan based on learnings

---

## Post-Implementation

- [ ] Update documentation
- [ ] Update CHANGELOG
- [ ] Create PR with description
- [ ] Request code review
```

---

## 🔨 Task Decomposition Strategies

### Strategy 1: By File/Module

```markdown
Feature: Add email verification

Phase 1: Entity Changes
- Task 1: Add emailVerified field to User entity
- Task 2: Add verificationToken field to User entity
- Task 3: Create migration for new fields

Phase 2: DTOs
- Task 4: Update CreateUserDto
- Task 5: Create VerifyEmailDto

Phase 3: Service Logic
- Task 6: Implement sendVerificationEmail()
- Task 7: Implement verifyEmail()
- Task 8: Update findByEmail() to check verified status

Phase 4: Controller
- Task 9: Add POST /auth/verify endpoint
- Task 10: Add POST /auth/resend-verification endpoint

Phase 5: Tests
- Task 11: Unit tests for sendVerificationEmail()
- Task 12: Unit tests for verifyEmail()
- Task 13: E2E tests for verification flow
```

---

### Strategy 2: By TDD Cycle

```markdown
Bug Fix: Fix N+1 query in /api/users

Phase 1: RED (Write failing test)
- Task 1: Create test that demonstrates N+1
- Task 2: Run test, confirm it fails

Phase 2: GREEN (Make test pass)
- Task 3: Add eager loading to find() call
- Task 4: Run test, confirm it passes

Phase 3: REFACTOR (Improve code)
- Task 5: Extract query to repository method
- Task 6: Add JSDoc documentation
- Task 7: Run tests, confirm still pass

Phase 4: VERIFICATION
- Task 8: Check query logs (should be 1 query not N)
- Task 9: Run all tests
- Task 10: Performance benchmark (before vs after)
```

---

### Strategy 3: By Dependency Chain

```markdown
Refactor: Introduce Repository Pattern

Phase 1: Foundation
- Task 1: Create IUserRepository interface
- Task 2: Create UserRepository implementation
- Task 3: Register repository in module

Phase 2: Migrate Service (depends on Phase 1)
- Task 4: Inject IUserRepository into UserService
- Task 5: Replace direct typeorm calls with repository methods
- Task 6: Run tests (should pass without changes)

Phase 3: Cleanup (depends on Phase 2)
- Task 7: Remove direct TypeORM imports from service
- Task 8: Update tests to mock repository
- Task 9: Verify all tests pass
```

---

## 🧩 Task Template

### Complete Task Format

```markdown
**Task X: [Clear, Actionable Name]** (Y min)

**File**: `src/exact/path/to/file.ts` (or "New file")

**Action**: [Concise description of what to do]

**Dependencies**: Task A, Task B (must be done first)

**Code**:
```typescript
// Complete, runnable code
// Not pseudocode or "TODO: implement this"

import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { User } from './entities/user.entity';
import { CreateUserDto } from './dto/create-user.dto';

@Injectable()
export class UsersService {
  constructor(
    @InjectRepository(User)
    private readonly userRepository: Repository<User>,
  ) {}

  async create(createUserDto: CreateUserDto): Promise<User> {
    const user = this.userRepository.create(createUserDto);
    return this.userRepository.save(user);
  }

  async findAll(): Promise<User[]> {
    return this.userRepository.find();
  }
}
```

**Verification**:
```bash
# Step 1: Check compilation
$ npm run build
Expected: ✅ Build successful

# Step 2: Run tests
$ npm test -- users.service.spec.ts
Expected: ✅ Tests: 2 passed, 2 total

# Step 3: Check lint
$ npm run lint
Expected: ✅ No linting errors
```

**Success Criteria**:
- [ ] File created/modified
- [ ] Code compiles
- [ ] Tests pass
- [ ] No linting errors

**Estimated Time**: Y minutes

**Blocks**: Task Z (cannot start until this completes)
```

---

## 🎓 Examples

### Example 1: JWT Authentication Feature

```markdown
# Implementation Plan: JWT Authentication

**Risk Level**: Critical
**Estimated Duration**: 3-4 hours
**Total Tasks**: 18 tasks

---

## Overview

**Goal**: Implement JWT-based authentication with access and refresh tokens

**Success Criteria**:
- [ ] Users can login with email/password
- [ ] JWT access token issued (15 min expiry)
- [ ] JWT refresh token issued (7 days expiry)
- [ ] Protected routes require valid access token
- [ ] Refresh token rotation implemented
- [ ] Security audit passed (OWASP)

---

## Task Breakdown

### Phase 1: Dependencies & Configuration (Tasks 1-3, ~10 min)

**Task 1: Install JWT dependencies** (2 min)

**File**: `package.json`

**Action**: Install @nestjs/jwt and @nestjs/passport

**Code**:
```bash
npm install @nestjs/jwt @nestjs/passport passport passport-jwt
npm install -D @types/passport-jwt
```

**Verification**:
```bash
$ npm list @nestjs/jwt
# Expected: @nestjs/jwt@X.X.X
```

---

**Task 2: Create JWT configuration** (3 min)

**File**: `src/config/jwt.config.ts` (New file)

**Action**: Create JWT config with secret and expiry

**Code**:
```typescript
import { registerAs } from '@nestjs/config';

export default registerAs('jwt', () => ({
  accessSecret: process.env.JWT_ACCESS_SECRET || 'change-me-in-production',
  refreshSecret: process.env.JWT_REFRESH_SECRET || 'change-me-in-production',
  accessExpiresIn: '15m',
  refreshExpiresIn: '7d',
}));
```

**Verification**:
```bash
$ npm run build
# Expected: ✅ Compilation successful
```

---

**Task 3: Update .env.example** (2 min)

**File**: `.env.example`

**Action**: Add JWT secret placeholders

**Code**:
```env
# JWT Configuration
JWT_ACCESS_SECRET=your-access-secret-here
JWT_REFRESH_SECRET=your-refresh-secret-here
```

**Verification**:
```bash
$ git diff .env.example
# Expected: Shows new JWT variables
```

---

### Phase 2: Entities & DTOs (Tasks 4-7, ~15 min)

**Task 4: Add password field to User entity** (3 min)

**File**: `src/users/entities/user.entity.ts`

**Action**: Add password field with @Exclude decorator

**Code**:
```typescript
import { Entity, Column, PrimaryGeneratedColumn } from 'typeorm';
import { Exclude } from 'class-transformer';

@Entity('users')
export class User {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column({ unique: true })
  email: string;

  @Column()
  @Exclude()  // Never expose in API responses
  password: string;

  @Column({ default: true })
  isActive: boolean;

  @Column({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}
```

**Verification**:
```bash
$ npm run build
# Expected: ✅ Compilation successful

$ npm test -- user.entity.spec.ts
# Expected: ✅ Entity tests pass
```

---

**Task 5: Create LoginDto** (3 min)

**File**: `src/auth/dto/login.dto.ts` (New file)

**Action**: Create DTO with email and password validation

**Code**:
```typescript
import { IsEmail, IsString, MinLength } from 'class-validator';

export class LoginDto {
  @IsEmail({}, { message: 'Invalid email format' })
  email: string;

  @IsString()
  @MinLength(8, { message: 'Password must be at least 8 characters' })
  password: string;
}
```

**Verification**:
```bash
$ npm run build
# Expected: ✅ Compilation successful

$ npm test -- login.dto.spec.ts
# Expected: ✅ Validation tests pass
```

---

[Continue with remaining 11 tasks...]

---

### Phase 3: Auth Service (Tasks 8-11, ~20 min)
### Phase 4: JWT Strategy (Tasks 12-13, ~10 min)
### Phase 5: Auth Controller (Tasks 14-15, ~15 min)
### Phase 6: Guards & Middleware (Tasks 16-17, ~20 min)
### Phase 7: Testing & Verification (Task 18, ~30 min)

---

## Verification Checklist

- [ ] All 18 tasks completed
- [ ] All tests pass (unit + integration)
- [ ] Coverage > 80%
- [ ] No OWASP issues
- [ ] Manual testing:
  - [ ] Can login with valid credentials
  - [ ] Cannot login with invalid credentials
  - [ ] Access token expires after 15 min
  - [ ] Can refresh token
  - [ ] Protected routes work
  - [ ] Invalid tokens rejected

---

## Rollback Plan

If critical issues found:
1. Stop at current task
2. `git reset --hard HEAD~N` (N = commits since start)
3. Document what went wrong
4. Revise plan with lessons learned
```

---

## ✅ Planning Checklist

Before considering plan complete:

- [ ] **Every task is 2-5 minutes** (not 1 min, not 30 min)
- [ ] **Complete code provided** (not pseudocode or "TODO")
- [ ] **Exact file paths** (not "create a service file")
- [ ] **Verification commands** (not "test it")
- [ ] **Dependencies clear** (task X requires task Y first)
- [ ] **Phases logical** (grouped by related functionality)
- [ ] **Success criteria defined** (know when "done")
- [ ] **Rollback plan exists** (know how to undo if needed)

---

## 🚫 Red Flags - Bad Plans

### 🚩 Red Flag #1: Vague Tasks

```diff
- ❌ "Task 1: Set up authentication"
+ ✅ "Task 1: Create AuthModule with JwtModule import (3 min)"
```

---

### 🚩 Red Flag #2: Missing Code

```diff
- ❌ "Task 2: Implement login method
      Code: // TODO: implement login logic"

+ ✅ "Task 2: Implement AuthService.login() (4 min)
      Code: [complete implementation with error handling]"
```

---

### 🚩 Red Flag #3: No Verification

```diff
- ❌ "Task 3: Create UserDto
      Verification: Test it"

+ ✅ "Task 3: Create CreateUserDto (3 min)
      Verification:
      $ npm test -- create-user.dto.spec.ts
      Expected: ✅ 4/4 tests pass"
```

---

### 🚩 Red Flag #4: Wrong Size

```diff
- ❌ "Task 1: Implement entire auth system (2 hours)"

+ ✅ [Break into 20+ tasks of 2-5 min each]
```

---

## 🔄 Integration with Workflow

### Automatic Transition

After plan is written and validated:

```typescript
if (planComplete && allTasksWellDefined) {
  // Enforce TDD if applicable
  if (riskLevel >= 'medium') {
    enforce('test-driven-development');
  }

  // Transition to execution
  transition_to('executing-plans', {
    plan: planDocument,
    totalTasks: taskCount,
    estimatedDuration: duration,
    verificationRequired: true
  });
}
```

---

## 📊 Plan Quality Metrics

Track plan quality:

```json
{
  "plan": "jwt-authentication",
  "totalTasks": 18,
  "avgTaskDuration": "3.2 min",
  "tasksWithCode": 18,
  "tasksWithVerification": 18,
  "qualityScore": "95/100",

  "qualityBreakdown": {
    "taskSizing": "100/100",      // All tasks 2-5 min
    "codeCompleteness": "100/100", // All have complete code
    "verification": "90/100",      // Most have verification
    "dependencies": "95/100"       // Dependencies mostly clear
  }
}
```

---

## 🎯 Summary

**Writing Plans Rule**:
```
FOR each feature/bug/refactor
  DECOMPOSE into tasks of 2-5 minutes each
  PROVIDE complete code (not pseudocode)
  SPECIFY exact file paths
  INCLUDE verification commands
  DEFINE dependencies between tasks
  DOCUMENT success criteria
  CREATE rollback plan
THEN transition to executing-plans
```

**Remember**: Good plans make execution mechanical. Bad plans require decisions during execution.

---

**Required Sub-Skill**: executing-plans (auto-invoked after completion)
**Auto-Activated In**: feature-development (all), bug-fixing (medium+), refactor (medium+)
