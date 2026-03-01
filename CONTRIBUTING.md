# Contributing to Agent007

Thank you for your interest in contributing to Agent007! This document provides guidelines for contributing to the project.

## 🚀 Quick Start

1. **Fork the repository** and clone your fork
2. **Read the documentation** in `.claude/CLAUDE.md` to understand the architecture
3. **Check existing issues** or create a new one to discuss your contribution
4. **Make your changes** following the guidelines below
5. **Submit a pull request** with a clear description

## 📋 Contribution Areas

### 1. Skills Development
- Create new skills for specific workflows
- Improve existing skills with better prompts or patterns
- Add reference materials to skills using `references/` directory

### 2. Agent Enhancement
- Improve agent prompts and methodologies
- Add new expert agents for different domains
- Enhance agent selection logic in orchestrator

### 3. Documentation
- Improve README and setup guides
- Add examples and use cases
- Write tutorials or walkthroughs

### 4. Quality & Testing
- Add validation scripts
- Improve test coverage
- Report bugs or edge cases

## 🛠️ Development Guidelines

### Skill Development Standards

When creating or modifying skills, follow the **Frontmatter Standard**:

```yaml
---
name: skill-name              # kebab-case, required
description: "..."            # Include trigger phrases, required
version: X.Y.Z                # Semver, required
invokable: true/false         # User can call directly?, required
accepts_args: true/false      # Accepts arguments?, optional
allowed-tools: [...]          # Tool restrictions, optional
when:                         # Auto-activation conditions, optional
  - task_type: [...]
    risk_level: [...]
---
```

**Description Requirements**:
- Must include "Use when user asks to..." trigger phrases
- Should clearly explain what the skill does
- Keep it concise (1-3 sentences)

**File Organization**:
- Skills >600 lines: Use `references/` for lookup tables, checklists, examples
- Keep behavioral instructions in main `SKILL.md`
- Add `SUMMARY.md` (50 lines) for large skills

### Validation Before Submitting

Run validation scripts:
```bash
node .claude/scripts/validate-frontmatter.js
```

Ensure:
- ✅ YAML frontmatter parses correctly
- ✅ All required fields present
- ✅ No duplicate skill names
- ✅ File size reasonable (<1500 lines)

### Commit Message Format

Use conventional commits:
```
type(scope): brief description

Longer description if needed

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Types**: feat, fix, docs, refactor, test, chore

## 🧪 Testing

### Manual Testing Checklist

When adding/modifying skills:
1. Test that skill activates correctly with trigger phrases
2. Verify integration with related skills (sub-skills, transitions)
3. Check that `allowed-tools` restrictions work
4. Test edge cases and error handling

### Behavioral Testing

Document test cases in `.claude/skills/TEST_SUITE.md`:
```markdown
## Test: [Skill Name] Auto-Activation
**Input**: "[User prompt]"
**Expected**: [Expected behavior]
**Actual**: [PASS/FAIL]
```

## 📝 Pull Request Process

1. **Create a descriptive PR title**
   - Good: "feat(skills): Add security-review skill with OWASP checklist"
   - Bad: "Update files"

2. **Describe your changes**
   - What problem does this solve?
   - How does it work?
   - Any breaking changes?

3. **Link related issues**
   - Use "Fixes #123" or "Relates to #456"

4. **Request review**
   - Tag relevant maintainers
   - Be responsive to feedback

## 🎯 Skill Development Guide

### Creating a New Skill

1. **Choose the right location**:
   ```
   .claude/skills/
   ├── _core/              # Quality enforcement (verification, anti-rationalization)
   ├── _orchestration/     # Session orchestration
   ├── workflow/           # Development workflows (brainstorming, TDD, planning)
   ├── quality-gates/      # Quality checks (debugging, architecture review)
   ├── product/            # Product management
   ├── devrel/             # Developer relations
   └── [domain]/           # Domain-specific (api-design, frontend-design, etc.)
   ```

2. **Use the template**:
   ```markdown
   ---
   name: my-skill
   description: "Brief description. Use when user asks to 'keyword1' or 'keyword2'."
   version: 1.0.0
   invokable: true
   ---
   
   # Skill Name - Brief Title
   
   **Purpose**: What this skill does
   
   **When to use**: Conditions for activation
   
   ## Process
   
   [Step-by-step workflow]
   
   ## Output
   
   [What this skill produces]
   
   ## Integration
   
   [How this connects to other skills]
   ```

3. **Test thoroughly** before submitting

### Extending Existing Skills

1. Read the skill completely first
2. Understand its purpose and integration points
3. Make minimal changes - avoid scope creep
4. Test that existing functionality still works
5. Update version number (semver)

## ❓ Questions?

- **General questions**: Open a GitHub Discussion
- **Bug reports**: Create an issue with reproduction steps
- **Feature requests**: Create an issue describing the use case
- **Security issues**: Email security@agent007.dev (if applicable)

## 📜 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Assume good intentions

## 🎉 Recognition

Contributors will be:
- Listed in CHANGELOG.md for each release
- Credited in commit messages (Co-Authored-By)
- Mentioned in release notes for significant contributions

Thank you for contributing to Agent007!
