---
name: security-review
description: "Security audit for code focusing on OWASP Top 10, authentication, authorization, and sensitive data handling. Use when user asks to 'review security', 'security audit', or 'check vulnerabilities'."
version: 1.0.0
invokable: true
accepts_args: true
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Security Review - OWASP Top 10 & Best Practices

**Purpose**: Perform comprehensive security audits of code, focusing on OWASP Top 10 vulnerabilities, authentication/authorization, and sensitive data protection.

**When to use**:
- Before production deployment
- After implementing auth/payment features
- When user requests security audit
- For compliance requirements (SOC2, GDPR, PCI)

---

## Review Process

### Phase 1: Scope Assessment (5 min)

Ask the user:

```markdown
**Security Review Scope**

What would you like me to review?

A) Full codebase security audit (comprehensive)
B) Specific module/feature (focused)
C) Authentication/Authorization only
D) API endpoints security
E) Database queries and data handling

Which option? [A/B/C/D/E]

If B: Which module/files?
```

---

### Phase 2: Automated Scanning (2-3 min)

Run automated checks:

```bash
# 1. Search for common vulnerabilities
grep -r "eval\|exec\|innerHTML\|dangerouslySetInnerHTML" src/

# 2. Check for hardcoded secrets
grep -r "password.*=\|api_key.*=\|secret.*=" --include="*.ts" --include="*.js" src/

# 3. Find SQL query patterns (potential injection)
grep -r "query.*+\|execute.*+" --include="*.ts" src/

# 4. Check for insecure dependencies
npm audit --json | jq '.vulnerabilities | to_entries[] | select(.value.severity == "high" or .value.severity == "critical")'
```

---

### Phase 3: Manual Code Review

Review against OWASP Top 10 (2021):

#### 1. Broken Access Control

**Check**:
- [ ] Routes have authentication middleware
- [ ] Authorization checks before data access
- [ ] No IDOR (Insecure Direct Object References)
- [ ] CORS configured correctly

**Example - Good**:
```typescript
// ✅ Proper authorization
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Get('users/:id')
async getUser(@Param('id') id: string, @CurrentUser() user: User) {
  // Check if user can access this resource
  if (user.role !== 'admin' && user.id !== id) {
    throw new ForbiddenException('Cannot access other users');
  }
  return this.usersService.findById(id);
}
```

**Example - Bad**:
```typescript
// ❌ No authorization check
@Get('users/:id')
async getUser(@Param('id') id: string) {
  return this.usersService.findById(id); // Anyone can access any user!
}
```

---

#### 2. Cryptographic Failures

**Check**:
- [ ] Passwords hashed with bcrypt (cost ≥12)
- [ ] Sensitive data encrypted at rest
- [ ] TLS/HTTPS enforced
- [ ] No weak algorithms (MD5, SHA1)

**Example - Good**:
```typescript
// ✅ Proper password hashing
import * as bcrypt from 'bcrypt';

async hashPassword(password: string): Promise<string> {
  const salt = await bcrypt.genSalt(12); // Cost factor 12
  return bcrypt.hash(password, salt);
}

async verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

**Example - Bad**:
```typescript
// ❌ Weak hashing
import { createHash } from 'crypto';

hashPassword(password: string): string {
  return createHash('md5').update(password).digest('hex'); // MD5 is broken!
}
```

---

#### 3. Injection

**Check**:
- [ ] Parameterized queries (TypeORM)
- [ ] Input validation with class-validator
- [ ] No string concatenation in queries
- [ ] SQL, NoSQL, Command injection prevented

**Example - Good**:
```typescript
// ✅ Parameterized query
async findByEmail(email: string): Promise<User> {
  return this.userRepository.findOne({
    where: { email } // Safe - TypeORM parameterizes
  });
}

// ✅ Input validation
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

**Example - Bad**:
```typescript
// ❌ SQL Injection vulnerability
async findByEmail(email: string): Promise<User> {
  return this.userRepository.query(
    `SELECT * FROM users WHERE email = '${email}'` // Dangerous!
  );
}
```

---

#### 4. Insecure Design

**Check**:
- [ ] Rate limiting on sensitive endpoints
- [ ] CSRF protection enabled
- [ ] Secure session management
- [ ] Business logic validated

**Example - Good**:
```typescript
// ✅ Rate limiting
@UseGuards(ThrottlerGuard)
@Throttle(5, 60) // 5 requests per 60 seconds
@Post('login')
async login(@Body() loginDto: LoginDto) {
  return this.authService.login(loginDto);
}

// ✅ CSRF protection
app.use(csurf({ cookie: true }));
```

---

#### 5. Security Misconfiguration

**Check**:
- [ ] Error messages don't leak info
- [ ] Debug mode disabled in production
- [ ] Security headers configured
- [ ] Default credentials changed

**Example - Good**:
```typescript
// ✅ Safe error handling
@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost) {
    const response = host.switchToHttp().getResponse();
    const status = exception.getStatus();
    
    // Don't leak stack traces in production
    const errorResponse = process.env.NODE_ENV === 'production'
      ? { statusCode: status, message: 'An error occurred' }
      : { statusCode: status, message: exception.message, stack: exception.stack };
    
    response.status(status).json(errorResponse);
  }
}

// ✅ Security headers
import helmet from 'helmet';
app.use(helmet());
```

---

#### 6. Vulnerable Components

**Check**:
- [ ] Dependencies up to date
- [ ] No known vulnerabilities (npm audit)
- [ ] Minimal dependency footprint
- [ ] Lock files committed

