#!/usr/bin/env python3
"""
subagent-context.py — SubagentStart Hook: Full Context Injection

Injects into every subagent's context:
  1. Relevant skills registry (v6 naming — Ola-25)
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


def read_active_prompt(project_root):
    """Inject /prompt-gen v4 spec into the subagent (if fresh).

    Reads .sdlc/state/active-prompt.json. Honors the spec's ttl_seconds
    (default 7200 = 2h). Returns formatted block or "" if absent/expired/invalid.
    """
    path = os.path.join(project_root, ".sdlc", "state", "active-prompt.json")
    if not os.path.exists(path):
        return ""
    try:
        import time
        from datetime import datetime, timezone
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        ts_raw = data.get("generated_at", "")
        if not ts_raw:
            return ""
        try:
            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00")).timestamp()
        except (ValueError, TypeError):
            return ""
        ttl = int(data.get("ttl_seconds", 7200))
        if time.time() - ts > ttl:
            return ""
        spec = data.get("spec_xml", "")
        if not spec or len(spec) > 4000:
            spec = (spec or "")[:4000]
        target = data.get("target", "?")
        tier = data.get("tier", "?")
        # P4 cache fix: drop visible `Generated: {ts_raw}` from rendered block.
        # ts_raw is still validated above for TTL freshness; it must not appear
        # in the injected bytes because it rotates per session and would
        # invalidate the prompt cache on every subagent launch.
        return (
            f"\n## Active Prompt Spec (from /prompt-gen v4)\n\n"
            f"Target: {target} · Tier: {tier}\n\n"
            f"```xml\n{spec}\n```"
        )
    except (OSError, ValueError, json.JSONDecodeError):
        return ""


# ---------------------------------------------------------------------------
# Skill registry (v6 naming — Ola-25)
# ---------------------------------------------------------------------------

SKILL_REGISTRY = """
## Available Skills — invoke via Skill('name')

### Pipeline (development flow)
- Skill('brainstorming')                    → Socratic requirements exploration (medium/complex features)
- Skill('plan')                            → Decompose to 2-5min tasks with exact paths + TDD steps
- Skill('generate')                        → Execute single task: RED→GREEN→REFACTOR + commit
- Skill('verify')                          → Two-pass verification: evidence gate + SDD compliance
- Skill('tdd-workflow')                    → Red-Green-Refactor gate: failing test REQUIRED before any implementation
- Skill('subagent-driven-development')     → Dispatch expert subagents per task from plan (wave execution)
- Skill('using-git-worktrees')             → Isolated branch via git worktree
- Skill('finishing-a-development-branch')  → Close branch: verify → merge/PR/keep/discard
- Skill('sop-reverse')                     → Reverse-engineer existing code before refactoring

### Domain / Expert
- Skill('domain-api-design-principles')        → NestJS REST API design and audit
- Skill('domain-architecture-patterns')        → Clean Architecture, DDD, Bounded Contexts
- Skill('domain-resilience-patterns')          → Circuit breakers, retry, health checks
- Skill('domain-nestjs-code-reviewer')         → NestJS + TypeORM code review + OWASP
- Skill('domain-security-review')              → OWASP Top 10, auth, authorization, sensitive data
- Skill('domain-react-best-practices')         → React/Next.js optimization and best practices
- Skill('domain-frontend-design')              → High-quality UI/UX design and implementation
- Skill('domain-gsap')                         → GSAP animations: tweens, timelines, ScrollTrigger, React integration
- Skill('domain-discovery-before-code')        → Pre-implementation discovery: search libs + codebase first
- Skill('domain-shadcn-component-install')     → shadcn/ui component installation and customization
- Skill('domain-a11y-contrast-check')          → Accessibility contrast and WCAG compliance checks
- Skill('domain-design-tokens-extract')        → Extract and manage design tokens from Figma/CSS
- Skill('domain-design-system-doc')            → Document design system components and patterns
- Skill('domain-page-transitions-barba')       → Page transitions with Barba.js
- Skill('domain-ios-hig-mobile')               → iOS Human Interface Guidelines for mobile UI
- Skill('domain-spline-3d-embed')              → Embed and optimize Spline 3D scenes in web
- Skill('domain-behavioral-contracts')         → Define and validate agent behavioral contracts

### Quality Gates
- Skill('quality-gates-systematic-debugging')  → Root-cause analysis: reproduce → isolate → fix → verify
- Skill('sdd-analyze')                         → Cross-artifact contradiction detection before apply
- Skill('sdd-checklist')                       → Spec completeness check before design
- Skill('agent-self-diagnosis')                → 4-phase loop recovery (fires at 3 repeated calls with no progress)

### Workflow Utilities
- Skill('commit')              → Pipe-delimited commit: Tipo|IdTarea|YYYYMMDD|Desc
- Skill('pull-request')        → Create structured GitHub PRs
- Skill('changelog')           → Generate changelog from git history
- Skill('deep-research')       → 4-phase systematic research methodology
- Skill('search-first')        → Pre-coding gate: scan libs + codebase → Adopt/Extend/Compose/Build
- Skill('rules-distill')       → Scan skills for repeated principles → elevate to rules/ (with approval)
- Skill('skill-stocktake')     → Automated skill audit: Keep/Improve/Retire/Merge

