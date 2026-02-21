---
name: tdd
description: "Test-Driven Development workflow. RED (write failing test) → GREEN (make it pass) → REFACTOR (improve code). Enforces test-first approach."
invokable: true
accepts_args: true
auto-activate: feature (all), bug-fix (all)
version: 1.0.0
when:
  - user mentions "test"
  - user mentions "TDD"
  - feature development starts
  - bug fix starts
---

# TDD - Test-Driven Development Workflow

**Propósito**: Implementar features y fixes usando la metodología RED-GREEN-REFACTOR para garantizar código testeado desde el inicio.

**Cuándo se activa**:
- Feature development (cualquier nivel de riesgo)
- Bug fixing (para garantizar test de regresión)
- Cuando usuario menciona "test" o "TDD"
- Refactors (para garantizar no-regression)

---

## 🎯 El Ciclo TDD

```
RED → GREEN → REFACTOR → repeat
```

### 🔴 RED: Write a Failing Test

**Objetivo**: Escribir un test que falla porque la funcionalidad aún no existe.

**Proceso**:
1. Entender el requirement/bug
2. Escribir test que describe el comportamiento esperado
3. Ejecutar test → DEBE FALLAR
4. Si NO falla, el test está mal escrito o la feature ya existe

**Ejemplo - Feature: Login endpoint**:
```typescript
// users.controller.spec.ts
describe('POST /auth/login', () => {
  it('should return JWT token for valid credentials', async () => {
    const loginDto = { email: 'test@example.com', password: 'password123' };

    const response = await request(app.getHttpServer())
      .post('/auth/login')
      .send(loginDto)
      .expect(200);

    expect(response.body).toHaveProperty('access_token');
    expect(response.body.access_token).toBeDefined();
  });
});
```

**Ejecutar**:
```bash
npm run test:e2e -- users.controller.spec.ts
# EXPECTED: ❌ FAIL - endpoint doesn't exist yet
```

**Regla de Oro**:
```diff
❌ NO escribir código de implementación antes del test
✅ Test primero → FALLA → ENTONCES código
```

---

### 🟢 GREEN: Make the Test Pass

**Objetivo**: Escribir el código MÍNIMO necesario para hacer pasar el test.

**Proceso**:
1. Implementar solo lo necesario para pasar el test
2. No agregar funcionalidad "extra" que no esté en el test
3. Ejecutar test → DEBE PASAR
4. Si no pasa, debuggear hasta que pase

**Ejemplo - Implementación mínima**:
```typescript
// auth.controller.ts
@Controller('auth')
export class AuthController {
  constructor(private authService: AuthService) {}

  @Post('login')
  async login(@Body() loginDto: LoginDto) {
    return this.authService.login(loginDto);
  }
}

// auth.service.ts
export class AuthService {
  async login(loginDto: LoginDto) {
    // Implementación MÍNIMA
    const user = await this.validateUser(loginDto);
    return {
      access_token: this.generateToken(user),
    };
  }
}
```

**Ejecutar**:
```bash
npm run test:e2e -- users.controller.spec.ts
# EXPECTED: ✅ PASS
```

**Regla de Oro**:
```diff
❌ NO sobre-ingeniar en esta fase
✅ Código más simple que hace pasar el test
```

---

### 🔵 REFACTOR: Improve the Code

**Objetivo**: Mejorar el código SIN cambiar su comportamiento (test sigue pasando).

**Proceso**:
1. Identificar code smells: duplicación, nombres confusos, complejidad
2. Refactorizar código
3. Ejecutar test → DEBE SEGUIR PASANDO
4. Si falla, revertir o debuggear

