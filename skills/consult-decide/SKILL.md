---
name: consult-decide
description: "Planning-only dual-blind-proposer for decision-between-options questions. Reuses sdd-debate's state machine without entering the SDD pipeline. Outputs a consensus / hybrid / divergence verdict in plain prose."
allowed-tools: ["Task", "Read", "Bash"]
auto-activate: false
version: 1.0.0
when:
  - command: /consult
  - mode: decision
---

# consult-decide — Dual-Blind-Proposer for Option Decisions (v7.1 Ola 19)

**Purpose**: When the user asks `/consult` to choose between two (or three) options — tech stack, architectural pattern, library — fan out two blind proposers, each defending one option, then converge mechanically via the existing `sdd-debate` state machine. No SDD change, no spec, no tasks — pure planning.

**Difference from `sdd-debate`**: That skill runs INSIDE the SDD pipeline post-`sdd-design`. This skill runs STANDALONE from `/consult`. They share `_state_machine.py` but write to different engram topic keys and never persist a design artifact.

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `question` | string | yes | The raw user question (Spanish or English) |
| `force_debate` | bool | no | True when `--debate` flag is present. Skips keyword auto-detect. |
| `domain_hint` | `general` \| `tech` | no | Default: detected from question keywords |

---

## Auto-trigger

Skill is invoked from `/consult` when the question matches any of (case-insensitive, en + es):
`vs`, ` or `, ` o `, `versus`, `elegir entre`, `decidir entre`, `comparar`, `cuál es mejor`, `which is better`, `compare`. Explicit `--debate` flag overrides detection and forces invocation.

---

## Workflow

### Phase 1 — Parse options

Split the question on the separator keyword. Trim. Accept 2–3 options.

Example: `"PostgreSQL or MongoDB for this feature?"` → `["PostgreSQL", "MongoDB"]`.

If parsing yields <2 options, abort and tell the user the question wasn't structured as a choice.

### Phase 2 — Pick proposer agent

Default: `agent007:product-expert` (general decisions).

If the question contains stack-level keywords (`database`, `postgres`, `mongo`, `redis`, `typeorm`, `microservice`, `monorepo`, `nestjs`, `kafka`, `queue`, `cache`, `framework`, `language`, `typescript`, `python`, `go`, `rust`): use `agent007:backend-db-expert`.

### Phase 3 — Fan-out (blind parallel)

Spawn two Task invocations in the SAME orchestrator turn. Each receives:

```
You are running in adversarial peer-review mode.
You will NOT see the other proposer's reasoning.
DEFEND option <X>. Argue FOR it. Find ≥3 concrete reasons it beats <Y>.
Be specific (cite trade-offs, scale, team, ecosystem) — not generic.
Emit a SubagentResponseV1 envelope with a markdown body under "## Findings".
Each finding is a bullet: `- <area>: <claim>`.
```

Persist bodies to engram:
- A → `consult/decide/<timestamp>/<option-a>`
- B → `consult/decide/<timestamp>/<option-b>`

### Phase 4 — Converge via state machine

```python
import sys
sys.path.insert(0, ".claude/skills/sdd-debate")
from _state_machine import run_debate

result = run_debate(
    change_name=f"consult-decide-{timestamp}",
    proposal_a_path=body_a,   # raw markdown — module accepts strings
    proposal_b_path=body_b,
    tier="medium",            # always 1 round, early-exit on convergence
)
```

The state machine handles hash-merge, stance resolution, verdict derivation. Skill does NOT modify it.

### Phase 5 — Render verdict in prose

| Verdict | Output template |
|---|---|
| `consensus` | "Both proposers converged on **<winner>**. Reasons: <merged bullets>." |
| `hybrid` | "Each option wins in different dimensions. Use **<A>** for <use-case-A>; use **<B>** for <use-case-B>." |
| `divergence` | "Proposers maintained opposing positions. Disagreements: <list>. Decide with the user." |

The skill returns prose, not JSON. The orchestrator pastes it directly into the `/consult` reply.

---

## Example

```
/consult ¿PostgreSQL o MongoDB para este feature de 100 usuarios?
→ Mode: consult-decide (matched "o")
→ Options: ["PostgreSQL", "MongoDB"]
→ Proposer agent: backend-db-expert
→ Fan-out: 2 parallel Task calls
→ State machine: consensus (PostgreSQL — relational fit, ACID, small scale)
→ Reply: "Both proposers converged on PostgreSQL..."
```

---

## Token budget

Two subagent spawns + 1 state-machine pass. No second round (medium tier). ~1.2× the cost of a single deep `/consult --deep` call. Early-exit when both findings hash-match.

---

## Determinism contract

- Same question + same proposer bodies → same verdict (state machine is content-addressed).
- Skill itself adds NO probabilistic branching beyond the proposer LLM calls.
- Topic keys include timestamp to avoid collision across consultations.

---

## Friction with reused modules

- `_state_machine.py` has NO `if __name__ == "__main__"` guard and exposes `run_debate` as the public entrypoint. Import path requires `sys.path.insert(0, …)` because the parent directory uses a hyphen (`sdd-debate`) which Python cannot import as a package without aliasing. **Not refactored** per Ola 19 constraint.
- The module accepts raw markdown strings (not just file paths) — see `_load_proposal()` — so this skill can pass subagent bodies directly without writing temp files.

---

## See also

- `../sdd-debate/SKILL.md` — pipeline twin (runs inside SDD)
- `../sdd-debate/_state_machine.py` — shared convergence engine
- `consult-critique/SKILL.md` — adversarial review counterpart
