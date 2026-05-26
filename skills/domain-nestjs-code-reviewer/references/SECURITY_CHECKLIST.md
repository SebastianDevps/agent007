# Security Checklist - NestJS + TypeORM

## OWASP Top 10 (2021) - NestJS Context

### A01:2021 - Broken Access Control

**Validación de Ownership**:
```typescript
// ✅ Guard personalizado
@Injectable()
export class ResourceOwnerGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const user = request.user;
    const resourceId = request.params.id;

    // Validar que el usuario es dueño del recurso
    return this.checkOwnership(user.id, resourceId);
  }
}
```

**Rate Limiting**:
```typescript
// app.module.ts
import { ThrottlerModule } from '@nestjs/throttler';

ThrottlerModule.forRoot({
  ttl: 60,
  limit: 10, // 10 requests por minuto
});
```

---

### A02:2021 - Cryptographic Failures

**Password Hashing**:
```typescript
import * as bcrypt from 'bcrypt';

// ✅ Mínimo 10 rounds
const hash = await bcrypt.hash(password, 12);
```

**Sensitive Data**:
```typescript
// Entity
@Entity()
export class User {
  @Column()
  @Exclude() // No retornar en responses
  password: string;

  @Column()
  @Exclude()
  resetToken?: string;
}
```

**Environment Variables**:
```typescript
// ✅ Validar en startup
@Module({
  imports: [
    ConfigModule.forRoot({
      validationSchema: Joi.object({
        DATABASE_URL: Joi.string().required(),
        JWT_SECRET: Joi.string().min(32).required(),
      }),
    }),
  ],
})
```

---

### A03:2021 - Injection

**SQL Injection**:
```typescript
// ❌ NUNCA
const users = await repo.query(
  `SELECT * FROM users WHERE role = '${role}'`
);

// ✅ SIEMPRE
const users = await repo.query(
  'SELECT * FROM users WHERE role = $1',
  [role]
);

// ✅ MEJOR: QueryBuilder
const users = await repo.createQueryBuilder('user')
  .where('user.role = :role', { role })
  .getMany();
```

**NoSQL Injection** (si usas MongoDB):
```typescript
// ❌ Vulnerable
find({ email: req.body.email });

// ✅ Seguro
find({ email: String(req.body.email) });
```

---

### A04:2021 - Insecure Design

**Business Logic Validation**:
```typescript
// ✅ Validar lógica de negocio
async transferMoney(from: string, to: string, amount: number) {
  if (amount <= 0) {
    throw new BadRequestException('Amount must be positive');
  }

  const balance = await this.getBalance(from);
  if (balance < amount) {
    throw new BadRequestException('Insufficient funds');
  }

  // Race condition protection con transacción
  await this.dataSource.transaction(async (manager) => {
    await manager.decrement(Account, { id: from }, 'balance', amount);
    await manager.increment(Account, { id: to }, 'balance', amount);
  });
}
```

---

### A05:2021 - Security Misconfiguration

**CORS**:
```typescript
// ❌ Inseguro
app.enableCors({ origin: '*' });

// ✅ Específico
app.enableCors({
  origin: ['https://myapp.com'],
  credentials: true,
});
```

**Helmet (Security Headers)**:
```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
    },
  },
}));
```

**Production Settings**:
```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}

// main.ts
if (process.env.NODE_ENV === 'production') {
  app.disable('x-powered-by');
  app.useGlobalFilters(new AllExceptionsFilter());
}
```

---

### A06:2021 - Vulnerable Components

**Dependency Auditing**:
```bash
# Ejecutar regularmente
npm audit
npm audit fix

# CI/CD
npm audit --audit-level=moderate
```

---

### A07:2021 - Identification/Authentication Failures

**JWT Best Practices**:
```typescript
// ✅ Token con expiración corta
JwtModule.register({
  secret: process.env.JWT_SECRET,
  signOptions: {
    expiresIn: '15m', // Access token corto
    algorithm: 'HS256'
  },
});

// ✅ Refresh token en httpOnly cookie
@Post('refresh')
async refresh(@Req() req, @Res() res) {
  const refreshToken = req.cookies['refresh_token'];
  // Validar y generar nuevo access token
}
```

**Session Security**:
```typescript
// express-session config
{
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    httpOnly: true,
    secure: true, // HTTPS only
    sameSite: 'strict',
    maxAge: 3600000 // 1 hora
  }
}
```

---

### A08:2021 - Software/Data Integrity Failures

**Package Integrity**:
```bash
# Usar lock files
npm ci # En CI/CD, no npm install
```

**Logging de Cambios Críticos**:
```typescript
@Injectable()
export class AuditLogger {
  async logCriticalChange(action: string, userId: string, data: any) {
    await this.auditRepo.save({
      action,
      userId,
      data,
      timestamp: new Date(),
      ipAddress: this.request.ip,
    });
  }
}
```

---

### A09:2021 - Logging Failures

**Structured Logging**:
```typescript
import { Logger } from '@nestjs/common';

// ✅ Log de eventos de seguridad
this.logger.warn({
  event: 'failed_login_attempt',
  username: dto.username,
  ip: request.ip,
  timestamp: new Date(),
});

// ❌ NO loguear datos sensibles
this.logger.log(`User ${user.password}`); // NUNCA
```

---

### A10:2021 - Server-Side Request Forgery (SSRF)

**Validación de URLs**:
```typescript
import { isURL } from 'class-validator';

@Injectable()
export class HttpService {
  async fetch(url: string) {
    // ✅ Validar que no sea URL interna
    if (this.isInternalUrl(url)) {
      throw new BadRequestException('Internal URLs not allowed');
    }

    // ✅ Whitelist de dominios permitidos
    const allowed = ['api.example.com', 'cdn.example.com'];
    const hostname = new URL(url).hostname;

    if (!allowed.includes(hostname)) {
      throw new BadRequestException('Domain not allowed');
    }

    return axios.get(url);
  }

  private isInternalUrl(url: string): boolean {
    const hostname = new URL(url).hostname;
    return ['localhost', '127.0.0.1', '0.0.0.0'].includes(hostname)
      || hostname.startsWith('192.168.')
      || hostname.startsWith('10.');
  }
}
```

---

## Quick Security Checklist

- [ ] Todos los endpoints tienen guards apropiados
- [ ] DTOs con `class-validator` en todos los inputs
- [ ] `ValidationPipe` global con `whitelist: true`
- [ ] Passwords hasheados con bcrypt (min 12 rounds)
- [ ] JWT con expiración < 1 hora
- [ ] CORS configurado específicamente (no `*`)
- [ ] Helmet habilitado con CSP
- [ ] Rate limiting en endpoints públicos
- [ ] SQL queries usan parámetros, no concatenación
- [ ] Sensitive data con `@Exclude()` en entities
- [ ] Variables en `.env`, validadas en startup
- [ ] HTTPS en producción (secure cookies)
- [ ] Logging de eventos de seguridad
- [ ] `npm audit` sin vulnerabilities críticas
- [ ] Error messages no exponen stack traces en prod
