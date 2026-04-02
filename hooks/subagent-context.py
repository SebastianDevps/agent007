#!/usr/bin/env python3
"""
subagent-context.py — SubagentStart Hook: Full Context Injection

Injects into every subagent's context:
  1. Relevant skills registry (v5 naming)
  2. .sdlc/context/ files (tech-stack, conventions, project-overview)
  3. Current task spec (docs/changes/*/tasks.md if present)
  4. MASTER_GUIDE.md conventions summary
  5. Banned phrases list

WHY THIS EXISTS:
Empirical research (ai-framework/Dario-Arcos) measured that subagents
invoked applicable skills in only 53% of cases when skills were merely
documented. When the skill registry is injected passively into context,
invocation rate rises to ~100%.

Law 1 of Context Engineering: Passive > Active.
"""

import json
import os
import sys
from pathlib import Path


def _find_project_root() -> str:
    """Walk up from cwd to find the Agent007 project root."""
    current = os.getcwd()
    while current != os.path.dirname(current):
        if os.path.isdir(os.path.join(current, ".claude")):
            return current
        current = os.path.dirname(current)
    return os.getcwd()


def read_file_safe(path: str, max_chars: int = 3000) -> str:
    """Read a file safely, truncating to max_chars."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(max_chars)
        if len(content) == max_chars:
            content += "\n[... truncated for context budget ...]"
        return content
    except (OSError, UnicodeDecodeError):
        return ""


def find_current_task_spec(project_root: str) -> str:
    """Find the most recently modified task spec file."""
    docs_changes = os.path.join(project_root, "docs", "changes")
    if not os.path.isdir(docs_changes):
        return ""

    task_files = []
    for root, _, files in os.walk(docs_changes):
        for fname in files:
            if fname in ("tasks.md", "spec.md"):
                full = os.path.join(root, fname)
                task_files.append((os.path.getmtime(full), full))

    if not task_files:
        return ""

    task_files.sort(reverse=True)
    latest = task_files[0][1]
    content = read_file_safe(latest, max_chars=2000)
    if content:
        return f"\n## Current Task Spec ({os.path.relpath(latest, project_root)})\n\n{content}"
    return ""


# ---------------------------------------------------------------------------
# Skill registry (v5 naming)
# ---------------------------------------------------------------------------

SKILL_REGISTRY = """
## Available Skills — invoke via Skill('name')

### Pipeline (development flow)
- Skill('brainstorming')                    → Socratic requirements exploration (medium/complex features)
- Skill('plan')                            → Decompose to 2-5min tasks with exact paths + TDD steps
- Skill('generate')                        → Execute single task: RED→GREEN→REFACTOR + commit
- Skill('verify')                          → Two-pass verification: evidence gate + SDD compliance
- Skill('subagent-driven-development')     → Dispatch expert subagents per task from plan
- Skill('using-git-worktrees')             → Isolated branch via git worktree
- Skill('finishing-a-development-branch')  → Close branch: verify → merge/PR/keep/discard
- Skill('reverse-engineer')                → Reverse-engineer existing code before refactoring

### Domain / Expert
- Skill('api-design-principles')   → NestJS REST API design and audit
- Skill('architecture-patterns')   → Clean Architecture, DDD, Bounded Contexts
- Skill('resilience-patterns')     → Circuit breakers, retry, health checks
- Skill('nestjs-code-reviewer')    → NestJS + TypeORM code review + OWASP
- Skill('security-review')         → OWASP Top 10, auth, authorization, sensitive data
- Skill('react-best-practices')    → React/Next.js optimization and best practices
- Skill('frontend-design')         → High-quality UI/UX design and implementation

### Workflow Utilities
- Skill('commit')              → Pipe-delimited commit: Tipo|IdTarea|YYYYMMDD|Desc
- Skill('pull-request')        → Create structured GitHub PRs
- Skill('changelog')           → Generate changelog from git history
- Skill('deep-research')       → 4-phase systematic research methodology

### Standard Workflows
- Build/fix feature:  Skill('generate') → Skill('verify')
- Complex feature:    Skill('brainstorming') → Skill('using-git-worktrees') → Skill('plan') → Skill('subagent-driven-development')
- Bug fix:            Skill('generate') → Skill('verify')
- Refactor:           Skill('reverse-engineer') → Skill('plan') → Skill('generate') → Skill('verify')
- Completion gate:    ALWAYS invoke Skill('verify') before claiming done
"""

# ---------------------------------------------------------------------------
# Banned phrases (quick reference)
# ---------------------------------------------------------------------------

BANNED_PHRASES = """
## Banned Phrases — self-correct immediately

| Banned | Required replacement |
|--------|---------------------|
| "should work" | "verified working — evidence: [cmd] → [output]" |
| "probably" | "confirmed by testing: [cmd] → [output]" |
| "might work" | "tested and confirmed: [evidence]" |
| "I assume" | "I verified by reading [file:line]" |
| "seems correct" | "confirmed: [specific behavior tested]" |
| "looks good" | "reviewed [file:line] — no issues found" |
| "typically" | "confirmed in [file/test/docs]" |
"""


def main() -> None:
    try:
        sys.stdin.read()  # consume input JSON
    except Exception:
        pass

    project_root = _find_project_root()

    sections = [SKILL_REGISTRY.strip()]

    # Inject .sdlc/context/ files
    context_dir = os.path.join(project_root, ".sdlc", "context")
    context_files = [
        ("Tech Stack", os.path.join(context_dir, "tech-stack.md")),
        ("Conventions", os.path.join(context_dir, "conventions.md")),
        ("Project Overview", os.path.join(context_dir, "project-overview.md")),
    ]
    for label, path in context_files:
        content = read_file_safe(path, max_chars=1500)
        if content:
            sections.append(f"\n## {label}\n\n{content}")

    # Inject current task spec
    task_spec = find_current_task_spec(project_root)
    if task_spec:
        sections.append(task_spec)

    # Inject MASTER_GUIDE.md conventions (summary section)
    master_guide = os.path.join(project_root, "MASTER_GUIDE.md")
    if os.path.exists(master_guide):
        content = read_file_safe(master_guide, max_chars=1500)
        if content:
            sections.append(f"\n## MASTER_GUIDE.md (summary)\n\n{content}")

    # Inject banned phrases
    sections.append(BANNED_PHRASES.strip())

    full_context = "\n\n---\n\n".join(sections)

    output = {
        "hookSpecificOutput": {
            "additionalContext": full_context
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