**Ejemplo - Refactor**:
```typescript
// ANTES (código funcional pero mejorable)
async login(loginDto: LoginDto) {
  const user = await this.userRepository.findOne({
    where: { email: loginDto.email }
  });

  if (!user) throw new UnauthorizedException();

  const isValid = await bcrypt.compare(loginDto.password, user.password);
  if (!isValid) throw new UnauthorizedException();

  const payload = { sub: user.id, email: user.email };
  return {
    access_token: this.jwtService.sign(payload),
  };
}

// DESPUÉS (refactored - más legible)
async login(loginDto: LoginDto) {
  const user = await this.validateUser(loginDto);
  const token = await this.generateToken(user);
  return { access_token: token };
}

private async validateUser(loginDto: LoginDto): Promise<User> {
  const user = await this.findUserByEmail(loginDto.email);
  await this.verifyPassword(loginDto.password, user.password);
  return user;
}

private async generateToken(user: User): Promise<string> {
  const payload = { sub: user.id, email: user.email };
  return this.jwtService.sign(payload);
}
```

**Ejecutar**:
```bash
npm run test:e2e -- users.controller.spec.ts
# EXPECTED: ✅ PASS (comportamiento idéntico)
```

**Regla de Oro**:
```diff
❌ NO cambiar comportamiento durante refactor
✅ Mejorar estructura manteniendo tests green
```

---

## 🔄 TDD Workflow Completo

### Fase 1: Preparación (PRE-RED)

```markdown
1. **Entender requirement**
   - Leer user story/bug report
   - Identificar casos de uso
   - Definir acceptance criteria

2. **Decidir tipo de test**
   - Unit test (service logic, utils)
   - Integration test (controller + service)
   - E2E test (full request/response)

3. **Crear archivo de test** (si no existe)
   - `feature.service.spec.ts` (unit)
   - `feature.controller.spec.ts` (integration)
   - `feature.e2e-spec.ts` (e2e)
```

---

### Fase 2: RED - Write Failing Test

```markdown
1. **Escribir test case**
   - Describe comportamiento esperado
   - Setup: preparar datos/mocks
   - Execute: llamar función/endpoint
   - Assert: verificar resultado

2. **Ejecutar test**
   ```bash
   npm run test:unit -- feature.service.spec.ts
   ```

3. **Verificar que FALLA**
   - ❌ Si pasa → Test está mal o feature ya existe
   - ✅ Si falla → Continuar a GREEN

4. **Leer error message**
   - Entender QUÉ falta implementar
```

**Checklist RED**:
- [ ] Test escrito con descripción clara
- [ ] Test ejecutado: FALLA como esperado
- [ ] Error message es claro (no confuso)
- [ ] Committed test (git add test file)

---

### Fase 3: GREEN - Make Test Pass

```markdown
1. **Implementar código mínimo**
   - Crear clase/función/endpoint
   - Implementar lógica básica
   - NO agregar features extra

2. **Ejecutar test**
   ```bash
   npm run test:unit -- feature.service.spec.ts
   ```

3. **Verificar que PASA**
   - ✅ Si pasa → Continuar a REFACTOR
   - ❌ Si falla → Debuggear implementación

4. **Commit código**
   ```bash
   git add src/feature.service.ts
   git commit -m "feat: implement feature (GREEN phase)"
   ```
```

**Checklist GREEN**:
- [ ] Código implementado
- [ ] Test ejecutado: PASA
- [ ] NO hay código "extra" no testeado
- [ ] Committed implementación

---

### Fase 4: REFACTOR - Improve Code

```markdown
1. **Identificar mejoras**
   - Duplicación de código
   - Nombres confusos
   - Lógica compleja
   - Violaciones de principios (SOLID)

2. **Refactorizar**
   - Extraer métodos privados
   - Mejorar nombres
   - Simplificar condicionales
   - Aplicar design patterns si ayuda

3. **Ejecutar test**
   ```bash
   npm run test:unit -- feature.service.spec.ts
   ```

4. **Verificar que SIGUE PASANDO**
   - ✅ Si pasa → Refactor exitoso
   - ❌ Si falla → Revertir o debuggear

5. **Commit refactor**
   ```bash
   git commit -m "refactor: improve code readability"
   ```
```

