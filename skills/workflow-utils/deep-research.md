---
name: deep-research
description: "4-phase systematic research methodology: Scope → Gather → Synthesize → Deliver. For technical investigations, library comparisons, architecture decisions."
invokable: true
accepts_args: true
version: 1.0.0
when:
  keywords: ["research", "investigate", "explore", "compare", "analyze options", "deep-research"]
---

# Deep Research — 4-Phase Systematic Research

Delegates to the `/deep-research` command. See `.claude/commands/deep-research.md` for the full protocol.

## 4 Phases

### Phase 1 — Scope
Define the research question precisely. Identify: what we need to know, what we already know, success criteria for the research.

### Phase 2 — Gather
Systematic collection from multiple sources:
- Official docs
- GitHub issues / discussions
- Benchmarks / empirical data
- Known trade-offs / anti-patterns

### Phase 3 — Synthesize
Cross-reference sources. Resolve contradictions. Apply to our specific context (stack, constraints, team).

### Phase 4 — Deliver
Structured output:
- Executive summary (1 paragraph)
- Recommendation with rationale
- Trade-offs considered
- Sources with confidence level

## Invocation

```
Skill('deep-research') topic="<research question>"
```
