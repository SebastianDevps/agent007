---
name: security-review
description: "Security audit for code focusing on OWASP Top 10, authentication, authorization, and sensitive data handling. Use when user asks to 'review security', 'security audit', or 'check vulnerabilities'."
canonical-sources:
  - url: https://owasp.org/www-project-top-ten/
    when: "for OWASP Top 10 references"
  - url: https://cheatsheetseries.owasp.org/
    when: "for OWASP cheatsheets"
  - url: https://nvd.nist.gov/
    when: "for CVE references"
version: 1.0.0
invokable: true
accepts_args: true
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
references:
  - references/review-process.md
  - references/owasp-top-10.md
  - references/output-template.md
  - references/quick-reference.md
  - references/OWASP_CHECKLIST.md
---

# Security Review — OWASP Top 10 & Best Practices

**Purpose**: perform comprehensive security audits of code, focusing on OWASP Top 10 vulnerabilities, authentication/authorization, and sensitive data protection.

---

## When to Invoke

- Before production deployment
- After implementing auth, payments, or any feature handling sensitive data
- User explicitly asks: "review security", "security audit", "check vulnerabilities"
- For compliance requirements (SOC2, GDPR, PCI DSS)
- After a security incident or CVE alert affecting dependencies

---

## Review Workflow

1. **Phase 1 — Scope Assessment** (5 min): clarify with user (full audit / focused module / auth only / API / data layer).
2. **Phase 2 — Automated Scanning** (2-3 min): grep for risky patterns + `npm audit`.
3. **Phase 3 — Manual Code Review**: walk OWASP Top 10 (2021).
4. **Phase 4 — Output Generation**: prioritized findings with file:line and remediation.

Detailed steps live in `references/review-process.md`.

---

## Anti-Patterns

- **Authorization checks omitted**: routes returning resources without verifying the caller's identity/role enable IDOR.
- **String concatenation in DB queries**: classic SQL/NoSQL injection. Always use parameterized queries.
- **Weak hashing for passwords**: MD5, SHA1, or unsalted SHA-256. Use bcrypt cost ≥12 (or argon2).
- **Hardcoded secrets in source**: API keys, DB passwords in code or git history. Use env vars / secret manager.
- **Stack traces leaking to production responses**: gives attackers a roadmap. Strip in production filter.
- **No rate limiting on `/login`, `/reset-password`, `/signup`**: enables credential stuffing and abuse.
- **No account lockout after N failed attempts**: enables brute-force.
- **CORS `*` with credentials**: trivially defeats same-origin policy.
- **Missing security headers** (no `helmet`): CSP, HSTS, X-Frame-Options, etc.
- **User-controlled URLs fetched server-side without allowlist**: SSRF — internal network exposed.
- **Logging passwords, tokens, or PII**: secrets end up in log aggregation.
- **`eval`, `Function()`, `dangerouslySetInnerHTML`, `innerHTML` with user input**: arbitrary code/XSS.
- **Outdated dependencies with known CVEs**: `npm audit` ignored.
- **No audit log for admin/sensitive actions**: forensics impossible after incident.

---

## Need → Reference

| Need | Reference |
|------|-----------|
| End-to-end review process (4 phases) | `references/review-process.md` |
| OWASP Top 10 with checks + good/bad examples per item | `references/owasp-top-10.md` |
| Pattern → fix quick lookup | `references/quick-reference.md` |
| Output template (findings + OWASP coverage table) | `references/output-template.md` |
| Detailed OWASP per-control checklist | `references/OWASP_CHECKLIST.md` |

---

## Required tooling

- Read, Grep, Glob, Bash (for `npm audit`, `npm outdated`)
- Estimated time: 15-30 min focused review, 1-2 hours full codebase

---

## Referencias externas

- [OWASP Top 10 (2021)](https://owasp.org/www-project-top-ten/)
- [OWASP Cheatsheets](https://cheatsheetseries.owasp.org/)
- [NVD — CVE Database](https://nvd.nist.gov/)