**Checklist REFACTOR**:
- [ ] Código mejorado (legibilidad, estructura)
- [ ] Test ejecutado: SIGUE PASANDO
- [ ] NO cambió comportamiento
- [ ] Committed refactor

---

### Fase 5: REPEAT

```markdown
1. **Siguiente requirement**
   - Elegir siguiente caso de uso
   - Volver a fase RED

2. **Nuevo test case**
   - Mismo archivo de test
   - Nueva funcionalidad/edge case

**Ejemplo progresivo**:
- Test 1: Login con credenciales válidas ✅
- Test 2: Login con password inválido ✅
- Test 3: Login con email no existente ✅
- Test 4: Login con cuenta bloqueada ✅
```

---

## 🧪 Tipos de Tests en TDD

### 1. Unit Tests (Aislado)

**Cuándo**: Lógica de servicios, utils, helpers

```typescript
// feature.service.spec.ts
describe('FeatureService', () => {
  let service: FeatureService;
  let mockRepository: MockType<Repository<Entity>>;

  beforeEach(() => {
    mockRepository = {
      find: jest.fn(),
      save: jest.fn(),
      // ...
    };
    service = new FeatureService(mockRepository);
  });

  it('should calculate total correctly', () => {
    const result = service.calculateTotal([1, 2, 3]);
    expect(result).toBe(6);
  });
});
```

---

### 2. Integration Tests (Controller + Service)

**Cuándo**: Endpoints, integración entre capas

```typescript
// feature.controller.spec.ts
describe('FeatureController', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const module = await Test.createTestingModule({
      imports: [FeatureModule],
    }).compile();

    app = module.createNestApplication();
    await app.init();
  });

  it('GET /features should return array', async () => {
    const response = await request(app.getHttpServer())
      .get('/features')
      .expect(200);

    expect(Array.isArray(response.body)).toBe(true);
  });
});
```

---

### 3. E2E Tests (Full Flow)

**Cuándo**: Flujos completos, autenticación, transacciones

```typescript
// feature.e2e-spec.ts
describe('Feature Flow (e2e)', () => {
  it('should complete full user registration flow', async () => {
    // 1. Register user
    const registerResponse = await request(app)
      .post('/auth/register')
      .send({ email: 'test@example.com', password: 'pass123' });

    expect(registerResponse.status).toBe(201);

    // 2. Login
    const loginResponse = await request(app)
      .post('/auth/login')
      .send({ email: 'test@example.com', password: 'pass123' });

    const token = loginResponse.body.access_token;

    // 3. Access protected route
    const profileResponse = await request(app)
      .get('/profile')
      .set('Authorization', `Bearer ${token}`);

    expect(profileResponse.status).toBe(200);
  });
});
```

---

## 🚫 Anti-Patterns en TDD

### ❌ Anti-Pattern #1: Escribir código antes del test

```diff
- ❌ MAL:
  1. Implementar AuthService.login()
  2. Después escribir test

+ ✅ BIEN:
  1. Escribir test que llama AuthService.login() (FALLA)
  2. Implementar AuthService.login() (PASA)
```

---

### ❌ Anti-Pattern #2: Tests que siempre pasan

```diff
- ❌ MAL:
it('should work', () => {
  expect(true).toBe(true);  // Inútil
});

+ ✅ BIEN:
it('should return user by id', async () => {
  const user = await service.findById(1);
  expect(user.id).toBe(1);
  expect(user.email).toBeDefined();
});
```

---

### ❌ Anti-Pattern #3: Agregar features no testeadas en GREEN

```diff
- ❌ MAL (GREEN phase):
async login(dto: LoginDto) {
  const user = await this.validateUser(dto);

  // ❌ No hay test para esto!
  await this.logLoginAttempt(user);
  await this.sendWelcomeEmail(user);

  return { access_token: this.generateToken(user) };
}

+ ✅ BIEN:
async login(dto: LoginDto) {
  const user = await this.validateUser(dto);
  return { access_token: this.generateToken(user) };
}

// Si quieres logging/email → Escribe TEST primero (nuevo ciclo RED)
```

