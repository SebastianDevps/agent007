# Security Review Output Template

After review, generate:

```markdown
# Security Review Output - [Module/Feature Name]

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
| 1. Broken Access Control | Pass | Auth guards properly implemented |
| 2. Cryptographic Failures | Partial | Upgrade bcrypt cost to 12 |
| 3. Injection | Pass | TypeORM parameterized queries used |
| 4. Insecure Design | Fail | Missing rate limiting on /login |
| 5. Security Misconfiguration | Pass | Helmet configured |
| 6. Vulnerable Components | Partial | 2 medium severity npm audit issues |
| 7. Auth Failures | Fail | No account lockout mechanism |
| 8. Data Integrity | Pass | CI/CD secured |
| 9. Logging Failures | Partial | Add audit logs for admin actions |
| 10. SSRF | Pass | No external URL handling |

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
