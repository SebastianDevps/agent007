# Security Review Process

## Phase 1: Scope Assessment (5 min)

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

## Phase 2: Automated Scanning (2-3 min)

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

## Phase 3: Manual Code Review

Review against OWASP Top 10 — see `references/owasp-top-10.md`.

## Phase 4: Report Generation

Generate using the template in `references/report-template.md`.

## Checklist: Security Review Complete

Before marking as complete:

- [ ] Automated scans executed
- [ ] OWASP Top 10 manually reviewed
- [ ] Critical findings documented
- [ ] Remediation steps provided
- [ ] Report generated and shared
- [ ] Follow-up review scheduled (if needed)

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