---

### ❌ Anti-Pattern #4: Cambiar comportamiento en REFACTOR

```diff
- ❌ MAL (REFACTOR phase):
// Original: lanza UnauthorizedException
async validateUser(dto: LoginDto) {
  const user = await this.findUser(dto.email);
  if (!user) throw new UnauthorizedException();
  return user;
}

// Refactor: cambia a retornar null (BREAKING CHANGE)
async validateUser(dto: LoginDto) {
  const user = await this.findUser(dto.email);
  return user || null;  // ❌ Test fallará
}

+ ✅ BIEN (REFACTOR phase):
// Solo cambiar NOMBRES, ESTRUCTURA, no COMPORTAMIENTO
async validateUser(dto: LoginDto): Promise<User> {
  const user = await this.userRepository.findByEmail(dto.email);
  this.ensureUserExists(user);
  return user;
}

private ensureUserExists(user: User | null): asserts user is User {
  if (!user) throw new UnauthorizedException('User not found');
}
```

---

## 📋 TDD Checklist (Para Cada Feature)

### Pre-Development
- [ ] Requirement entendido
- [ ] Acceptance criteria definido
- [ ] Tipo de test decidido (unit/integration/e2e)

### RED Phase
- [ ] Test case escrito
- [ ] Test ejecutado → FALLA
- [ ] Error message es claro
- [ ] Test committed

### GREEN Phase
- [ ] Código mínimo implementado
- [ ] Test ejecutado → PASA
- [ ] NO código extra sin test
- [ ] Implementación committed

### REFACTOR Phase
- [ ] Code smells identificados
- [ ] Refactor aplicado
- [ ] Test ejecutado → SIGUE PASANDO
- [ ] Refactor committed

### Repeat
- [ ] Siguiente test case identificado
- [ ] Volver a RED phase

---

## 🎓 Ejemplo Completo: Feature "Password Reset"

### Iteration 1: Request Password Reset

**RED**:
```typescript
it('should send reset email for valid email', async () => {
  const response = await request(app)
    .post('/auth/password-reset-request')
    .send({ email: 'user@example.com' })
    .expect(200);

  expect(response.body.message).toBe('Reset email sent');
});
```
Ejecutar → ❌ FAIL (endpoint no existe)

**GREEN**:
```typescript
@Post('password-reset-request')
async requestPasswordReset(@Body() dto: PasswordResetRequestDto) {
  await this.authService.sendPasswordResetEmail(dto.email);
  return { message: 'Reset email sent' };
}
```
Ejecutar → ✅ PASS

**REFACTOR**:
```typescript
// Extraer constantes
const PASSWORD_RESET_SUCCESS = 'Reset email sent';

@Post('password-reset-request')
async requestPasswordReset(@Body() dto: PasswordResetRequestDto) {
  await this.authService.requestPasswordReset(dto.email);
  return { message: PASSWORD_RESET_SUCCESS };
}
```
Ejecutar → ✅ PASS (comportamiento idéntico)

---

### Iteration 2: Reset Password with Token

**RED**:
```typescript
it('should reset password with valid token', async () => {
  const response = await request(app)
    .post('/auth/reset-password')
    .send({ token: 'valid-token', newPassword: 'newpass123' })
    .expect(200);

  expect(response.body.message).toBe('Password updated');
});
```
Ejecutar → ❌ FAIL (endpoint no existe)

**GREEN**: [Implementar...]

**REFACTOR**: [Mejorar...]

---

## 🔄 Integration con Workflow

**Auto-transición después de Brainstorming/Planning**:

```typescript
if (planningComplete && tasksIdentified) {
  transition_to('tdd-workflow', {
    tasks: tasks,
    testStrategy: 'test-first',
    mode: 'RED-GREEN-REFACTOR'
  });
}
```

---

## 📊 Métricas de Éxito

