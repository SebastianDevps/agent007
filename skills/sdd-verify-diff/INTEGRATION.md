# sdd-verify-diff — Orchestrator Integration Contract

Contract for wiring `sdd-verify-diff` (v7.1 P3) into the SDD pipeline. Sibling document to `sdd-debate/INTEGRATION.md` — same conventions.

---

## 1. Detection

After `sdd-apply` returns, the orchestrator reads:

```
.sdlc/state/<change-name>/triage.json
```

The relevant field is `per_diff_verify_required` (boolean, set by the P0 `debate-trigger.py` Guide).

| `triage_tier` | `per_diff_verify_required` | Action |
|---|---|---|
| `trivial` | false | Skip sdd-verify-diff. Run only sdd-verify-meta. |
| `medium` | false | Skip sdd-verify-diff. Run only sdd-verify-meta. |
| `high` | true | Invoke sdd-verify-diff AFTER sdd-verify-meta. |

If `triage.json` is missing (defensive default): treat as `medium` and skip per-diff verify.

**This skill SUPPLEMENTS `sdd-verify-meta` — it does NOT replace it.** Meta-level review always runs; per-diff fan-out is conditional on the gate.

---

## 2. Invocation

```
Skill('sdd-verify-diff', {
  change_name: "<change>",
  tier: "high",
  files_override: [...]   # optional — usually omitted, skill auto-resolves
})
```

Skill internally:
1. Resolves modified files (priority: `files_override` → `apply-progress.json` → git diff → staged diff).
2. Persists each diff to `.sdlc/state/<change>/diffs/<sanitized-path>.diff`.
3. Spawns `code-reviewer` subagents IN PARALLEL via the Task tool (one per diff, adversarial mode).
4. Aggregates SubagentResponseV1 envelopes via `_aggregator.aggregate_reviews(...)`.
5. Writes `.sdlc/state/<change>/verify-diff-report.json`.

---

## 3. Verdict dispatch

After the skill returns, the orchestrator reads the verdict from the returned envelope OR from `.sdlc/state/<change>/verify-diff-report.json`:

### `clean`
- Action: proceed to `sdd-archive` normally.
- User notification: brief — "Per-diff verify clean across N files."

### `findings`
- Action: proceed to `sdd-archive`, but surface findings to the user as a WARNING.
- The warning includes `findings_by_severity` counts and the list of `review_refs` so the user can drill into any single file's report.
- The pipeline does NOT halt — non-blocking findings (med/low) are informational.

### `blocked`
- Action: **HALT the SDD pipeline. DO NOT run sdd-archive.**
- Emit escalation to user. The escalation must include:
  - The `blocking_findings` list (each with file_path, severity, claim, review_ref).
  - The `findings_by_severity` rollup.
  - A prompt: "Address blocking findings, then re-run sdd-apply, or override with explicit user approval."
- The orchestrator pauses the SDD pipeline until the user responds.

---

## 4. Iteration-budget interaction (P2)

`sdd-verify-diff` is a single SDD phase from the iteration-budget Sentinel's perspective. The Sentinel sees the skill's envelope:

- `status=done` + verdict in (`clean`, `findings`) → normal flow.
- `status=done` + verdict=`blocked` → no auto-retry; user resolves blocking findings.
- `status=partial` → Sentinel may re-invoke if budget remains (rare — skill aggregates whatever envelopes it received).
- `status=blocked` → no auto-retry; escalate.

The fan-out across N code-reviewer subagents happens INSIDE the skill and consumes NO iteration-budget invocations for `sdd-verify-diff` itself. Only re-invocations of the skill as a whole count.

---

## 5. File-based artifacts

All artifacts are written to `.sdlc/state/<change>/`:

| Artifact | Location |
|---|---|
| Per-file diffs | `.sdlc/state/<change>/diffs/<sanitized-path>.diff` |
| Per-file review reports | `.sdlc/state/<change>/reviews/<sanitized-path>-review.json` |
| Aggregate report | `.sdlc/state/<change>/verify-diff-report.json` |

`<sanitized-path>` replaces `/` with `__` so the filename is filesystem-safe and reversible.

When `triage_tier` is `trivial` or `medium`, none of these artifacts are written.

---

## 6. Failure modes

| Failure | Behavior |
|---|---|
| Modified-files list resolves to empty | Skill returns `status=done`, verdict=`clean`, `files_reviewed=0`. Orchestrator proceeds to sdd-archive. |
| One code-reviewer subagent returns an error | Aggregator processes remaining envelopes. Skill emits `status=partial`, reason="reviewer-failed:N", includes the partial report. Iteration-budget Sentinel decides retry. |
| All code-reviewer subagents fail | Skill emits `status=blocked`, reason="all-reviewers-failed". NO auto-retry. |
| `_aggregator` raises | Skill emits `status=blocked` with error details. NO auto-retry. |
| Sensitive-path file in diff list | Reviewer still runs (its adversarial framing already covers this). The high tier itself is the gate. |

---

## 7. Pipeline ordering

```
sdd-apply → sdd-verify-meta → [if per_diff_verify_required] sdd-verify-diff → sdd-archive
```

- `sdd-verify-meta` validates against the spec. If it blocks, `sdd-verify-diff` does NOT run.
- `sdd-verify-diff` only runs when meta passes AND the gate is open.
- Both must produce passing verdicts before `sdd-archive`.

---

## 8. What this Ola does NOT change

This Ola (Ola 17) ships ONLY the skill + the aggregator module + tests. It does NOT:
- Modify the orchestrator's CLAUDE.md routing (deferred to a follow-up Ola).
- Update `settings.json` hook registration.
- Touch `triage-paths.toml` or `iteration-budget.toml`.
- Modify the `sdd-verify` agent definition.
- Modify the `code-reviewer` agent definition.

The orchestrator wire-up is the next Ola's responsibility, after this skill is verified in isolation against the test fixtures.
