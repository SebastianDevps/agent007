---
name: changelog
version: 1.0
description: "Generate structured changelog from git history following Keep a Changelog format"
accepts_args: true
---

# changelog

> Generate a release changelog by reading git commit history and organizing by type.

---

## When to invoke

- When preparing a release
- When the user asks "what changed since last release?"
- After completing a multi-task feature branch

---

## Step 1 — Determine scope

```bash
git tag --sort=-creatordate | head -5   # Find latest tags
git log --oneline <last-tag>..HEAD      # Commits since last release
```

If no tags exist, use last 30 commits:
```bash
git log --oneline -30
```

---

## Step 2 — Parse commits

Group by Agent007 commit type (`Tipo|IdTarea|YYYYMMDD|Desc`):

| Tipo | Changelog Section |
|------|------------------|
| `feat` | ### Added |
| `fix` | ### Fixed |
| `refactor`, `perf` | ### Changed |
| `docs` | ### Documentation |
| `test`, `chore`, `ci`, `build` | (omit from user-facing unless `--all` flag) |
| `revert` | ### Reverted |

---

## Step 3 — Format output

```markdown
## [version] — YYYY-MM-DD

### Added
- Implement user authentication with JWT refresh rotation

### Fixed
- Resolve null pointer in UserService.findById when email missing

### Changed
- Optimize bulk insert queries — 3x performance improvement
```

---

## Step 4 — Write to file (optional)

Ask the user: "¿Escribo esto en `CHANGELOG.md`?"

If yes:
- Prepend the new section above existing content
- Never overwrite existing changelog entries

---

## Flags

| Flag | Effect |
|------|--------|
| `--all` | Include test/chore/ci commits |
| `--since <tag-or-sha>` | Custom start point |
| `--version X.Y.Z` | Use specific version header |
