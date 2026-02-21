# NestJS Code Reviewer - Quick Reference

> **Full details**: See SKILL.md for complete security checklist

## Security Quick Scan

### OWASP Top 10 Checklist

**1. Injection** (SQL, NoSQL, Command)
- [ ] No raw SQL queries (use QueryBuilder or ORM)
- [ ] Input validation con class-validator
- [ ] Parameterized queries (TypeORM safe by default)

**2. Authentication**
- [ ] JWT tokens con expiración
- [ ] Passwords hashed (bcrypt, rounds >= 12)
- [ ] No secrets hardcoded
- [ ] Refresh token rotation

**3. Sensitive Data Exposure**
- [ ] HTTPS only en producción
- [ ] No passwords/tokens en logs
- [ ] Env variables para secrets
- [ ] No datos sensibles en responses

**4. XML External Entities (XXE)**
- [ ] Validar y sanitizar XML uploads
- [ ] Deshabilitar external entities

**5. Access Control**
- [ ] Guards en todos los endpoints protegidos
- [ ] RBAC (Role-Based Access Control)
- [ ] Resource ownership verification

**6. Security Misconfiguration**
- [ ] Helmet.js habilitado
- [ ] CORS correctamente configurado
- [ ] Rate limiting (ThrottlerModule)
- [ ] Disable error stack traces en prod

**7. XSS (Cross-Site Scripting)**
- [ ] Input sanitization
- [ ] Output encoding
- [ ] CSP headers

**8. Insecure Deserialization**
- [ ] Validar DTOs antes de deserializar
- [ ] No usar `eval()` o `Function()`

**9. Components with Known Vulnerabilities**
- [ ] `npm audit` regularmente
- [ ] Dependencias actualizadas
- [ ] Snyk o Dependabot

**10. Insufficient Logging**
- [ ] Log de eventos de seguridad
- [ ] No loggear datos sensibles
- [ ] Correlation IDs para tracing

## Code Quality Quick Scan

**Anti-patterns**:
- ❌ `any` types
- ❌ N+1 queries
- ❌ Hardcoded values
- ❌ God classes (> 500 líneas)
- ❌ No error handling
- ❌ Missing validation decorators

**Best practices**:
- ✅ DTOs con validation
- ✅ Repository pattern
- ✅ Dependency injection
- ✅ Exception filters
- ✅ Logging con contexto
- ✅ Unit tests

## Common Vulnerabilities

### SQL Injection (VULNERABLE)
```typescript
// ❌ NEVER
await db.query(`SELECT * FROM users WHERE id = ${userId}`);

// ✅ Safe
await userRepo.findOne({ where: { id: userId } });
```

### Missing Validation
```typescript
// ❌ No validation
async create(@Body() dto: any) { }

// ✅ Validated DTO
export class CreateUserDto {
  @IsEmail()
  @IsNotEmpty()
  email: string;
}
```

### Exposed Secrets
```typescript
// ❌ Hardcoded
const JWT_SECRET = 'my-secret-123';

// ✅ Environment
const JWT_SECRET = process.env.JWT_SECRET;
```

### No Rate Limiting
```typescript
// ❌ No protection
@Post('login')
async login() { }

// ✅ Protected
@UseGuards(ThrottlerGuard)
@Throttle(5, 60) // 5 req/min
@Post('login')
async login() { }
```

## Quick Review Flow

1. **Security scan** (OWASP checklist)
2. **Input validation** (DTOs completos)
3. **Error handling** (try-catch, filters)
4. **Performance** (N+1 queries, indexing)
5. **Code quality** (no `any`, DRY, SOLID)

---

Ver SKILL.md para checklist completo y ejemplos de refactorización.
