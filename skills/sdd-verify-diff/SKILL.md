---
name: sdd-verify-diff
description: "Per-diff adversarial verify (v7.1 P3). When triage tier is high, fans out one code-reviewer subagent per modified file with clean context. Each diff is reviewed adversarially. Aggregates SubagentResponseV1 envelopes into a single verdict: clean | findings | blocked. Supplements sdd-verify-meta — does NOT replace it."
allowed-tools: ["Task", "Read", "Write", "Bash"]
auto-activate: when triage.json.per_diff_verify_required == true after sdd-apply completes
version: 1.0.0
when:
  - phase: post-sdd-apply
  - triage_tier: [high]
---

# sdd-verify-diff — Per-Diff Adversarial Verify (v7.1 P3)

**Purpose**: Close the v7.1 trilogy. Whole-task review (the existing `sdd-verify`) loses small-scope issues when a change touches multiple files. This skill splits the verify phase by file: each diff gets its own clean-context adversarial reviewer.

**Trigger**: Orchestrator detects `triage.json.per_diff_verify_required == true` AND the apply phase completed (changes exist on disk or in `apply-progress.json`).

**Relationship to `sdd-verify`**:
- `sdd-verify-meta` (current `sdd-verify` agent, scoped) — task-level: did the implementation satisfy the spec?
- `sdd-verify-diff` (this skill) — fan-out: one adversarial review per modified file.

This skill does NOT contain review logic. It dispatches `code-reviewer` (P0 agent, emits SubagentResponseV1) in adversarial mode for each diff and aggregates results via `_aggregator.py`.

**Skill text stays minimal — aggregation logic lives in `_aggregator.py`.**

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `change_name` | string | yes | The SDD change identifier (used for file organization) |
| `files_override` | list[string] | no | Explicit file list (testing / replays). If absent, skill auto-resolves. |
| `tier` | `high` | yes | From `triage.json.triage_tier`. Skill is NOT invoked for trivial/medium. |

---

## Workflow

### Phase 1 — Resolve modified files

The skill determines which files to review using this priority order:

1. **`files_override` argument** — caller passed an explicit list.
2. **`.sdlc/state/<change>/apply-progress.json`** — read the `files_touched` field written by `sdd-apply`.
3. **Git diff** — if git is available and a `base_ref` is known: `git diff --name-only <base_ref>..HEAD`. Default base: `main`.
4. **Staged diff fallback** — `git diff --name-only --cached` when nothing else resolves.

If after all four steps the list is empty, the skill emits `status=done`, verdict=`clean`, `files_reviewed=0`, and exits. There is nothing to review.

Generated files (`dist/`, `node_modules/`, `*.generated.*`, `migrations/`) are filtered out — same convention as `code-reviewer`.

### Phase 2 — Persist diffs

For each modified file, compute its diff:

- `git diff <base_ref>..HEAD -- <file>` when git is available
- Otherwise read the file's full content as the "diff" body (degraded mode)

Persist to:

```
.sdlc/state/<change>/diffs/<sanitized-path>.diff
```

`<sanitized-path>` replaces `/` with `__`, e.g. `src__auth__user.service.ts.diff`. This is deterministic (same path → same filename).

### Phase 3 — Fan-out (parallel adversarial reviews)

For each diff, spawn the `code-reviewer` subagent IN PARALLEL via the Task tool. The prompt passed to each subagent contains:

1. **Adversarial framing** (verbatim):
   > "You are running in ADVERSARIAL review mode. Assume this diff is broken. Find what is wrong. Be ruthless but stay above 80% confidence — false positives waste cycles."
2. **The diff content** — read from `.sdlc/state/<change>/diffs/<sanitized-path>.diff`.
3. **The relevant spec excerpt** — read from `openspec/changes/<change>/spec.md` (orchestrator passes the file path or pre-materialized content).
4. **File-based persistence directive**: subagent MUST persist its full report to `.sdlc/state/<change>/reviews/<sanitized-path>-review.json`.

