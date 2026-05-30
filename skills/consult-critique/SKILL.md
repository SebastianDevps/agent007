---
name: consult-critique
description: "Planning-only adversarial-review fan-out for proposal critique. Reuses sdd-verify-diff's aggregator without entering the SDD pipeline. Outputs findings count + top blocking issues in plain prose."
allowed-tools: ["Task", "Read", "Bash"]
auto-activate: false
version: 1.0.0
when:
  - command: /consult
  - mode: critique
---

# consult-critique — Adversarial Review for Proposals (v7.1 Ola 19)

**Purpose**: When the user pastes a proposal (architecture sketch, plan, design doc) into `/consult --critique`, fan out two adversarial reviewers in parallel, aggregate findings via the existing `sdd-verify-diff` aggregator, and surface the top blocking issues. No SDD change, no per-file diff loop — pure planning-time critique.

**Difference from `sdd-verify-diff`**: That skill reviews actual git diffs per file inside the SDD pipeline post-`sdd-apply`. This skill reviews a prose proposal standalone from `/consult`. They share `_aggregator.py` (severity map, hash dedup, verdict derivation) but consult-critique builds review envelopes from prose, not from `git diff` chunks.

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `proposal` | string | yes | The pasted proposal text (≥ 50 chars) |
| `force_critique` | bool | no | True when `--critique` flag is present. Skips auto-detect. |
| `reviewers` | list | no | Override default reviewer agents |

---

## Auto-trigger

Skill is invoked from `/consult` when:
- Explicit `--critique` flag, OR
- Input contains structured-proposal markers: headings `## Approach`, `## Plan`, `## Design`, `## Implementation`, AND total length > 200 words.

---

## Workflow

### Phase 1 — Pick reviewer pair

Default: `agent007:code-reviewer` + `agent007:security-expert` (broad coverage).

Override based on detected keywords in the proposal:
- Contains `architecture`, `clean architecture`, `bounded context`, `module`, `layering` → swap `code-reviewer` for `agent007:architect`.
- Contains `refactor`, `legacy`, `technical debt` → swap `security-expert` for `agent007:refactor-cleaner`.
- Contains `auth`, `jwt`, `oauth`, `password`, `secret`, `encryption` → KEEP `security-expert` (highest priority).

### Phase 2 — Fan-out (parallel adversarial)

Spawn two Task invocations in the SAME orchestrator turn. Each receives:

```
You are running in ADVERSARIAL review mode.
Assume the proposal is broken. Find weaknesses, gaps, risks.
Be specific — quote the proposal verbatim when calling out an issue.
Cite line ranges or section names. No generic comments.

Emit a SubagentResponseV1 envelope. Body MUST follow code-reviewer
REVIEWER-mode format:

### CRITICAL | HIGH | MEDIUM | LOW
**<Title>** · `<section-or-path>` · Confidence: NN%

(Title is the claim; section is the proposal section being critiqued.)
```

Persist envelopes to engram:
- Reviewer 1 → `consult/critique/<timestamp>/reviewer-1`
- Reviewer 2 → `consult/critique/<timestamp>/reviewer-2`

### Phase 3 — Aggregate via _aggregator.py

```python
import sys
sys.path.insert(0, ".claude/skills/sdd-verify-diff")
from _aggregator import aggregate_reviews

report = aggregate_reviews(
    change_name=f"consult-critique-{timestamp}",
    review_envelopes=[envelope_1, envelope_2],
)
# report.findings_by_severity → {"high": N, "med": N, "low": N}
# report.blocking_findings    → list[Finding] where blocking==True
# report.verdict              → "clean" | "findings" | "blocked"
```

Aggregator handles:
- Severity collapse: CRITICAL/HIGH → high+blocking; MEDIUM → med; LOW → low.
- Dedup by `sha1(file_path + "::" + claim)[:12]` — both reviewers flagging the same issue counts once but keeps the highest severity.
- Verdict: `clean` (no findings) → `findings` (only non-blocking) → `blocked` (any blocking).

### Phase 4 — Render verdict in prose

Template:

```
Critique found <N> findings (<H> high, <M> med, <L> low). Verdict: <verdict>.

Top blocking issues:
1. <title> — <section>
2. <title> — <section>
3. <title> — <section>

<if verdict == "clean">
No blocking issues. Proposal looks structurally sound.
</if>
<if verdict == "blocked">
Address the high-severity items before proceeding to /dev or /sdd-new.
</if>
```

Skill returns prose. Orchestrator pastes it into the `/consult` reply.

---

## Example

```
/consult --critique
[user pastes 300-word proposal containing hard-coded secret reference]

→ Mode: consult-critique
→ Reviewers: code-reviewer + security-expert
→ Fan-out: 2 parallel Task calls
→ Aggregator: 3 findings (1 high blocking, 2 med). Verdict: blocked.
→ Reply: "Critique found 3 findings... Top: hard-coded secrets reference in section X."
```

---

## Token budget

Two subagent spawns + 1 aggregation pass. Findings dedup'd by content hash, so duplicate flags don't inflate output. ~1.5× the cost of a single `/consult --deep`. No iterative re-review.

---

## Determinism contract

- `_aggregator.py` is pure logic — same envelope inputs → same report bytes.
- Skill adds NO probabilistic branching beyond the reviewer LLM calls.
- Timestamps in topic keys avoid collision; same `(file_path, claim)` deduplicates regardless of which reviewer surfaced it.

---

## Friction with reused modules

- `_aggregator.py` import requires `sys.path.insert` (parent dir `sdd-verify-diff` has hyphen, not importable as a package). **Not refactored** per Ola 19 constraint.
- The aggregator's `_extract_findings_from_body` regex expects code-reviewer REVIEWER-mode format (`### HIGH` + `**Title** · \`path\``). The subagent prompt in Phase 2 enforces this format so reviewer prose flows through the existing parser without modification.

---

## See also

- `../sdd-verify-diff/SKILL.md` — pipeline twin (runs inside SDD)
- `../sdd-verify-diff/_aggregator.py` — shared aggregation engine
- `consult-decide/SKILL.md` — decision-mode counterpart
