# Quick Reference: Common Vulnerabilities

| Vulnerability | Pattern to Search | Fix |
|---------------|-------------------|-----|
| SQL Injection | `.query(.*+.*)` | Use parameterized queries |
| XSS | `innerHTML\|dangerouslySetInnerHTML` | Sanitize input, use templates |
| Hardcoded secrets | `password.*=\|api_key.*=` | Use environment variables |
| Weak crypto | `md5\|sha1` | Use bcrypt for passwords, SHA-256+ for hashing |
| Missing auth | Routes without `@UseGuards` | Add authentication guards |
| IDOR | Direct DB access without ownership check | Validate user owns resource |