Después de aplicar TDD:

- **Test Coverage**: > 80% (ideal > 90%)
- **Bug Density**: Reducción del 40-60%
- **Refactor Confidence**: Tests garantizan no-regression
- **Documentation**: Tests sirven como documentación viva

---

## 🎯 Summary

**TDD Rule**:
```
IF implementing feature OR fixing bug
THEN use TDD workflow
  1. RED: Write failing test (verificar que falla)
  2. GREEN: Implement minimum code (verificar que pasa)
  3. REFACTOR: Improve code (verificar que sigue pasando)
  4. REPEAT: Next test case
```

**Remember**: Test-first approach previene bugs y reduce tiempo de debugging.

---

## Ralph Loop Integration (v2.0)

This skill is **Ralph-ready** and can be executed in iterative self-correction mode.

### Completion Signal

When this skill completes successfully in Ralph mode, it MUST output:

```
<promise>COMPLETE</promise>
```

### Completion Criteria

Before outputting the completion promise, verify ALL of these:

- [ ] All tests pass (`npm test` exit code 0)
- [ ] Test coverage >= 80% (if required)
- [ ] No TypeScript compilation errors (`tsc --noEmit`)
- [ ] No `any` types in newly written code
- [ ] No N+1 queries (if database code)

### Self-Correction Pattern

When executed in Ralph mode (multiple iterations):

**Iteration 1 (RED Phase)**:
- Write failing test that describes expected behavior
- Run `npm test` → Test MUST fail
- DO NOT output completion promise yet

**Iterations 2-N (GREEN Phase)**:
- Read test output from previous iteration
- Identify what's failing (read error messages carefully)
- Implement minimal code to make test pass
- Run `npm test` again
- If tests pass AND all criteria met → output `<promise>COMPLETE</promise>`
- If tests fail → analyze failure, try different approach

**Key Behaviors in Ralph Mode**:
- Always run `npm test` after making changes
- Read test failures as instructions (they tell you exactly what to fix)
- If same test fails 3+ times, try completely different approach
- Prefer simple solutions over complex ones
- Don't add untested code

### Progress Indicators

To avoid stall detection, each iteration should produce:
- New files created, OR
- Modifications to existing files, OR
- Reduction in number of failing tests

If 5 consecutive iterations produce none of these, Ralph will abort with STALL_DETECTED.

### Example Ralph Iteration Flow

```
Iteration 1:
  → Write test for user registration
  → Run npm test → FAIL (method doesn't exist)
  → No completion promise (not done yet)

Iteration 2:
  → Read error: "registerUser is not defined"
  → Implement registerUser method
  → Run npm test → FAIL (email validation missing)
  → No completion promise (still failing)

Iteration 3:
  → Read error: "Expected email validation to fail"
  → Add email validation logic
  → Run npm test → FAIL (password strength check missing)
  → No completion promise (still failing)

Iteration 4:
  → Read error: "Expected weak password to be rejected"
  → Add password strength validation
  → Run npm test → PASS (all 5 tests passing)
  → Coverage: 85%
  → Output: <promise>COMPLETE</promise> ✅
```

### Context from Previous Iterations

When Ralph re-invokes this skill, you'll receive enriched context:

```
[Your original task]

---
[Ralph Loop Context - Iteration N]

Modified files: src/auth/register.service.ts, src/auth/register.spec.ts
Last test output:
  FAIL src/auth/register.spec.ts
    ● should validate email format
      Expected "invalid@" to fail validation
File changes (last 3 iterations): 2, 1, 0

⚠️ WARNING: No file changes detected. You may be stalled.
```

Use this context to:
- See what you tried before (git diff, file changes)
- Read actual test failures (not guess)
- Avoid repeating same failed approach

---

**Auto-Activated In**: feature-development (all), bug-fixing (all)
**Ralph-Ready**: ✅ Yes (v2.0)
**Invocable**: `/tdd` or auto via session-orchestrator
