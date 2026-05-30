---
name: changelog
description: "Generate structured changelog from git history. Groups commits by type, filters noise, produces Keep a Changelog format. Single source of truth — no /commands wrapper."
version: 2.0.0
when:
  keywords: ["changelog", "release notes", "what changed", "history"]
allowed-tools:
  - Bash(git log *)
  - Bash(git tag *)
  - Read
  - Edit
  - Write
---

# changelog

Generate a release changelog by reading git history and organizing by Agent007 commit type.

## When to invoke

- Preparing a release
- User asks "what changed since last release?"
- After completing a multi-task feature branch

## Step 1 — Determine scope

```bash
git tag --sort=-creatordate | head -5      # Latest tags
git log --oneline <last-tag>..HEAD          # Commits since last release
```

If no tags:
```bash
git log --oneline -30
```

## Step 2 — Parse and group

Group by Agent007 type (`Tipo|IdTarea|YYYYMMDD|Desc`):

| Tipo | Changelog section |
|------|-------------------|
| `feat` | ### Added |
| `fix` | ### Fixed |
| `refactor`, `perf` | ### Changed |
| `docs` | ### Documentation |
| `revert` | ### Reverted |
| `test`, `chore`, `ci`, `build` | (omit unless `--all`) |

## Step 3 — Format output

Follows [Keep a Changelog](https://keepachangelog.com) v1.0.0:

```markdown
## [version] — YYYY-MM-DD

### Added
- Implement user authentication with JWT refresh rotation

### Fixed
- Resolve null pointer in UserService.findById when email missing

### Changed
- Optimize bulk insert queries — 3x performance improvement
```

## Step 4 — Write (optional)

Ask: "¿Escribo esto en `CHANGELOG.md`?"

If yes:
- Prepend new section above existing content
- NEVER overwrite existing entries

## Flags

| Flag | Effect |
|------|--------|
| `--all` | Include test/chore/ci/build commits |
| `--since <tag-or-sha>` | Custom start point |
| `--version X.Y.Z` | Use specific version header |

## Invocation

```
Skill('changelog') [version=X.Y.Z] [since=<tag-or-sha>]
```
