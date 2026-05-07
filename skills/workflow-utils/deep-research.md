---
name: deep-research
description: "Systematic 4-phase research methodology: Scope → Gather → Synthesize → Deliver. Single source of truth — no /commands wrapper."
invokable: true
accepts_args: true
version: 2.0.0
when:
  keywords: ["research", "investigate", "explore", "compare", "analyze options", "deep-research"]
allowed-tools:
  - WebSearch
  - WebFetch
  - Grep
  - Read
  - Bash(rg *)
  - Bash(fd *)
---

# deep-research

Systematic research for technical and product questions. Use when external source validation is required.

## When to invoke

- New technologies, libraries, or APIs
- Comparing architectural approaches
- Best practices for a domain
- Gathering evidence before recommending
- Any question requiring external source validation

## Phase 1 — Problem Definition

Before searching, write:

```
RESEARCH QUESTION: [exact question]
SCOPE: [in / out of scope]
SUCCESS CRITERIA: [what does a good answer look like?]
KNOWN CONTEXT: [what we already know]
UNKNOWNS: [what specifically needs verification]
```

Do NOT start searching until this is written.

## Phase 2 — Source Discovery

### Priority order
1. **Official documentation** — vendor docs, RFC/PEP
2. **Primary sources** — original papers, GitHub repos, release notes
3. **High-quality secondary** — engineering blogs (Stripe, Netflix, Uber, GitHub)
4. **Community consensus** — Stack Overflow (high vote count), GitHub issues
5. **Benchmarks** — with disclosed methodology

### Methods
```bash
WebSearch("query with current year 2026")
WebFetch(url, "extract [specific information needed]")
Grep("pattern", path)
```

### Source quality checklist
- [ ] Source dated (prefer < 2 years for fast-moving tech)?
- [ ] Author credible (engineer, maintainer, researcher)?
- [ ] Evidence provided (benchmarks, code, examples)?
- [ ] Cross-referenced with 2+ sources?

## Phase 3 — Synthesis

### Findings table

| Question | Answer | Source | Confidence |
|----------|--------|--------|------------|
| [q1] | [answer] | [url/file] | high/medium/low |

### Confidence levels
- **high** — multiple authoritative sources agree
- **medium** — one authoritative source, no primary docs
- **low** — community opinion, no direct evidence, or conflicting

### Conflicts
List contradictions discovered. Explain which source to trust and why.

### Gaps
List what could NOT be verified.

## Phase 4 — Output

```markdown
## Research: [Topic]

### Bottom Line
[Conclusion first — 2-3 sentences max]

### Evidence
[Findings table from Phase 3]

### Recommendation
[Concrete action based on evidence]

### Caveats
[Confidence gaps, conflicting sources, what might change]

### Sources
- [Source 1](url) — [why trusted]
- [Source 2](url) — [why trusted]
```

## Anti-patterns

| Anti-pattern | Correct behavior |
|---|---|
| Searching without a question | Define question first (Phase 1) |
| Trusting single source | Cross-reference 2+ authoritative |
| Fabricating citations | Only cite sources actually fetched |
| Confidence without evidence | Use confidence levels |
| "Typically" / "usually" | Find docs and cite |
| Outdated info | Note pub date, flag if > 2 years |

## Invocation

```
Skill('deep-research') topic="<research question>"
```
