---
name: search-first
description: "Pre-coding gate — before writing any custom implementation, forces a structured search: library scan, codebase scan, decision matrix. Proceed to Build only if all alternatives are ruled out."
allowed-tools: ["Bash", "Grep", "Glob", "Read", "WebSearch"]
auto-activate: before any "create new" or "implement from scratch" task
version: 1.0.0
when:
  - task_type: feature
  - signal: ["create", "implement", "build", "add", "write a", "new module", "from scratch"]
constraints:
  - check_libraries_before_coding
  - check_codebase_before_coding
  - document_why_custom_if_custom
---

# Search First — Pre-Coding Gate

**Purpose**: Prevent reinventing wheels. `deep-research` is reactive — the user asks for it. This gate fires automatically before any new implementation begins and answers three questions before a single line of production code is written.

**Hard rule**: If the decision is BUILD and no search evidence is documented, the implementation is not allowed to start.

---

## Step 1 — Library Scan

Search the relevant package registry for existing solutions:

- **Node/TypeScript**: `npm search <keyword>` or WebSearch `site:npmjs.com <keyword>`
- **Python**: WebSearch `site:pypi.org <keyword>`
- **Go**: WebSearch `site:pkg.go.dev <keyword>`

Search criteria — a library qualifies as a candidate if it:
- Has active maintenance (last publish < 12 months or activity on repo).
- Has > 100 weekly downloads or > 50 GitHub stars (not abandonware).
- Covers at least 80% of the required behavior.

Document every candidate found. Do not discard candidates without a stated reason.

---

## Step 2 — Codebase Scan

Search the project for existing implementations before adding a new one:

```bash
rg "<keyword>" --type ts -l          # find files mentioning the concept
rg "<keyword>" --type ts -C 3        # see context around matches
```

Look for:
- Utility functions solving the same problem.
- Services or helpers with overlapping responsibility.
- Patterns already established in the codebase that can be extended.

A codebase match means an existing abstraction can be extended or composed instead of rebuilt.

---

## Step 3 — Decision Matrix

Classify the result into one of four outcomes:

| Decision | Meaning | Condition |
|----------|---------|-----------|
| **Adopt** | Use the library as-is | Library covers >= 80% of need, no integration risk |
| **Extend** | Wrap or configure existing code | Library or codebase code covers 60–80%, a thin adapter closes the gap |
| **Compose** | Combine two existing pieces | Two smaller items together solve the problem |
| **Build** | Custom implementation | Nothing found that fits, or fit requires more work than building clean |

**If BUILD**: document what was found and why it does not fit. This is required — not optional. No undocumented custom implementations.

---

## Output Format

Every invocation of this skill ends with a single structured output line before implementation proceeds:

```
SEARCH_RESULT: [Adopt|Extend|Compose|Build]
FOUND: <library name, version — OR — internal file path>
REASON: <why this decision>
```

Examples:

```
SEARCH_RESULT: Adopt
FOUND: zod@3.22.4
REASON: Covers schema validation with TypeScript inference. Already in package.json.

SEARCH_RESULT: Build
FOUND: joi@17 (too heavy, pulls 12 deps), yup@1 (API doesn't support discriminated unions)
REASON: Neither library supports the discriminated union validation pattern required. Custom validator is ~30 lines and has zero deps.

SEARCH_RESULT: Extend
FOUND: src/shared/http/base-client.ts
REASON: Existing HTTP client covers auth injection; need to add retry logic only.
```

---

## Anti-Patterns — Reject Immediately

| Signal | Action |
|--------|--------|
| "I'll just write it quickly" | STOP — run the scan first |
| No SEARCH_RESULT line in output | STOP — gate not satisfied; do not write implementation |
| BUILD decision with no FOUND evidence | STOP — document what was searched |
| Library found but dismissed without reason | STOP — state the rejection reason explicitly |
| Codebase already has a helper; new one added anyway | STOP — extend or compose the existing one |

---

## Integration with Pipeline

This gate runs between routing and `Skill('generate')`:

```
routing → search-first → [Adopt/Extend/Compose: integrate] OR [Build: generate → verify]
```

For SDD flows, the SEARCH_RESULT is included in the proposal artifact so the design phase knows whether a library or existing code was chosen.
