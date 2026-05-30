---
name: sdd-checklist
description: Spec-completeness gate for the SDD pipeline. Use after sdd-spec, before sdd-design. Validates the SPEC ITSELF — observable, unambiguous, bounded, testable requirements with scenarios that trace to REQs. Inspired by github/spec-kit /speckit.checklist.
version: 1.0
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
source: inspired by github/spec-kit /speckit.checklist
---

# sdd-checklist

"Unit tests for English requirements." After `sdd-spec` writes a spec, this skill validates the SPEC ITSELF for completeness and clarity — BEFORE `sdd-design` builds architecture on top of it. Catches ambiguity, untestable wording, and scenario gaps at the cheapest possible moment.

This is the **intra-spec gate**. It does NOT cross-check artifacts (that is `sdd-analyze`'s job, post-tasks). It only inspects `spec.md` for self-coherence.

## When to use

- **Auto-trigger (recommended)**: After `sdd-spec` completes, BEFORE `sdd-design`. Gated by `triage.json.tier`: skip on `trivial`, run on `medium`/`high`/`critical`.
- **Manual**: `Skill('sdd-checklist')` with a change name to audit a spec before design work begins.
- **Pipeline position**: Orthogonal to `sdd-analyze`. Checklist runs early on a single artifact; analyze runs late across four artifacts.

## Inputs

Required (FAIL fast if missing):

- `openspec/changes/<change>/spec.md`

Optional context:

- `openspec/changes/<change>/proposal.md` — for "out of scope" cross-check
- `.sdlc/state/<change>/triage.json` — skip if `tier == "trivial"`

## Checks

Run all three groups. Each finding tagged `PASS` / `WARN` / `FAIL`.

### Per `REQ-N`

Extract every `REQ-N` identifier in `spec.md` via `Grep` pattern `REQ-\d+`. For each one:

1. **Observable** (FAIL on miss) — Does the REQ describe behavior an external observer can witness? Reject "the system should be performant", accept "p95 latency < 200ms under 100 concurrent users".
2. **Unambiguous** (FAIL on miss) — Could two readers disagree on what it means? Flag weasel words: *appropriate*, *reasonable*, *should*, *typically*, *good*, *fast*, *secure*. Demand a measurable replacement.
3. **Bounded** (WARN on miss) — Are the in-scope and out-of-scope edges clear? A REQ that ends "...and related features" is unbounded.
4. **Testable** (FAIL on miss) — Can at least one Given/When/Then scenario be written for it? If no concrete trigger exists, it is not testable.
5. **Has scenarios** (FAIL on miss) — Grep `spec.md` for a scenario referencing this REQ. Zero matches → FAIL (orphan requirement).

### Per acceptance scenario

Find every Given/When/Then block in `spec.md`. For each:

1. **Structure** (FAIL on miss) — Are Given, When, Then all present? Missing any → FAIL.
2. **Concrete When** (FAIL on miss) — Is the When step a user action or system event? Reject "the system is configured correctly", "the user is authenticated" (those are Given). Accept "the user clicks Submit", "the cron fires at 03:00".
3. **Observable Then** (FAIL on miss) — Is the Then step externally observable (HTTP response, DB row, log line, UI state)? Reject "the internal flag is set", "the cache is warm".
4. **Traces to a REQ** (WARN on miss) — Does the scenario name a `REQ-N`? Orphan scenarios are not blocking but signal drift.

### Spec-wide

1. **Orphan REQs** (FAIL) — Aggregate count of REQs with zero scenarios.
2. **Orphan scenarios** (WARN) — Aggregate count of scenarios not tied to any REQ.
3. **Out-of-scope explicit** (WARN on miss) — Does `spec.md` (or `proposal.md`) contain a "Non-goals" / "Out of scope" section? If absent → WARN.
4. **Dependencies stated** (WARN on miss) — If the change depends on another change or external system, is there a "Dependencies" section? If absent and proposal mentions a prerequisite → WARN.

## Output

Write to: `openspec/changes/<change>/checklist-report.md`

Format:

```markdown
# sdd-checklist report — <change>

**Verdict**: PASS | WARN | FAIL
**Date**: <YYYY-MM-DD>
**Triage tier**: <trivial|medium|high|critical>

## Summary
- REQs evaluated: <n>
- Scenarios evaluated: <n>
- FAIL findings: <n>
- WARN findings: <n>

## Per-REQ results

| REQ | Observable | Unambiguous | Bounded | Testable | Has scenarios |
|-----|------------|-------------|---------|----------|---------------|
| REQ-1 | PASS | FAIL ("appropriately") | PASS | PASS | PASS |
| ... | ... | ... | ... | ... | ... |

## Per-scenario issues
- [scenario excerpt] → [issue] → [suggested fix]

## Spec-wide findings
- [finding] → [suggested fix]

## Suggested fixes (FAIL items)
- [REQ or scenario] → [concrete rewrite suggestion]

## Green-light line
> If PASS: "Spec is complete and testable. Proceed to sdd-design."
```

## Exit criteria

- Report file written to `openspec/changes/<change>/checklist-report.md`.
- Verdict line communicated to the orchestrator.
- `FAIL` → halt pipeline; user must revise `spec.md` and re-run.
- `WARN` → surface findings, user explicitly acknowledges, then proceed.
- `PASS` → proceed silently to `sdd-design`.

## Anti-patterns

- Running without `spec.md` → emit error and stop. Do NOT generate a half-report.
- Critiquing the DESIGN or IMPLEMENTATION. This skill inspects requirements wording only. Architecture quality is `sdd-design`'s and `sdd-analyze`'s concern.
- Rewriting `spec.md` from this skill. Checklist is **read-only over spec.md** — it only writes `checklist-report.md` with suggestions.
- Accepting weasel words because "context makes it obvious". If a reader needs context outside the spec to disambiguate, the spec is ambiguous.

## Relationship to other SDD skills

```
sdd-spec → [sdd-checklist] → sdd-design → ... → sdd-tasks → [sdd-analyze] → sdd-apply → [sdd-verify-diff] → sdd-verify → sdd-archive
              ^                                                  ^                                              ^
              intra-spec gate                                    cross-artifact gate                            post-impl gate
```

- `sdd-checklist` validates one artifact (`spec.md`) early. Cheapest to fix.
- `sdd-analyze` validates four artifacts together late in planning. Catches drift across phases.
- `sdd-verify` validates code against spec post-implementation.

The three are complementary, not redundant. Each fails on a different class of defect.

## References

- Inspired by github/spec-kit `/speckit.checklist` (https://github.com/github/spec-kit/blob/main/templates/commands/speckit.checklist.md)
- Companion: `sdd-analyze` (cross-artifact, post-tasks)
- Companion: `sdd-verify` (post-implementation)
