---
name: sdd-analyze
description: Pre-apply cross-artifact consistency gate for SDD pipeline. Use after sdd-tasks completes, before sdd-apply. Cross-checks proposal/spec/design/tasks for coverage gaps, contradictions, scope leaks, naming drift, and rejected-alternative re-introduction. Inspired by github/spec-kit /speckit.analyze.
version: 1.0
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
source: inspired by github/spec-kit /speckit.analyze
---

# sdd-analyze

Pre-apply consistency gate for the SDD pipeline. Cross-checks the four planning artifacts (`proposal`, `spec`, `design`, `tasks`) for internal coherence BEFORE any implementation begins. Catches drift cheaply — at planning — instead of paying for it after `sdd-apply` lands code that has to be rewritten.

This is the **planning-side companion** to `sdd-verify` (which runs post-impl). `sdd-analyze` blocks bad plans; `sdd-verify` blocks bad code.

## When to use

- **Auto-trigger (recommended)**: After `sdd-tasks` completes in the SDD pipeline, BEFORE `sdd-apply`. Gated by `triage.json.tier`: skip on `trivial`, run on `medium`/`high`/`critical`.
- **Manual**: `Skill('sdd-analyze')` with a change name when you suspect drift between planning artifacts and want a structured report before committing to apply.

## Inputs

Required (FAIL fast if any missing):

- `openspec/changes/<change>/proposal.md`
- `openspec/changes/<change>/spec.md`
- `openspec/changes/<change>/design.md`
- `openspec/changes/<change>/tasks.md`

Optional context:

- `.sdlc/state/<change>/triage.json` (skip if `tier == "trivial"`)

## Checks

Run all six. Each check produces zero or more findings tagged `PASS` / `WARN` / `FAIL`.

### 1. Coverage check (FAIL on miss)

For every `REQ-N` identifier in `spec.md`:
- Grep `tasks.md` for `REQ-N`. If zero matches → **FAIL** (this requirement has no implementation task).
- Record matched task IDs per REQ for the report.

Algorithm:
1. Extract requirement IDs via `Grep` pattern `REQ-\d+` in `spec.md`.
2. For each ID, `Grep` the same pattern in `tasks.md`.
3. Build a `REQ → [task-ids]` map; any empty list → FAIL finding.

### 2. Backref check (WARN on miss)

For every task in `tasks.md`:
- Verify the task body references at least one `REQ-N` from spec.
- A task with no backref is a candidate for either (a) being an infra/setup task (acceptable, but should be tagged) or (b) being out-of-scope work (WARN).

### 3. Contradiction check (WARN, LLM heuristic)

For each `REQ-N` in `spec.md`:
- Pull the requirement statement.
- Read `design.md` sections that reference the same REQ.
- Surface any apparent logical conflict (e.g., spec says "MUST be synchronous", design says "queued via worker").

This is heuristic. Use LLM judgment over `Grep` matches — produce evidence quotes, not just IDs.

### 4. Scope check (FAIL on leak)

Read `proposal.md` "Out of scope" / "Non-goals" section.
- Extract each non-goal as a short phrase.
- `Grep` `spec.md`, `design.md`, `tasks.md` for those phrases.
- Any non-trivial match → **FAIL** (scope leak — out-of-scope work crept in).

### 5. Naming check (WARN on drift)

Extract all file paths mentioned across the four artifacts (regex like `[\w./-]+\.(ts|tsx|py|md|json|yaml)`).
- Compare paths. If `src/foo/bar.ts` appears in one artifact and `src/bar.ts` in another (referring to the same concept) → WARN.
- Compare module/class/function names across artifacts the same way.

### 6. Decision drift (WARN)

Read `design.md` "Alternatives considered" / "Rejected" section.
- For each rejected alternative, extract distinctive keywords.
- `Grep` `tasks.md` for those keywords. Any hit → WARN (a task may be implementing a rejected alternative).

## Output

Write to: `openspec/changes/<change>/analyze-report.md`

Format:

```markdown
# sdd-analyze report — <change>

**Verdict**: PASS | WARN | FAIL
**Date**: <YYYY-MM-DD>
**Triage tier**: <trivial|medium|high|critical>

## Summary
- Coverage: <n>/<total> REQs covered
- Backref: <n>/<total> tasks reference a REQ
- Contradictions: <n>
- Scope leaks: <n>
- Naming drift: <n>
- Decision drift: <n>

## FAIL findings (blocking)
- [Check] [Evidence] → [Suggested fix]

## WARN findings (non-blocking)
- [Check] [Evidence] → [Suggested fix]

## Green-light line
> If PASS: "Plan is internally consistent. Proceed to sdd-apply."
```

## Exit criteria

- Report file written to `openspec/changes/<change>/analyze-report.md`.
- Verdict line communicated to the orchestrator.
- If verdict is `FAIL` or `WARN`, orchestrator MUST surface findings to the user before proceeding to `sdd-apply`.
- `FAIL` → block pipeline; user must revise spec/design/tasks and re-run.
- `WARN` → surface, user explicitly acknowledges, then proceed.
- `PASS` → proceed silently.

## Anti-patterns

- Running `sdd-analyze` without all four artifacts present → emit an error finding and stop. Do NOT generate a half-report.
- Treating `WARN` as `PASS` without user acknowledgment. The orchestrator must pause.
- Modifying any of the four artifacts from this skill. `sdd-analyze` is **read-only over planning artifacts** — it only writes `analyze-report.md`.
- Performing semantic re-design. If a finding requires architectural judgment, surface it; do not silently rewrite design.

## Integration with pipeline (v7.1 gating)

- Invoked between `sdd-tasks` and `sdd-apply` when `triage.json.tier` is `medium`, `high`, or `critical`.
- For `trivial` tier → skip entirely (0% overhead).
- Orchestrator reads `.sdlc/state/<change>/triage.json` to decide.
- Manual override on `/sdd-new`: `--analyze=force` / `--analyze=skip` (mirrors debate/verify flags).

Sequence inside the substantial pipeline:

```
sdd-tasks → [triage gate] → sdd-analyze → [if PASS] → sdd-apply → ...
                                       → [if WARN] → surface → user ack → sdd-apply
                                       → [if FAIL] → halt, surface, user revises
```

## References

- Inspired by github/spec-kit `/speckit.analyze` (https://github.com/github/spec-kit/blob/main/templates/commands/speckit.analyze.md)
- Companion: `sdd-verify` (post-impl version of the same idea)
- Companion: `sdd-verify-diff` (per-file adversarial review, post-apply)
