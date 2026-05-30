---
name: adr-review
description: "Review existing Architecture Decision Records. Flag ADRs whose aging signals may have triggered given current state. Categorizes each as valid / aged / superseded and suggests follow-up actions."
allowed-tools: ["Read", "Bash", "Glob"]
auto-activate: false
version: 1.0.0
when:
  - command: Skill('adr-review')
---

# adr-review — Periodic ADR Aging Check (v7.2 Ola 35)

**Purpose**: Walk through every ADR in `.sdlc/adrs/` and assess whether its aging signals have triggered. Outputs a categorized report so the team knows which decisions deserve a fresh look.

**Trigger keywords (manual)**: `adr review`, `review adrs`, `check decisions`, `audit architecture`.
**Auto-trigger**: none. This is a periodic operation — recommend running monthly or quarterly.

---

## Inputs

| Field | Type | Required | Description |
|---|---|---|---|
| `--all` | flag | no | Review every ADR regardless of date (default) |
| `--since=YYYY-MM-DD` | string | no | Only review ADRs accepted before this date |
| `--status=<s>` | string | no | Filter by status: `proposed`, `accepted`, `superseded` |

---

## Workflow

### Phase 1 — Load ADRs

1. `Glob` `.sdlc/adrs/ADR-*.md`.
2. For each file, parse:
   - ADR number (from filename)
   - Title (H1)
   - Status (markdown frontmatter line)
   - Date
   - Aging signals section (bullet list)
3. Apply `--since` and `--status` filters if present.

### Phase 2 — Evaluate aging signals

For each ADR, run these checks:

**Check 1 — Status hygiene**
- If status is `proposed` and date > 30 days ago → flag as `stale-proposal`.
- If status is `superseded` → categorize as `superseded`, skip further checks.

**Check 2 — Signal evaluation**
For each aging signal bullet, attempt to assess it:
- Quantitative signals (e.g., "user base exceeds 10k") → ask user to confirm current value.
- Qualitative signals (e.g., "if we add multi-region") → check recent git log + file additions for matching keywords via `Bash` (`rg`/`fd`).
- Cannot auto-evaluate → mark as `manual-check-required`.

**Check 3 — Contradiction scan**
- Extract decision keywords (`Decision` section).
- `rg` the codebase for opposite patterns. Example: ADR says "use JWT only" → search for `session.cookie` usages. Flag matches as `possible-contradiction`.

### Phase 3 — Categorize

| Category | Criteria |
|---|---|
| `valid` | All signals untriggered, no contradictions |
| `aged` | ≥1 signal triggered OR contradiction found |
| `superseded` | Status is `superseded` |
| `stale-proposal` | Status `proposed` for >30 days |
| `manual-check-required` | Signals not auto-evaluable |

### Phase 4 — Render report

Output prose, grouped by category:

```
## ADR Review — YYYY-MM-DD

### Valid (N)
- ADR-001 — <title>

### Aged (N) — recommend re-review
- ADR-007 — <title>
  - Signal triggered: "<signal>"
  - Suggested action: `Skill('adr-write')` to propose a replacement

### Superseded (N)
- ADR-003 — <title> (replaced by ADR-012)

### Stale proposals (N)
- ADR-015 — <title> (proposed 47 days ago — accept or reject)

### Manual check required (N)
- ADR-009 — signal "<signal>" needs human evaluation
```

### Phase 5 — Emit envelope

Return `SubagentResponseV1`:
- `status`: `success`
- `executive_summary`: "Reviewed N ADRs: X valid, Y aged, Z superseded, W stale, M manual."
- `artifacts`: `[]` (no files written — review is read-only)
- `next_recommended`: "Run `Skill('adr-write')` for each aged ADR to draft replacements." (if any)
- `risks`: `[]`
- `skill_resolution`: `injected | fallback-*`

---

## Example invocations

```
Skill('adr-review')
Skill('adr-review --since=2026-01-01')
Skill('adr-review --status=proposed')
```

---

## Honest limits

- The skill cannot detect signals it does not understand. "If our user base exceeds 10k" requires the user to know the current count.
- Contradiction scan is keyword-based — false positives are common. Treat findings as hints, not verdicts.
- This is a read-only review. It does NOT auto-update ADR status — every change requires `adr-write` (for supersedes) or manual edit.

---

## See also

- `../adr-write/SKILL.md` — to draft replacements for aged ADRs
- `.sdlc/adrs/README.md` — directory purpose
