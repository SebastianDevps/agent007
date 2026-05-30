---
name: sdd-debate
description: "Dual-blind-proposer convergence between sdd-design and sdd-tasks. Spawns two parallel sdd-design subagents, hash-merges findings, runs a deterministic stance state machine (accept/concede/defend/dismiss), and emits one of three verdicts: consensus, hybrid, or divergence."
allowed-tools: ["Task", "Read", "Write", "Bash"]
auto-activate: when triage.json.debate_required == true after sdd-design completes
version: 1.0.0
when:
  - phase: post-sdd-design
  - triage_tier: [medium, high]
---

# sdd-debate — Dual-Blind-Proposer Convergence (v7.1 P1)

**Purpose**: Insert an adversarial gate between `sdd-design` and `sdd-tasks` so design errors are caught BEFORE they propagate into the task breakdown. Convergence is mechanical (state machine), not declared by a judge LLM.

**Trigger**: Orchestrator detects `triage.json.debate_required == true` after `sdd-design` completes. The original `sdd-design` output is the baseline; this skill re-runs design twice in blind parallel and reconciles.

**Skill text stays minimal — the logic lives in `_state_machine.py`.**

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `change_name` | string | yes | The SDD change identifier (used for file organization) |
| `baseline_design_ref` | string | yes | Topic key or path of the original `sdd-design` output |
| `tier` | `medium` \| `high` | yes | From `triage.json.triage_tier` |
| `subagent_invoker` | callable | optional | If absent, skill spawns real subagents via Task tool |

---

## Workflow

### Phase 1 — Fan-out (blind parallel)

Spawn `sdd-design` TWICE via the Task tool, in parallel. Each invocation:

1. Receives the same baseline inputs (proposal, spec) PLUS a per-instance tag.
2. Is told its instance: `instance=A` for the first, `instance=B` for the second.
3. Is told: "You are running in adversarial peer-review mode. You will NOT see the other proposer's output. Produce your design proposal independently."
4. Returns a `SubagentResponseV1` envelope. The body is persisted to `.sdlc/state/<change>/`:
   - A → file `.sdlc/state/<change>/design-A.md`
   - B → file `.sdlc/state/<change>/design-B.md`

**The two invocations MUST be launched in the same orchestrator turn** so neither sees the other's transcript.

### Phase 2 — State machine

After both A and B return:

1. Load both proposal bodies (markdown).
2. Call `_state_machine.run_debate(change_name, proposal_a_path, proposal_b_path, tier=tier)`.
3. The module:
   - Extracts findings as `(file_path, claim)` tuples from bullet sections.
   - Hashes each finding: `finding_id = sha1(file_path + "::" + claim)[:12]`.
   - Same `finding_id` from A and B → automatic agreed (no rounds).
   - Disputed findings go through the stance table.

### Phase 3 — Round budget

| Tier | Max rounds per finding | Wall clock cap |
|---|---|---|
| `medium` | 1 | 90 seconds |
| `high` | 2 | 180 seconds |

Each round re-invokes the relevant `sdd-design` subagent with: original proposal + the disputed finding + opponent's stance + instruction to choose a new stance (one of: accept, concede, defend, dismiss).

If a finding doesn't reach a terminal state within rounds → `disputed`.

### Phase 4 — Verdict + persistence

Read `DebateResult.verdict`:

| Verdict | Action | File write |
|---|---|---|
| `consensus` | Persist consensus body to `.sdlc/state/<change>/design.md` (replaces baseline). | yes |
| `hybrid` | Persist hybrid body (both sides contributed non-conflicting findings) to `.sdlc/state/<change>/design.md`, tagged `kind=hybrid`. | yes |
| `divergence` | Write `divergence_report` to `.sdlc/state/<change>/divergence.md`, emit user-facing escalation. DO NOT auto-advance to sdd-tasks. | yes |

---

## Stance state machine (summary)

| A stance | B stance | Initial terminal | Needs round? |
|---|---|---|---|
| accept | accept | agreed | no |
| accept | concede | agreed | no |
| concede | concede | agreed | no |
| accept | defend | pending | yes |
| concede | defend | pending | yes |
| defend | defend | disputed | no |
| accept | dismiss | pending | yes |
| dismiss | dismiss | rejected | no |
| defend | dismiss | disputed | no |
| concede | dismiss | disputed | no |

Symmetric entries (e.g. `defend, accept`) follow the same outcome. Full table is in `_state_machine.py:INITIAL_TRANSITIONS`.

If after `max_rounds` the pair is still `pending`, the finding is terminated as `disputed`.

---

## Why this beats "LLM as judge"

A judge LLM is just another agent's opinion. State-machine convergence is mechanical — same inputs → same outputs. If A says "use shutil.move" and B says "use os.rename" and both `defend` through the round budget, the machine surfaces a real disagreement worth user attention. No rationalization soup.

---

## Determinism contract

- `finding_id` is content-addressed (sha1).
- The transition table is an explicit dict, not conditional logic.
- Verdict derivation has no probabilistic branch.
- The `_state_machine` module's pure-logic surface has no I/O beyond loading proposals.
- Tests use fixture invokers (no real LLM calls) and the same inputs MUST produce the same outputs across runs.

---

## Token budget by tier

- `medium`: ~1.3× single-design cost (1 round, hash dedup, early-exit on convergence)
- `high`: ~2.2× single-design cost (up to 2 rounds, full machine)
- `trivial` tier: this skill is NOT invoked (gated by P0 triage)

---

## See also

- `INTEGRATION.md` — orchestrator contract: how to detect, invoke, and dispatch on verdict.
- `_state_machine.py` — pure-logic implementation.
