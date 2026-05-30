---
name: spec
version: 1.0
description: "CRUD sobre specs estables en openspec/specs/ — bypass del pipeline SDD para cambios chicos"
accepts_args: true
preconditions:
  - first_arg_in: ["new", "edit", "verify", "list"]
outputs:
  - name: spec_action_result
    type: string
    format: "ok | error:<code>"
triggers:
  - "spec new"
  - "spec edit"
  - "spec verify"
  - "spec list"
routing:
  all_actions: "Skill('spec') with $ARGUMENTS"
---

# /spec — Manage Stable Specs

Routes to `Skill('spec')` (`.claude/skills/spec/SKILL.md`) which dispatches to sub-actions.

This is a **thin shell**. No inline logic. All parsing, race-checking, audit, and LLM-driven edit live in the skill.

---

## Invocation

```
/spec new <name>         # Create new spec with scaffold
/spec edit <name>        # Edit existing spec interactively (LLM-driven, race-guarded)
/spec verify [<name>]    # Validate spec schema — single file or batch
/spec list [--json]      # List all stable specs with req count and schema status
```

`<name>` must match `^[a-z0-9][a-z0-9-]*[a-z0-9]$` (lowercase, hyphens, min 2 chars).

---

## Routing

```
Skill('spec') with $ARGUMENTS
```

The skill handles:
- `new`    → `python scripts/spec/spec_new.py <name>` (scaffold creation + EEXIST check + audit)
- `edit`   → race check via `spec_race_check.py` + LLM Read/Edit flow (scope: `openspec/specs/<name>.md` only)
- `verify` → `python scripts/spec/spec_verify.py [<name>]` (schema validation, batch if no name)
- `list`   → `python scripts/spec/spec_list.py [--json]` (tabular or JSON output)

All actions append one line to `.sdlc/state/spec-command-audit.jsonl`.

---

## Examples

**Create a new spec:**
```
/spec new payment-gateway
```

**Edit an existing spec interactively:**
```
/spec edit payment-gateway
```

**Validate a single spec:**
```
/spec verify payment-gateway
```

**Validate all specs (batch):**
```
/spec verify
```

**List all specs as a table:**
```
/spec list
```

**List all specs as JSON:**
```
/spec list --json
```

---

## Risk

- **Low** — mutates only `openspec/specs/<name>.md` (path-guard whitelist covers `spec` skill identity)
- Audit log written automatically to `.sdlc/state/spec-command-audit.jsonl`
- Race check runs before any `edit` mutation (reads `openspec/changes/_index.json` read-only)

> Note: `/spec verify` checks schema only — it is NOT the same as `/sdd-verify` (which validates implementation against a spec). See `.claude/skills/INDEX.md` for the distinction.
