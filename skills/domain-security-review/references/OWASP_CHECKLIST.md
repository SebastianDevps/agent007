# OWASP Top 10 (2021) - Detailed Checklist

Quick reference for security-review skill. Use this for comprehensive audits.

---

## A01:2021 - Broken Access Control

### Authentication
- [ ] All routes require authentication (except public endpoints)
- [ ] JWT tokens have expiration
- [ ] Refresh tokens properly rotated
- [ ] Session timeout implemented (15-30 min inactivity)

### Authorization
- [ ] Role-based access control (RBAC) implemented
- [ ] Resource ownership validated before access
- [ ] No IDOR vulnerabilities (can't access /users/123 for other users)
- [ ] Admin routes protected with role checks

### CORS
- [ ] CORS whitelist configured (not `*`)
- [ ] Credentials allowed only for trusted origins
- [ ] Preflight requests handled correctly

---

## A02:2021 - Cryptographic Failures

### Password Security
- [ ] Bcrypt with cost ≥12 (not MD5, SHA1, or plain bcrypt with low cost)
- [ ] Password requirements: min 8 chars, complexity rules
- [ ] Password reset tokens expire (15 min)
- [ ] No password in logs or error messages

### Data Encryption
- [ ] Sensitive data encrypted at rest (PII, PCI data)
- [ ] TLS 1.2+ enforced
- [ ] Certificate valid and not self-signed
- [ ] HSTS header set (`Strict-Transport-Security`)

### Key Management
- [ ] API keys in environment variables (not committed)
- [ ] Secrets rotated regularly
- [ ] No hardcoded credentials in code

---

## A03:2021 - Injection

### SQL Injection
- [ ] Parameterized queries (TypeORM `where: { }` syntax)
- [ ] No raw SQL with string concatenation
- [ ] Input validation on all parameters
- [ ] Stored procedures parameterized

### NoSQL Injection
- [ ] MongoDB queries use proper operators
- [ ] No `$where` with user input
- [ ] Mongoose schema validation

### Command Injection
- [ ] No `exec`, `eval`, or `child_process` with user input
- [ ] Shell commands avoid user-controlled arguments
- [ ] Whitelist allowed commands

### XSS
- [ ] No `innerHTML` or `dangerouslySetInnerHTML` with user data
- [ ] React escapes by default (use `{}` not JSX strings)
- [ ] Content-Security-Policy header set

---

## A04:2021 - Insecure Design

### Rate Limiting
- [ ] Login endpoint rate limited (5 attempts / minute)
- [ ] API endpoints rate limited (100 req/min per user)
- [ ] Password reset rate limited (3 attempts / hour)

### Business Logic
- [ ] Financial transactions validated (amount > 0, balance check)
- [ ] Multi-step processes validate each step
- [ ] State transitions validated (can't skip steps)

### CSRF Protection
- [ ] CSRF tokens on state-changing operations
- [ ] SameSite cookie attribute set
- [ ] Double-submit cookie pattern (if stateless)

---

## A05:2021 - Security Misconfiguration

### Error Handling
- [ ] Stack traces hidden in production
- [ ] Generic error messages (don't leak DB structure)
- [ ] 404 pages don't reveal file structure

### Security Headers
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-Frame-Options: DENY`
- [ ] `X-XSS-Protection: 1; mode=block`
- [ ] `Content-Security-Policy` configured
- [ ] `Referrer-Policy: no-referrer`

### Environment
- [ ] Debug mode off in production
- [ ] Default credentials changed
- [ ] Unnecessary services disabled
- [ ] Directory listing disabled

---

## A06:2021 - Vulnerable and Outdated Components

### Dependencies
- [ ] `npm audit` shows 0 high/critical vulnerabilities
- [ ] Dependencies updated monthly
- [ ] Lock files (`package-lock.json`) committed
- [ ] No deprecated packages

### Monitoring
- [ ] Dependabot or Snyk enabled
- [ ] CI fails on high/critical vulnerabilities
- [ ] Security patches applied within 7 days

---

## A07:2021 - Identification and Authentication Failures

### Authentication
- [ ] Multi-factor authentication available
- [ ] Account lockout after 5 failed attempts
- [ ] Lockout duration: 15-30 minutes
- [ ] Email verification required

### Session Management
- [ ] Session IDs not in URL
- [ ] Sessions invalidated on logout
- [ ] Concurrent session limit (optional)
- [ ] Session fixation prevented (regenerate on login)

### Password Policy
- [ ] Minimum 8 characters
- [ ] Complexity: uppercase, lowercase, number, symbol
- [ ] Password history (prevent reuse of last 5)
- [ ] No common passwords (check against list)

---

## A08:2021 - Software and Data Integrity Failures

### CI/CD
- [ ] Code review required before merge
- [ ] Automated tests run on every commit
- [ ] Secrets not in repository
- [ ] Build artifacts signed

### Dependencies
- [ ] Subresource Integrity (SRI) for CDN scripts
- [ ] Package signatures verified
- [ ] No untrusted package sources

### Updates
- [ ] Auto-updates disabled (manual review required)
- [ ] Rollback plan documented
- [ ] Database migrations reversible

---

## A09:2021 - Security Logging and Monitoring Failures

### Logging
- [ ] Login attempts logged (success and failure)
- [ ] Access denied events logged
- [ ] Admin actions audited
- [ ] Sensitive data NOT logged (passwords, tokens)

### Monitoring
- [ ] Failed login threshold alerts (10+ in 5 min)
- [ ] Unusual access patterns detected
- [ ] Error rate monitoring
- [ ] Log retention: 90 days minimum

### Incident Response
- [ ] Security incident response plan exists
- [ ] Logs centralized and searchable
- [ ] Alerts routed to security team
- [ ] Forensics-ready logging (timestamp, user, action, IP)

---

## A10:2021 - Server-Side Request Forgery (SSRF)

### URL Validation
- [ ] Whitelist of allowed external domains
- [ ] Block internal IP ranges (localhost, 192.168.*, 10.*)
- [ ] Block cloud metadata endpoints (169.254.169.254)
- [ ] DNS rebinding prevented

### API Calls
- [ ] User input not directly used in fetch/axios URLs
- [ ] URL parsing and validation before requests
- [ ] Timeout on external requests (5-10 sec)

---

## Additional Checks (Beyond OWASP Top 10)

### API Security
- [ ] API versioning (`/api/v1/`)
- [ ] Pagination on list endpoints (prevent resource exhaustion)
- [ ] Input size limits (max payload 10MB)
- [ ] GraphQL query depth limiting

### File Upload
- [ ] File type validation (whitelist extensions)
- [ ] File size limits enforced
- [ ] Files scanned for malware
- [ ] Uploaded files not executable
- [ ] File storage outside web root

### Compliance
- [ ] GDPR: Data deletion endpoints
- [ ] GDPR: Data export endpoints
- [ ] SOC2: Audit logs for all data access
- [ ] PCI DSS: No credit card storage (use Stripe/payment gateway)

---

## Severity Levels

**Critical**: Exploitable, leads to data breach or account takeover
- SQL Injection, Authentication bypass, RCE

**High**: Exploitable, impacts confidentiality/integrity
- XSS, CSRF, Missing authorization

**Medium**: Exploitable, limited impact or requires user interaction
- Information disclosure, weak crypto

**Low**: Best practice, defense in depth
- Missing security headers, outdated dependencies (low severity)

---

## Testing Tools

### Automated
- `npm audit` - Dependency vulnerabilities
- `eslint-plugin-security` - Code pattern analysis
- OWASP ZAP - Dynamic security testing
- Snyk - Continuous monitoring

### Manual
- Burp Suite - Request interception
- Postman - API endpoint testing
- Browser DevTools - Client-side inspection
