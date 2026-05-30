---
name: retrospective
description: "Close the feedback loop after a change ships. Capture intent vs outcome, surprises, process learnings, and reusable patterns. Writes per-change retrospectives and aggregates monthly digests so institutional knowledge accumulates instead of evaporating."
allowed-tools: ["Read", "Write", "Bash", "Glob"]
auto-activate: suggested by sdd-archive at change close
version: 1.0.0
when:
  - command: Skill('retrospective')
  - phase: post-sdd-archive
---

# retrospective — Post-Change Lessons Capture (v7.2 Ola 35)

**Purpose**: Most teams ship and move on. Lessons stay in heads. This skill makes the lesson-capture step a formal output — a markdown file in `.sdlc/retrospectives/` that persists to git and surfaces in future reviews.

**Trigger keywords (manual)**: `retro`, `retrospective`, `post-mortem`, `lessons learned`, `what did we learn`.
**Auto-suggest**: `sdd-archive` recommends invoking this skill at change close (does not auto-run — the user controls whether to invest the time).

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `change_name` | string | no | SDD change identifier. If absent, asks user. |
| `archive_ref` | string | no | Path/topic_key to archive report |

---

## Workflow

### Phase 1 — Load archive context

1. If `change_name` is provided:
   - `Read` `.sdlc/state/<change_name>/archive-report.md` to load context.
   - Fallback: `Read` `openspec/changes/<change_name>/archive-report.md`.
2. Extract: original intent (from proposal), final outcome (from archive), task list, verify report status.
3. If no archive exists, ask user to summarize the change in 2-3 sentences.

### Phase 2 — Five questions (one at a time)

Drive a structured Q&A. Ask each question, wait for the answer, then proceed. Do NOT dump all five at once.

1. **Intent** — "What did we promise to deliver?" (Pre-fill from proposal if available; user confirms or edits.)
2. **Outcome** — "What did we actually deliver?" (Pre-fill from archive if available.)
3. **Surprises** — "What surprised us? Positive or negative — anything that diverged from expectation."
4. **Differently** — "If we did this again from scratch, what would we change about the process?"
5. **Pattern** — "What pattern emerged here that's worth saving for next time? Name it, describe it in one paragraph."

The fifth answer becomes the reusable pattern entry in the retrospective file. It is the most important question — if the user gives a shallow answer (e.g., "nothing"), re-prompt once: "Even a small reusable convention counts — a file layout, a naming rule, an error-handling shortcut. Anything?"

### Phase 3 — Write the per-change retrospective

Path: `.sdlc/retrospectives/<YYYY-MM>-<change_name>.md`

Template:
```markdown
# Retrospective — <change_name>

**Date:** YYYY-MM-DD
**Change:** <change_name>
**Status:** shipped | partial | abandoned

## Intent
<answer 1>

## Outcome
<answer 2>

## Surprises
<answer 3>

## What we'd do differently
<answer 4>

## Pattern emerged
**Name:** <short name>
**Description:** <paragraph>
**Reusable for:** <when this pattern applies>
```

### Phase 4 — Persist pattern

The pattern (answer 5) is saved alongside the retrospective file for future reference.
No external backend is required — the markdown file is the source of truth.
The pattern is visible in the per-change retrospective at `.sdlc/retrospectives/<YYYY-MM>-<change_name>.md`
and aggregated into the monthly digest at `.sdlc/retrospectives/<YYYY-MM>-digest.md`.

### Phase 5 — Monthly aggregation (conditional)

At end of month (when today is the last day of the month OR user passes `--digest`):

1. `Glob` `.sdlc/retrospectives/<YYYY-MM>-*.md` (excluding existing digest).
2. For each, extract the "Pattern emerged" block.
3. Write `.sdlc/retrospectives/<YYYY-MM>-digest.md`:
   ```markdown
   # Monthly Retrospective Digest — YYYY-MM

   ## Patterns emerged this month
   - **<pattern name>** (from <change>): <one-line summary>
   - ...

   ## Recurring themes
   <if 2+ patterns share keywords, group them here>
   ```
4. Digest is persisted to `.sdlc/retrospectives/<YYYY-MM>-digest.md`. No external backend required.

### Phase 6 — Emit envelope

Return `SubagentResponseV1`:
- `status`: `success`
- `executive_summary`: "Retrospective captured for <change>. Pattern: <name>."
- `artifacts`: `[{ path, topic_key }]`
- `next_recommended`: "Run `Skill('retrospective --digest')` at month-end to aggregate."
- `risks`: `[]`
- `skill_resolution`: `injected | fallback-*`

---

## Example invocations

```
Skill('retrospective')
  change_name: "auth-refactor-2026-05"

Skill('retrospective --digest')   # forces monthly aggregation now

Skill('retrospective')            # asks user for change name + context
```

---

## Honest limits

- Quality of the retrospective is entirely a function of the user's engagement. Shallow answers produce shallow files. The skill cannot inject depth.
- The monthly digest is text-aggregation, not semantic clustering. "Recurring themes" detection is keyword-overlap only.
- Quarterly themes do NOT have an automated rollup — they emerge from reviewing `Glob('.sdlc/retrospectives/<YYYY-Q*>-*.md')` when someone looks.
- Auto-suggestion from `sdd-archive` is a recommendation, not enforcement. Users can skip retrospectives. The trade-off (lost learning) accumulates silently.

---

## See also

- `.sdlc/retrospectives/README.md` — directory purpose
- `Skill('sdd-archive')` — predecessor; closes the change record