### Standard Workflows
- Build/fix feature:  Skill('tdd-workflow') → Skill('generate') → Skill('verify')
- Complex feature:    Skill('brainstorming') → Skill('using-git-worktrees') → Skill('plan') → Skill('subagent-driven-development')
- Bug fix:            Skill('quality-gates-systematic-debugging') → Skill('generate') → Skill('verify')
- Refactor:           Skill('sop-reverse') → Skill('plan') → Skill('generate') → Skill('verify')
- Before any custom code: Skill('search-first')
- Completion gate:    ALWAYS invoke Skill('verify') before claiming done
- Loop detected:      Skill('agent-self-diagnosis') at 3+ repeated calls
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


# ---------------------------------------------------------------------------
# Apply-phase response convention
# ---------------------------------------------------------------------------

APPLY_RESPONSE_CONVENTION = """
## Apply-Phase Response Convention

When you are dispatched as a **writing specialist** during the SDD apply phase, you MUST:

**1. Write verbose output to apply-progress.md**
Append your working output (implementation details, reasoning, commands run, evidence) to:
`openspec/changes/<change-name>/apply-progress.md`

Section format:
```
## <your-agent-name> · <ISO-8601 timestamp> · attempt <n>
<verbose working output>
---
```
Create the file if it does not exist. NEVER overwrite existing content — append only.

**2. Return a short envelope as your final response**
Your final response MUST be a JSON code block with these fields:

Required always:
- `status`: "done" | "partial" | "blocked" | "needs_specialist"
- `file_changes`: int (number of files modified)
- `summary`: string ≤ 240 chars (one sentence)
- `artifact_ref`: "file:openspec/changes/<change-name>/apply-progress.md"

Required when status ≠ "done":
- `error_class`: "transient" | "permanent" | "unknown"
- `verdict`: "PASS" | "WARN" | "FAIL"
- `failure_signature`: deterministic string (failing test names / rule IDs / error hashes)
- `recommended_specialist`: agent name (only when status = "needs_specialist")

**Exemption**: If `file_changes == 0` (read-only work), you are exempt from the apply-progress requirement. Return the short envelope only.
"""


def main() -> None:
    try:
        sys.stdin.read()  # consume input JSON
    except Exception:
        pass

    project_root = _find_project_root()

    # P2 cache fix: assemble STABLE sections first (cacheable prefix), then
    # DYNAMIC sections last (cache-busting tail). Anything that varies between
    # subagent launches (task-spec by mtime, active-prompt by session) must
    # come AFTER the stable bytes so the prefix can be reused across calls.
    #
    # Order:
    #   STABLE prefix:
    #     1. SKILL_REGISTRY
    #     2. .sdlc/context/* files
    #     3. MASTER_GUIDE.md
    #     4. BANNED_PHRASES
    #     5. APPLY_RESPONSE_CONVENTION
    #   --- implicit cache boundary ---
    #   DYNAMIC tail:
    #     6. Current task spec (selected by mtime — rotates)
    #     7. Active prompt spec (per-session XML — rotates)

    stable_sections = []

    # Inject behavioral contracts (always-on identity).
    # Read fresh from disk — never hardcode, single source of truth lives in
    # .claude/contracts/behavioral-contracts.md so CLAUDE.md and this hook stay in sync.
    contracts_path = os.path.join(project_root, ".claude", "contracts", "behavioral-contracts.md")
    contracts_content = read_file_safe(contracts_path, max_chars=2000)
    if contracts_content:
        stable_sections.append(contracts_content)

    stable_sections.append(SKILL_REGISTRY.strip())

    # Inject .sdlc/context/ files (stable per release)
    context_dir = os.path.join(project_root, ".sdlc", "context")
    context_files = [
        ("Tech Stack", os.path.join(context_dir, "tech-stack.md")),
        ("Conventions", os.path.join(context_dir, "conventions.md")),
        ("Project Overview", os.path.join(context_dir, "project-overview.md")),
    ]
    for label, path in context_files:
        content = read_file_safe(path, max_chars=1500)
        if content:
            stable_sections.append(f"\n## {label}\n\n{content}")

    # Inject MASTER_GUIDE.md conventions (stable per release)
    master_guide = os.path.join(project_root, "MASTER_GUIDE.md")
    if os.path.exists(master_guide):
        content = read_file_safe(master_guide, max_chars=1500)
        if content:
            stable_sections.append(f"\n## MASTER_GUIDE.md (summary)\n\n{content}")

    # Inject banned phrases (stable per script edit)
    stable_sections.append(BANNED_PHRASES.strip())

    # Inject apply-phase response convention (stable per script edit)
    stable_sections.append(APPLY_RESPONSE_CONVENTION.strip())

    # ---- DYNAMIC TAIL (must come last to preserve cacheable prefix) ----
    dynamic_sections = []

    # Inject current task spec (selected by mtime — changes per invocation)
    task_spec = find_current_task_spec(project_root)
    if task_spec:
        dynamic_sections.append(task_spec)

    # Inject active prompt-spec (per-session XML)
    active_prompt = read_active_prompt(project_root)
    if active_prompt:
        dynamic_sections.append(active_prompt)

    sections = stable_sections + dynamic_sections
    full_context = "\n\n---\n\n".join(sections)

    output = {
        "hookSpecificOutput": {
            "hookEventName": "SubagentStart",
            "additionalContext": full_context
        }
    }

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
