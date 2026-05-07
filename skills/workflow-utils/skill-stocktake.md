---
name: skill-stocktake
description: "Automated skill quality audit. Evaluates every skill against a checklist, assigns Keep/Improve/Retire/Merge verdicts, and caches results for incremental re-runs. Requires explicit confirmation before any deletion."
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
invokable: true
accepts_args: false
version: 1.0.0
constraints:
  - read_only_unless_approved
  - cache_results
  - incremental_on_second_run
---

# Skill Stocktake

Slash command: `/skill-stocktake`

Audits every skill in the system and produces a verdict table. Nothing is deleted without explicit user confirmation per item.

---

## Step 1 — Load Skill List

Read `.claude/skills/INDEX.md` to get the canonical list of skills and their paths.

If INDEX.md is missing or stale, fall back to: find all `*.md` files under `.claude/skills/` excluding `INDEX.md` and `_shared/`.

---

## Step 2 — Check Cache (Incremental Mode)

Read `.sdlc/state/skill-stocktake.json` if it exists.

If found:
- Extract `last_run` timestamp
- Run `git log --since="<last_run>" --name-only --pretty=format: -- .claude/skills/` to find skills modified since the last run
- Only re-evaluate those skills; carry forward cached verdicts for the rest

If not found: evaluate all skills (full run).

---

## Step 3 — Evaluate Each Skill

For each skill in scope, run the following four checks:

**Consumer check** — Is this skill referenced from any of:
- `CLAUDE.md` (any project or global)
- Any agent file under `.claude/agents/`
- Any command file under `.claude/commands/`
- Any other skill file (as a dependency)

Result: `consumed: yes | no`

**Accuracy check** — Does the `description` field in the frontmatter match what the skill body actually does?

Read the first 40 lines of the body. If the description would mislead a reader about the skill's purpose, flag it.

Result: `accurate: yes | no | partial`

**Redundancy check** — Does this skill overlap >70% in purpose with another skill?

Compare the skill's `description` and constraint list against all other skills. Overlap is semantic, not textual — two skills that do the same thing in different words are redundant.

Result: `overlap: none | partial | high (with which skill)`

**Freshness check** — When was this skill last modified?

Run: `git log -1 --format="%ci" -- <skill-path>`

Flag as stale if last modified more than 90 days ago AND it has no consumers.

Result: `last_modified: <date> | untracked`

---

## Step 4 — Assign Verdict

| Condition | Verdict |
|---|---|
| consumed + accurate + no overlap | Keep |
| consumed + (inaccurate OR partial overlap) | Improve |
| not consumed + not stale | Improve (add consumer or document purpose) |
| not consumed + stale | Retire |
| high overlap with another skill | Merge (specify which) |

---

## Step 5 — Save Cache

Write results to `.sdlc/state/skill-stocktake.json`:

```json
{
  "last_run": "<ISO timestamp>",
  "verdicts": {
    "<skill-name>": {
      "verdict": "Keep|Improve|Retire|Merge",
      "reason": "...",
      "action_required": "...",
      "checked_at": "<ISO timestamp>"
    }
  }
}
```

---

## Step 6 — Present Verdict Table

Output grouped by verdict type, worst first (Retire → Merge → Improve → Keep):

```
| Skill | Verdict | Reason | Action required |
|---|---|---|---|
| systematic-debugging | Keep | Consumed by CLAUDE.md, accurate, no overlap | None |
| old-unused-skill | Retire | No consumers, last modified 120 days ago | Confirm deletion |
| agent-init | Merge | 80% overlap with sdd-init | Confirm merge with sdd-init |
| code-review | Improve | Description says "audit" but body does "suggest" | Update description |
```

---

## Step 7 — Retire/Merge Confirmation

For each `Retire` or `Merge` verdict:
- Ask explicitly: `"Retire <skill-name>? (yes / no / skip)"`
- Wait for response before proceeding to the next item
- Only delete or archive after receiving "yes" for that specific skill
- Never batch-delete

For `Improve` verdicts: present the specific suggestion. No confirmation needed to suggest — confirmation only needed to write the change.
