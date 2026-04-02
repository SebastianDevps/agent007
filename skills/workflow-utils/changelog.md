---
name: changelog
description: "Generate structured changelog from git history. Groups commits by type, filters noise, produces Keep a Changelog format."
invokable: true
accepts_args: true
version: 1.0.0
when:
  keywords: ["changelog", "release notes", "what changed", "history"]
---

# Changelog — Structured Release Notes Generator

## What It Does

Generates a formatted changelog by reading git history and grouping commits by type following the Agent007 pipe-delimited format (`Tipo|IdTarea|YYYYMMDD|Desc`).

## Output Format

Follows [Keep a Changelog](https://keepachangelog.com) v1.0.0:

```markdown
## [version] — YYYY-MM-DD

### Added
- feat|...|Description

### Fixed
- fix|...|Description

### Changed
- refactor|...|Description

### Removed
- (removed features)
```

## Protocol

### Step 1 — Determine scope

```bash
git log --oneline <base>..<head>
```

If no base provided, default to last tag or last 20 commits.

### Step 2 — Parse and group

Group commits by Tipo:
- `feat` → Added
- `fix` → Fixed
- `refactor` / `perf` → Changed
- `docs` → Documentation
- `test` / `chore` / `ci` → (omit from user-facing changelog unless requested)

### Step 3 — Format and deliver

Output the changelog section. Ask if user wants to write it to `CHANGELOG.md`.

## Invocation

```
Skill('changelog') [version=X.Y.Z] [since=<tag-or-sha>]
```
