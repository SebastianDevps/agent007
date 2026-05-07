# OWASP Top 10 (2021) — Code Review Guide

## 1. Broken Access Control

**Check**:
- [ ] Routes have authentication middleware
- [ ] Authorization checks before data access
- [ ] No IDOR (Insecure Direct Object References)
- [ ] CORS configured correctly

**Good**:
```typescript
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Get('users/:id')
async getUser(@Param('id') id: string, @CurrentUser() user: User) {
  if (user.role !== 'admin' && user.id !== id) {
    throw new ForbiddenException('Cannot access other users');
  }
  return this.usersService.findById(id);
}
```

**Bad**:
```typescript
@Get('users/:id')
async getUser(@Param('id') id: string) {
  return this.usersService.findById(id); // Anyone can access any user!
}
```

## 2. Cryptographic Failures

**Check**:
- [ ] Passwords hashed with bcrypt (cost ≥12)
- [ ] Sensitive data encrypted at rest
- [ ] TLS/HTTPS enforced
- [ ] No weak algorithms (MD5, SHA1)

**Good**:
```typescript
import * as bcrypt from 'bcrypt';

async hashPassword(password: string): Promise<string> {
  const salt = await bcrypt.genSalt(12);
  return bcrypt.hash(password, salt);
}

async verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

**Bad**:
```typescript
import { createHash } from 'crypto';

hashPassword(password: string): string {
  return createHash('md5').update(password).digest('hex'); // MD5 is broken!
}
```

## 3. Injection

**Check**:
- [ ] Parameterized queries (TypeORM)
- [ ] Input validation with class-validator
- [ ] No string concatenation in queries
- [ ] SQL, NoSQL, Command injection prevented

**Good**:
```typescript
async findByEmail(email: string): Promise<User> {
  return this.userRepository.findOne({ where: { email } });
}

class CreateUserDto {
  @IsEmail()
  @IsNotEmpty()
  email: string;

  @IsString()
  @MinLength(8)
  @Matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
  password: string;
}
```

**Bad**:
```typescript
async findByEmail(email: string): Promise<User> {
  return this.userRepository.query(
    `SELECT * FROM users WHERE email = '${email}'`
  );
}
```

## 4. Insecure Design

**Check**:
- [ ] Rate limiting on sensitive endpoints
- [ ] CSRF protection enabled
- [ ] Secure session management
- [ ] Business logic validated

**Good**:
```typescript
@UseGuards(ThrottlerGuard)
@Throttle(5, 60)
@Post('login')
async login(@Body() loginDto: LoginDto) {
  return this.authService.login(loginDto);
}

app.use(csurf({ cookie: true }));
```

## 5. Security Misconfiguration

**Check**:
- [ ] Error messages don't leak info
- [ ] Debug mode disabled in production
- [ ] Security headers configured
- [ ] Default credentials changed

**Good**:
```typescript
@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost) {
    const response = host.switchToHttp().getResponse();
    const status = exception.getStatus();

    const errorResponse = process.env.NODE_ENV === 'production'
      ? { statusCode: status, message: 'An error occurred' }
      : { statusCode: status, message: exception.message, stack: exception.stack };

    response.status(status).json(errorResponse);
  }
}

import helmet from 'helmet';
app.use(helmet());
```

## 6. Vulnerable Components

**Check**:
- [ ] Dependencies up to date
- [ ] No known vulnerabilities (npm audit)
- [ ] Minimal dependency footprint
- [ ] Lock files committed

```bash
npm audit
npm outdated
npm audit fix
```

## 7. Identification & Authentication Failures

**Check**:
- [ ] Multi-factor authentication available
- [ ] Session timeout implemented
- [ ] Password requirements enforced
- [ ] Account lockout after failed attempts

**Good**:
```typescript
const MAX_LOGIN_ATTEMPTS = 5;
const LOCKOUT_TIME = 15 * 60 * 1000;

async login(loginDto: LoginDto) {
  const user = await this.findByEmail(loginDto.email);

  if (user.lockoutUntil && user.lockoutUntil > new Date()) {
    throw new ForbiddenException('Account locked. Try again later.');
  }

  const valid = await bcrypt.compare(loginDto.password, user.passwordHash);

  if (!valid) {
    user.failedLoginAttempts++;
    if (user.failedLoginAttempts >= MAX_LOGIN_ATTEMPTS) {
      user.lockoutUntil = new Date(Date.now() + LOCKOUT_TIME);
    }
    await this.userRepository.save(user);
    throw new UnauthorizedException('Invalid credentials');
  }

  user.failedLoginAttempts = 0;
  user.lockoutUntil = null;
  await this.userRepository.save(user);

  return this.generateToken(user);
}
```

## 8. Software & Data Integrity Failures

**Check**:
- [ ] CI/CD pipeline secured
- [ ] Code signing/verification
- [ ] Dependency integrity (SRI)
- [ ] No unsigned/untrusted packages

## 9. Security Logging & Monitoring Failures

**Check**:
- [ ] Authentication events logged
- [ ] Failed access attempts logged
- [ ] Sensitive operations audited
- [ ] Log retention policy

**Good**:
```typescript
@Injectable()
export class SecurityLogger {
  log(event: 'login' | 'logout' | 'access_denied', userId: string, metadata: any) {
    this.logger.warn({
      event,
      userId,
      timestamp: new Date().toISOString(),
      ip: metadata.ip,
      userAgent: metadata.userAgent,
      resource: metadata.resource
    });
  }
}

this.securityLogger.log('access_denied', user.id, {
  ip: request.ip,
  userAgent: request.headers['user-agent'],
  resource: '/admin/users'
});
```

## 10. Server-Side Request Forgery (SSRF)

**Check**:
- [ ] URL validation for external requests
- [ ] Whitelist of allowed domains
- [ ] No user-controlled URLs
- [ ] Internal network protection

**Good**:
```typescript
const ALLOWED_DOMAINS = ['api.stripe.com', 'api.twilio.com'];

async fetchExternal(url: string) {
  const parsedUrl = new URL(url);

  if (!ALLOWED_DOMAINS.includes(parsedUrl.hostname)) {
    throw new BadRequestException('Domain not allowed');
  }

  if (parsedUrl.hostname === 'localhost' || parsedUrl.hostname.startsWith('192.168.')) {
    throw new BadRequestException('Internal URLs not allowed');
  }

  return fetch(url);
}
```
