# /security-scan — Agent007 Security Audit

Local-only scan of the Agent007 ecosystem for configuration weaknesses and
potential prompt injection vulnerabilities.

**All analysis is local — no data is sent externally.**

---

## Usage

```
/security-scan                    # full scan, human-readable report
/security-scan --category <1-5>   # scan only one category
/security-scan --json             # machine-readable output
```

---

## Categories

| # | Target | What it checks |
|---|--------|---------------|
| 1 | `CLAUDE.md` | Safety-bypass phrases: "ignore safety", "bypass guard", "override constraint" |
| 2 | `settings.json` | `permissions.deny` covers `rm -rf /` and `sudo`; no over-permissive `Bash(*)` |
| 3 | `hooks/` | No `eval()`, no unsafe `exec()` with user input, no external `curl` |
| 4 | `skills/` | No prompt-injection patterns ("ignore previous instructions", instruction tags) |
| 5 | `instincts/` | No instinct with confidence > 0.9 (flags unexpected auto-apply elevation) |

---

## Step 1 — Run the scanner

```bash
node .claude/scripts/security-scan.js
```

## Step 2 — Parse results

Report format:
```
Score: [A-F]  |  [N] critical  [N] warnings  [N] clean categories

✅ [1] CLAUDE.md — safety bypass phrases
⚠️  [2] settings.json — permissions.deny coverage
    WARNING  permissions.deny missing protection for: sudo
🚨 [4] skills/ — prompt injection patterns
    CRITICAL Potential prompt injection: "ignore previous instructions"
             → .claude/skills/pipeline/some-skill.md
```

## Step 3 — Act on findings

| Grade | Meaning | Action |
|-------|---------|--------|
| A | All clean | No action needed |
| B | Minor warnings | Review and confirm intentional |
| C | Warnings or 1 critical | Fix before next session |
| D | Multiple criticals | Fix immediately |
| F | 3+ criticals | Stop and audit manually |

**On CRITICAL issues**:
1. Open the flagged file
2. Remove or replace the offending content
3. Re-run `/security-scan` to confirm resolution

---

## Scoring Reference

```
A  →  0 issues
B  →  1-2 warnings
C  →  3-4 warnings  OR  1 critical
D  →  5+ warnings   OR  2 criticals
F  →  3+ criticals
```

Exit code: `0` for grade A/B, `1` for C–F.