**Commands**:
```bash
npm audit
npm outdated
npm audit fix
```

---

#### 7. Identification & Authentication Failures

**Check**:
- [ ] Multi-factor authentication available
- [ ] Session timeout implemented
- [ ] Password requirements enforced
- [ ] Account lockout after failed attempts

**Example - Good**:
```typescript
// ✅ Account lockout
const MAX_LOGIN_ATTEMPTS = 5;
const LOCKOUT_TIME = 15 * 60 * 1000; // 15 minutes

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

---

#### 8. Software & Data Integrity Failures

**Check**:
- [ ] CI/CD pipeline secured
- [ ] Code signing/verification
- [ ] Dependency integrity (SRI)
- [ ] No unsigned/untrusted packages

---

#### 9. Security Logging & Monitoring Failures

**Check**:
- [ ] Authentication events logged
- [ ] Failed access attempts logged
- [ ] Sensitive operations audited
- [ ] Log retention policy

**Example - Good**:
```typescript
// ✅ Security logging
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

// Usage
this.securityLogger.log('access_denied', user.id, {
  ip: request.ip,
  userAgent: request.headers['user-agent'],
  resource: '/admin/users'
});
```

---

#### 10. Server-Side Request Forgery (SSRF)

**Check**:
- [ ] URL validation for external requests
- [ ] Whitelist of allowed domains
- [ ] No user-controlled URLs
- [ ] Internal network protection

**Example - Good**:
```typescript
// ✅ SSRF protection
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

---

## Phase 4: Generate Security Report

After review, generate:

```markdown
# Security Review Report - [Module/Feature Name]

**Date**: [YYYY-MM-DD]
**Reviewer**: Claude Security Expert
**Scope**: [Description]

---

## Executive Summary

[1-2 sentences: overall security posture]

---

## Findings

### Critical (Fix Immediately)
- [ ] **[VULN-001]** [Description]
  - **Risk**: High
  - **Location**: `file.ts:123`
  - **Fix**: [Specific remediation]

### High (Fix Before Production)
- [ ] **[VULN-002]** [Description]
  - **Risk**: High
  - **Location**: `file.ts:456`
  - **Fix**: [Specific remediation]

### Medium (Address Soon)
- [ ] **[VULN-003]** [Description]
  - **Risk**: Medium
  - **Location**: `file.ts:789`
  - **Fix**: [Specific remediation]

### Low (Best Practice)
- [ ] **[VULN-004]** [Description]
  - **Risk**: Low
  - **Location**: `file.ts:012`
  - **Fix**: [Specific remediation]

---

## OWASP Top 10 Coverage

| Category | Status | Notes |
|----------|--------|-------|
| 1. Broken Access Control | ✅ Pass | Auth guards properly implemented |
| 2. Cryptographic Failures | ⚠️ Partial | Upgrade bcrypt cost to 12 |
| 3. Injection | ✅ Pass | TypeORM parameterized queries used |
| 4. Insecure Design | ❌ Fail | Missing rate limiting on /login |
| 5. Security Misconfiguration | ✅ Pass | Helmet configured |
| 6. Vulnerable Components | ⚠️ Partial | 2 medium severity npm audit issues |
| 7. Auth Failures | ❌ Fail | No account lockout mechanism |
| 8. Data Integrity | ✅ Pass | CI/CD secured |
| 9. Logging Failures | ⚠️ Partial | Add audit logs for admin actions |
| 10. SSRF | ✅ Pass | No external URL handling |

---

## Recommendations Priority

1. **Immediate** (before next deployment):
   - Fix [VULN-001]
   - Fix [VULN-002]

2. **Short-term** (within 1 week):
   - Implement account lockout
   - Add rate limiting

3. **Medium-term** (within 1 month):
   - Upgrade dependencies
   - Enhance audit logging

---

## Compliance Notes

- **SOC2**: Missing audit logs for admin actions
- **GDPR**: Ensure data encryption at rest
- **PCI DSS**: (if applicable) Validate PAN handling

---

**Next Review**: [Date 3 months from now]
```

---

## Checklist: Security Review Complete

Before marking as complete:

- [ ] Automated scans executed
- [ ] OWASP Top 10 manually reviewed
- [ ] Critical findings documented
- [ ] Remediation steps provided
- [ ] Report generated and shared
- [ ] Follow-up review scheduled (if needed)

---

## Integration with Workflow

```
security-review (this skill)
  → Triggered by user request or pre-deployment
  → Scans code for OWASP Top 10
  → Generates security report
  → Output: Vulnerability list + remediation steps

systematic-debugging (if vulnerabilities found)
  → Fix identified security issues
  → Verify fixes work
  → Re-run security-review
```

---

## Quick Reference: Common Vulnerabilities

| Vulnerability | Pattern to Search | Fix |
|---------------|-------------------|-----|
| SQL Injection | `.query(.*+.*)` | Use parameterized queries |
| XSS | `innerHTML\|dangerouslySetInnerHTML` | Sanitize input, use templates |
| Hardcoded secrets | `password.*=\|api_key.*=` | Use environment variables |
| Weak crypto | `md5\|sha1` | Use bcrypt for passwords, SHA-256+ for hashing |
| Missing auth | Routes without `@UseGuards` | Add authentication guards |
| IDOR | Direct DB access without ownership check | Validate user owns resource |

---

**Required tools**: Read, Grep, Glob, Bash (for npm audit)
**Estimated time**: 15-30 min for focused review, 1-2 hours for full codebase
**Output**: Security report with prioritized findings
