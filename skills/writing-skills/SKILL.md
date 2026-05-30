---
name: writing-skills
description: Use when creating new skills, editing existing skills, or verifying skills work before deployment
---

# Writing Skills

## Overview

**Writing skills IS Test-Driven Development applied to process documentation.**

Personal skills live in agent-specific directories (`~/.claude/skills` for Claude Code). Project skills live under `.claude/skills/<name>/SKILL.md`.

You write test cases (pressure scenarios with subagents), watch them fail (baseline behavior), write the skill (documentation), watch tests pass (agents comply), and refactor (close loopholes).

**Core principle:** If you didn't watch an agent fail without the skill, you don't know if the skill teaches the right thing.

**REQUIRED BACKGROUND:** You MUST understand the standard test-driven-development cycle before using this skill. That cycle defines RED→GREEN→REFACTOR; this skill adapts it to documentation.

## What is a Skill?

A **skill** is a reference guide for proven techniques, patterns, or tools. Skills help future Claude instances find and apply effective approaches.

**Skills are:** Reusable techniques, patterns, tools, reference guides

**Skills are NOT:** Narratives about how you solved a problem once

## TDD Mapping for Skills

| TDD Concept | Skill Creation |
|-------------|----------------|
| **Test case** | Pressure scenario with subagent |
| **Production code** | Skill document (SKILL.md) |
| **Test fails (RED)** | Agent violates rule without skill (baseline) |
| **Test passes (GREEN)** | Agent complies with skill present |
| **Refactor** | Close loopholes while maintaining compliance |
| **Write test first** | Run baseline scenario BEFORE writing skill |
| **Watch it fail** | Document exact rationalizations agent uses |
| **Minimal code** | Write skill addressing those specific violations |
| **Watch it pass** | Verify agent now complies |
| **Refactor cycle** | Find new rationalizations → plug → re-verify |

The entire skill creation process follows RED→GREEN→REFACTOR.

## When to Create a Skill

**Create when:**
- Technique wasn't intuitively obvious to you
- You'd reference this again across projects
- Pattern applies broadly (not project-specific)
- Others would benefit

**Don't create for:**
- One-off solutions
- Standard practices well-documented elsewhere
- Project-specific conventions (put in CLAUDE.md)
- Mechanical constraints (if it's enforceable with regex/validation, automate it — save documentation for judgment calls)

## Skill Types

- **Technique** — concrete method with steps (e.g. `condition-based-waiting`, `root-cause-tracing`)
- **Pattern** — way of thinking about a class of problems (e.g. `flatten-with-flags`, `test-invariants`)
- **Reference** — API docs, syntax guides, tool documentation

## Directory Structure

```
skills/
  skill-name/
    SKILL.md              # Main reference (required)
    references/           # Heavy reference, only if needed
    supporting-file.*     # Reusable tool, only if needed
```

**Flat namespace** — all skills in one searchable namespace.

**Separate files for:**
1. **Heavy reference** (100+ lines) — API docs, comprehensive syntax
2. **Reusable tools** — scripts, utilities, templates

**Keep inline:**
- Principles and concepts
- Code patterns (< 50 lines)
- Everything else

## SKILL.md Structure

**Frontmatter (YAML):**
- Two required fields: `name` and `description` (see [agentskills.io/specification](https://agentskills.io/specification) for all supported fields)
- Max 1024 characters total
- `name`: letters, numbers, and hyphens only (no parentheses, special chars)
- `description`: Third-person, describes ONLY when to use (NOT what it does)
  - Start with "Use when..." to focus on triggering conditions
  - Include specific symptoms, situations, and contexts
  - **NEVER summarize the skill's process or workflow**
  - Keep under 500 characters if possible

```markdown
---
name: Skill-Name-With-Hyphens
description: Use when [specific triggering conditions and symptoms]
---

# Skill Name

## Overview
What is this? Core principle in 1-2 sentences.

## When to Use
[Small inline flowchart IF decision non-obvious]
Bullet list with SYMPTOMS and use cases. When NOT to use.

## Core Pattern (for techniques/patterns)
Before/after code comparison.

## Quick Reference
Table or bullets for scanning common operations.

## Implementation
Inline code for simple patterns. Link to file for heavy reference or reusable tools.

## Common Mistakes
What goes wrong + fixes.

## Real-World Impact (optional)
Concrete results.
```

## The Iron Law (Same as TDD)

```
NO SKILL WITHOUT A FAILING TEST FIRST
```

This applies to NEW skills AND EDITS to existing skills.

Write skill before testing? Delete it. Start over.
Edit skill without testing? Same violation.

**No exceptions:**
- Not for "simple additions"
- Not for "just adding a section"
- Not for "documentation updates"
- Don't keep untested changes as "reference"
- Don't "adapt" while running tests
- Delete means delete

**REQUIRED BACKGROUND:** the standard test-driven-development cycle explains why this matters. Same principles apply to documentation.

## Deep-Dive References

Load these only when you reach the matching phase — they are NOT auto-included.

- `references/cso-and-naming.md` — Description writing, keyword coverage, naming, token efficiency, cross-referencing other skills. Load when authoring frontmatter or naming a skill.
- `references/flowcharts-examples-organization.md` — When to use a flowchart, how to write a single excellent code example, file-organization patterns, anti-patterns. Load when laying out the skill body.
- `references/testing-and-bulletproofing.md` — Per-skill-type test approach, rationalization tables, red-flag lists, RED→GREEN→REFACTOR protocol, deployment checklist. Load when running the TDD cycle on the skill.

## STOP: Before Moving to Next Skill

After writing ANY skill, you MUST STOP and run the testing + deployment loop documented in `references/testing-and-bulletproofing.md`. Do NOT batch-create skills.

Deploying untested skills = deploying untested code.
