# sdd-debate — Orchestrator Integration Contract

This document is the **contract** the orchestrator follows when wiring `sdd-debate` into the SDD pipeline. It does NOT implement the orchestrator — it documents the surface that downstream Olas will hook into.

---

## 1. Detection

After `sdd-design` returns, the orchestrator reads:

```
.sdlc/state/<change-name>/triage.json
```

The relevant field is `debate_required` (boolean, set by the P0 `debate-trigger.py` Guide).

| `triage_tier` | `debate_required` | Action |
|---|---|---|
| `trivial` | false | Skip sdd-debate. Go directly to sdd-tasks. |
| `medium` | true | Invoke sdd-debate with `tier=medium`. |
| `high` | true | Invoke sdd-debate with `tier=high`. |

If `triage.json` is missing (defensive default): treat as `medium` and invoke.

---

## 2. Invocation

The orchestrator calls the skill with these canonical inputs:

```
Skill('sdd-debate', {
  change_name: "<change>",
  baseline_design_ref: ".sdlc/state/<change>/design.md",   # file path
  tier: "<medium|high>",
})
```

Skill internally:
1. Spawns two `sdd-design` subagents in parallel (Task tool, same orchestrator turn).
2. Writes their outputs to `.sdlc/state/<change>/design-A.md` and `.sdlc/state/<change>/design-B.md`.
3. Invokes `_state_machine.run_debate(...)` to converge.
4. Persists the result.

---

## 3. Verdict dispatch

After the skill returns, the orchestrator reads the verdict from the DebateResult (or from the persisted artifact at `.sdlc/state/<change>/design.md`):

### `consensus`
- Action: proceed to `sdd-tasks` normally with the consensus design as input.
- User notification: brief — "Debate converged on consensus design."
- No special handling required.

### `hybrid`
- Action: proceed to `sdd-tasks` with the hybrid design as input.
- The hybrid body contains findings from both A and B that did not conflict.
- User notification: "Debate produced a hybrid design — both proposers contributed distinct valid findings."

### `divergence`
- Action: **DO NOT proceed automatically to sdd-tasks.**
- Emit escalation to user. The escalation must include:
  - The `divergence_report` body (from `.sdlc/state/<change>/divergence.md`).
  - The list of disputed findings with each proposer's final stance.
  - A prompt: "Choose A, choose B, manually reconcile, or extend the round budget."
- The orchestrator pauses the SDD pipeline until the user responds.

---

## 4. Iteration-budget interaction (P2)

`sdd-debate` itself is a single SDD phase from the iteration-budget Sentinel's perspective. The Sentinel sees the skill's envelope:

- `status=done` + verdict in (`consensus`, `hybrid`) → normal flow.
- `status=done` + verdict=`divergence` → no auto-retry; user resolves.
- `status=partial` → Sentinel may re-invoke if budget remains (rare — debate is generally all-or-nothing).
- `status=blocked` → no auto-retry; escalate.

The state machine's internal round budget (1 for medium, 2 for high) is INSIDE the skill and consumes NO iteration-budget invocations. Only re-invocations of `sdd-debate` itself count.

---

## 5. File-based artifacts

All artifacts produced by this skill are written to `.sdlc/state/<change>/`:

| Artifact | File path |
|---|---|
| Proposer A output | `.sdlc/state/<change>/design-A.md` |
| Proposer B output | `.sdlc/state/<change>/design-B.md` |
| Consensus or hybrid design (final) | `.sdlc/state/<change>/design.md` (overwrites baseline) |
| Divergence report | `.sdlc/state/<change>/divergence.md` |
| Debate audit log (rounds, stances) | `.sdlc/state/<change>/debate-audit.md` |

When `triage_tier=trivial`, none of these are written.

---

## 6. Failure modes

| Failure | Behavior |
|---|---|
| One of the two A/B subagents returns an error | Skill emits `status=partial`, reason="proposer-failed". No verdict. Iteration-budget Sentinel decides retry. |
| Both A and B return empty findings | Verdict = `consensus` (vacuously — nothing to debate). Skill returns immediately. |
| State machine wall-clock budget exceeded | Findings still in `pending` are forced to `disputed`. Verdict typically becomes `divergence`. |
| `_state_machine` raises | Skill emits `status=blocked` with error details. NO auto-retry. |

---

## 7. What this Ola does NOT change

This Ola (Ola 16) ships ONLY the skill + the state-machine module + tests. It does NOT:
- Modify the orchestrator's CLAUDE.md routing.
- Update `settings.json` hook registration.
- Change `triage-paths.toml` or `iteration-budget.toml`.
- Touch the `sdd-design` agent definition.

The orchestrator wire-up is Ola 17's responsibility, after this skill is verified in isolation against the test fixtures.
