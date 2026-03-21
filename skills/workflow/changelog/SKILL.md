---
name: changelog
description: "Generate structured changelogs from git history following Keep a Changelog format."
invokable: true
version: 1.0.0
---

# changelog

> Generate structured changelogs from git history. Ported from ai-framework (Dario-Arcos).

---

## When to invoke

- Preparing a release
- User asks for "changelog", "release notes", "what changed"

---

## Step 1 — Determine range

```bash
# From last tag to HEAD
git describe --tags --abbrev=0    # latest tag
git log v1.2.3..HEAD --oneline   # commits since tag

# Or from specific date
git log --since="2026-01-01" --oneline
```

---

## Step 2 — Categorize commits

Commits follow the pipe-delimited standard: `Tipo|IdTarea|YYYYMMDD|Descripción`
Extract the `Tipo` from the first pipe segment:

```bash
git log v1.2.3..HEAD --format="%s" | awk -F'|' '{print $1}' | sort | uniq -c
```

Categories:
- **Breaking Changes** — manual annotation in body or footer
- **New Features** — `feat` commits
- **Bug Fixes** — `fix` commits
- **Performance** — `perf` commits (if used)
- **Other** — `refactor`, `docs`, `chore`, `test`, `review`

---

## Step 3 — Draft changelog

```markdown
## [version] — YYYY-MM-DD

### Breaking Changes
- **auth**: JWT token format changed — clients must update token parsing

### New Features
- **users**: Add bulk import via CSV upload
- **api**: Rate limiting with configurable per-route thresholds

### Bug Fixes
- **payments**: Fix race condition in concurrent payment processing
- **auth**: Resolve refresh token expiry miscalculation

### Performance
- **db**: Add index on users.email — 80% query speedup

### Internal
- Update dependencies (no user-facing changes)
```

---

## Step 4 — Apply humanizer

Invoke `humanizer` on the draft to remove AI writing patterns.

---

## Step 5 — Save

```bash
# Prepend to CHANGELOG.md
# Or create release notes file
```

---

## Version determination

| Change type | Version bump |
|------------|-------------|
| BREAKING CHANGE | MAJOR (x.0.0) |
| feat | MINOR (0.x.0) |
| fix, perf, refactor | PATCH (0.0.x) |
