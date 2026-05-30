---
name: adr-write
description: "Author an Architecture Decision Record (ADR). Captures decisions with implications beyond the current change — lasts months, affects multiple files, hard to reverse. Records context, alternatives considered, consequences, and aging signals so the decision can be revisited when conditions change."
allowed-tools: ["Read", "Write", "Bash", "Glob"]
auto-activate: when sdd-design risk-level == high
version: 1.0.0
when:
  - command: Skill('adr-write')
  - phase: post-sdd-design (auto when risk-level=high)
---

# adr-write — Architecture Decision Record Author (v7.2 Ola 35)

**Purpose**: Persist an architectural decision that outlives the current change. ADRs are the project's institutional memory — when someone asks "why are we using X?" six months later, the answer lives here, not in a Slack thread.

**Trigger keywords (manual)**: `adr`, `architecture decision`, `decision record`, `record decision`.
**Auto-trigger**: `sdd-design` invokes this skill when the design phase yields `risk-level=high` (touches auth, payments, data model, public API, or other sensitive paths).

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | yes | Short decision title (will become slug) |
| `context_ref` | string | no | Topic key or path to proposal/design (if invoked from SDD) |
| `decision_question` | string | yes (if no context_ref) | Free-form question being decided |
| `risk_level` | `low` \| `medium` \| `high` | no | From SDD triage. Defaults to medium when manual. |

---

## Workflow

### Phase 1 — Gather context

If `context_ref` is provided:
1. Resolve via `Read` the referenced file path (e.g., `openspec/changes/<change>/design.md` or `.sdlc/state/<change>/design.md`).
2. Extract: problem statement, constraints, options considered.

If only `decision_question` is provided:
1. Drive a short structured Q&A with the user — one question at a time:
   - What problem are we solving?
   - What are the forces / constraints at play?
   - What options did you consider?
   - Why did you reject the alternatives?
   - What changes if this decision turns out wrong in 6 months?

### Phase 2 — Compute next ADR number

1. List `.sdlc/adrs/*.md` via `Glob`.
2. Extract numeric prefixes (`ADR-001`, `ADR-002`, ...).
3. Next number = `max(existing) + 1`, zero-padded to 3 digits. If empty → `001`.

### Phase 3 — Draft ADR body

Use this template verbatim. Fill every section — no `TBD` placeholders.

```markdown
# ADR-NNN — <title>

**Date:** YYYY-MM-DD
**Status:** proposed
**Supersedes:** ADR-XXX (if applicable; omit line otherwise)
**Superseded by:** (filled later if this gets replaced)

## Context
What problem are we solving? What forces are at play?
- Force 1: ...
- Force 2: ...

## Decision
What did we choose? State it as an imperative: "We will use X because Y."

## Alternatives considered
- **A: <name>** — Rejected because: ...
- **B: <name>** — Rejected because: ...
- **C: <name>** — Rejected because: ...

## Consequences
**Easier:**
- ...

**Harder:**
- ...

**New risks:**
- ...

## Aging signals
Triggers that would cause us to revisit this decision:
- If <condition> — e.g., "user base exceeds 10k", "p95 latency >500ms", "we add multi-region"
- If <condition>
- If <condition>
```

### Phase 4 — Write to disk

1. Slug = lowercase title, replace non-alphanumeric with `-`, strip duplicates.
2. Path = `.sdlc/adrs/ADR-NNN-<slug>.md`.
3. `Write` the file. The markdown file is the source of truth — no external backend required.
4. If this ADR supersedes another:
   - Edit the old ADR file: change `Status: accepted` → `Status: superseded`, fill `Superseded by: ADR-NNN — <title>` field.

### Phase 5 — Emit envelope

Return `SubagentResponseV1`:
- `status`: `success`
- `executive_summary`: "ADR-NNN created: <title>. Status: proposed. Path: <path>."
- `artifacts`: `[{ path, topic_key }]`
- `next_recommended`: "Discuss with team. Update status to `accepted` after sign-off."
- `risks`: `[]`
- `skill_resolution`: `injected | fallback-*`

---

## Auto-invocation from sdd-design

When `sdd-design` finishes with `risk-level=high`:
1. Orchestrator reads design output.
2. Detects high-risk decision points (typically 1–3 per design).
3. For each, invokes `Skill('adr-write')` with the decision title + `context_ref` pointing to the design.
4. ADRs become artifacts of the SDD change, listed alongside the spec/design/tasks.

---

## Example invocations

```
Skill('adr-write')
  title: "Use JWT refresh-token rotation"
  decision_question: "How do we handle session longevity vs. security trade-off?"

Skill('adr-write')
  title: "Adopt PostgreSQL over MongoDB"
  context_ref: "sdd/auth-refactor/design"
  risk_level: high
```

---

## Honest limits

- ADRs only capture decisions you remember to record. There is no detector for "you just made an architectural decision without writing it down".
- Aging signals are user-defined. The skill does not validate they are measurable — `"if it feels wrong"` is accepted (but discouraged).
- Superseding requires the user to know which prior ADR is being replaced. The skill does NOT auto-detect conflicts with existing ADRs (`adr-review` is the periodic safety net).

---

## See also

- `../adr-review/SKILL.md` — periodic check for aging ADRs
- `.sdlc/adrs/README.md` — directory purpose