**All `code-reviewer` invocations MUST be launched in the same orchestrator turn** so they run with clean, independent contexts.

Each `code-reviewer` returns a SubagentResponseV1 envelope (per its existing contract — see `.claude/agents/code-reviewer.md`).

### Phase 4 — Aggregate

Call `_aggregator.aggregate_reviews(change_name, review_envelopes)`. The module:

1. Parses each SubagentResponseV1 envelope.
2. Extracts findings from each artifact body (or from `executive_summary` when artifact body is absent in degraded mode).
3. Computes `finding_id = sha1(file_path + "::" + claim)[:12]` — same convention as P1.
4. Deduplicates findings with identical `finding_id`, keeping the highest severity.
5. Maps `code-reviewer` severities into the aggregate scale:
   - `CRITICAL` → `high`, `blocking=true`
   - `HIGH` → `high`, `blocking=true`
   - `MEDIUM` → `med`, `blocking=false`
   - `LOW` → `low`, `blocking=false`
6. Derives the verdict mechanically (see § Verdict logic).

### Phase 5 — Persist report

Write the aggregate report to:

```
.sdlc/state/<change>/verify-diff-report.json
```

Shape:

```json
{
  "ts": "2026-05-11T...",
  "change": "<name>",
  "files_reviewed": N,
  "findings_by_severity": {"high": N, "med": N, "low": N},
  "blocking_findings": [
    {"finding_id": "...", "file_path": "...", "severity": "high", "blocking": true, "claim": "...", "review_ref": ".sdlc/state/<change>/reviews/<sanitized-path>-review.json"}
  ],
  "review_refs": [".sdlc/state/<change>/reviews/<path>-review.json", ...],
  "verdict": "clean | findings | blocked",
  "elapsed_ms": N
}
```

### Phase 6 — Exit verdict

The skill returns one of three verdicts (mirrored from the report):

| Verdict | Meaning | Orchestrator action (see INTEGRATION.md) |
|---|---|---|
| `clean` | Zero findings across all diffs | proceed to `sdd-archive` |
| `findings` | Non-blocking findings only (med/low) | proceed but surface as warning |
| `blocked` | At least one blocking (CRITICAL/HIGH) finding | HALT pipeline, surface to user, do NOT archive |

---

## Mode by tier

| Tier | This skill runs? |
|---|---|
| `trivial` | NO — gated by P0 triage |
| `medium` | NO — gated by P0 triage |
| `high` | YES — full fan-out |

The orchestrator is responsible for the tier check. The skill assumes if it was invoked, the gate already opened.

---

## Verdict logic (mechanical)

```python
if len(findings) == 0:
    verdict = "clean"
elif any(f.blocking for f in findings):
    verdict = "blocked"
else:
    verdict = "findings"
```

No probabilistic branch. Same envelope inputs → same verdict bytes.

---

## Determinism contract

- `finding_id` is content-addressed (sha1) — same convention as P1.
- Severity mapping is a fixed dict, not conditional logic.
- Dedup keeps the highest severity entry per `finding_id`.
- File ordering in the report is alphabetical by `file_path` (then `finding_id` as tiebreaker).
- Tests use fixture envelopes (no real subagents) — same pattern P1 used.

---

## Token budget

This skill multiplies verify-phase cost by the number of modified files, but each subagent gets a **smaller** context (one diff + one spec excerpt). For changes touching ≤ 5 files: net cost roughly doubles vs. whole-task review, but recall on per-file issues improves materially. For changes touching > 10 files: caller should reconsider whether the change should have been split into multiple SDD changes.

---

## See also

- `INTEGRATION.md` — orchestrator contract: detection, invocation, verdict dispatch.
- `_aggregator.py` — pure-logic aggregation.
- `.claude/agents/code-reviewer.md` — the agent dispatched per diff.
- `.claude/skills/sdd-debate/` — P1 sibling skill (same conventions).
