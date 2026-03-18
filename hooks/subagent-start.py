#!/usr/bin/env python3
"""
SubagentStart Hook — Skill Registry Injection
Injects compressed skill registry into every subagent's context.

WHY THIS EXISTS:
Empirical research (ai-framework/Dario-Arcos) measured that subagents
invoked applicable skills in only 53% of cases when skills were merely
documented. When the skill registry is injected passively into context,
invocation rate rises to ~100%.

Law 1 of Context Engineering: Passive > Active.
"""

import json
import sys

# Agent007 compressed skill registry for subagents
SKILL_REGISTRY = """
## Available Skills — invoke via Skill tool

### Workflow
- Build/fix feature:  Skill("scenario-driven-development") → Skill("verification-before-completion")
- Bug:                Skill("systematic-debugging") → Skill("scenario-driven-development") → Skill("verification-before-completion")
- Research:           Skill("deep-research")
- Plan (complex):     Skill("brainstorming") → Skill("writing-plans") → Skill("subagent-driven-development")
- Git commit:         Skill("commit")
- PR:                 Skill("pull-request")
- Changelog:          Skill("changelog")
- Branch cleanup:     Skill("branch-cleanup")
- New skill:          Skill("skill-creator")
- Humanize output:    Skill("humanizer")

### SOP Pipeline (complex multi-task features)
- Discover patterns:  Skill("sop-discovery")
- Plan SOP:           Skill("sop-planning") (planning + task generation combined)
- Execute task:       Skill("sop-code-assist")
- Review SDD:         Skill("sop-reviewer")
- Reverse engineer:   Skill("sop-reverse")

### Domain / Expert
- UI work:            Skill("frontend-design") before any implementation
- NestJS API:         Skill("api-design-principles")
- Architecture:       Skill("architecture-patterns")
- Security audit:     Skill("security-review")
- Resilience:         Skill("resilience-patterns")
- React/Next:         Skill("react-best-practices")
- NestJS review:      Skill("nestjs-code-reviewer")
- Product:            Skill("product-discovery")
- API docs:           Skill("api-documentation")
- Architecture deep:  Skill("architecture-review")

### Quality Gates
- Completion claim:   MUST invoke Skill("verification-before-completion") first
- Code quality:       Skill("requesting-code-review")

## Banned Phrases (self-correct immediately)
- "should work" → "verified working — evidence: [command] → [output]"
- "probably" → "confirmed by testing"
- "might" → "tested and confirmed"
- "I assume" → "I verified by reading [file]"
"""

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        # If no valid JSON, still inject the registry
        input_data = {}

    output = {
        "hookSpecificOutput": {
            "additionalContext": SKILL_REGISTRY.strip()
        }
    }

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
