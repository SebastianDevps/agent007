---
name: deep-research
version: 1.0
description: "Systematic 4-phase research methodology for technical and product questions."
accepts_args: true
---

# deep-research

> Systematic 4-phase research methodology for technical and product questions. Ported from ai-framework (Dario-Arcos).

---

## When to invoke

- Researching new technologies, libraries, or APIs
- Comparing architectural approaches
- Understanding best practices for a domain
- Gathering evidence before making recommendations
- Any question requiring external source validation

---

## Phase 1 — Problem Definition

Before searching, state precisely:

```
RESEARCH QUESTION: [exact question to answer]
SCOPE: [what's in / out of scope]
SUCCESS CRITERIA: [what does a good answer look like?]
KNOWN CONTEXT: [what do we already know?]
UNKNOWNS: [what specifically needs verification?]
```

Do NOT start searching until this is written.

---

## Phase 2 — Source Discovery

### Priority order for sources:

1. **Official documentation** — vendor docs, spec files, RFC/PEP/BEP
2. **Primary sources** — original papers, GitHub repos, release notes
3. **High-quality secondary** — well-known engineering blogs (Stripe, Netflix, Uber, GitHub)
4. **Community consensus** — Stack Overflow (high vote counts), GitHub issues
5. **Benchmarks** — with methodology disclosed

### Retrieval methods:

```bash
# Use WebSearch for current information
WebSearch("query with current year 2026")

# Use WebFetch for specific pages
WebFetch(url, "extract [specific information needed]")

# Use Grep/Read for local codebase
Grep("pattern", path)
```

### Source quality checklist:
- [ ] Source dated? (prefer < 2 years old for fast-moving tech)
- [ ] Author credible? (company engineer, maintainer, researcher)
- [ ] Evidence provided? (benchmarks, code, examples)
- [ ] Consensus or outlier? (cross-reference with 2+ sources)

---

## Phase 3 — Synthesis

Organize findings into a structured report:

### Findings table

| Question | Answer | Source | Confidence |
|----------|--------|--------|------------|
| [q1] | [answer] | [url/file] | high/medium/low |
| [q2] | [answer] | [url/file] | high/medium/low |

### Confidence levels:
- **high** — multiple authoritative sources agree
- **medium** — one authoritative source or consensus without primary docs
- **low** — community opinion, no direct evidence, or conflicting sources

### Conflicting findings:
List any contradictions discovered and explain which source to trust and why.

### Gaps:
List what could NOT be verified and what additional research would clarify it.

---

## Phase 4 — Output

Structure the final output as:

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
- [Source 1](url) — [why it was trusted]
- [Source 2](url) — [why it was trusted]
```

After output, invoke `humanizer` if producing user-facing content.

---

## Anti-patterns

| Anti-pattern | Correct behavior |
|---|---|
| Searching without a question | Define research question first (Phase 1) |
| Trusting single source | Cross-reference minimum 2 authoritative sources |
| Fabricating citations | Only cite sources actually fetched and read |
| Claiming confidence without evidence | Use confidence levels table |
| "Typically" / "usually" | Find the actual documentation and cite it |
| Outdated information | Note publication date, flag if > 2 years old |
