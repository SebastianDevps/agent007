---
name: rules-distill
description: "Scans all skill files, finds principles appearing in 2+ skills, and proposes whether they should be elevated to rules/. Requires explicit user approval before writing anything."
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
version: 1.0.0
constraints:
  - require_approval_before_writing
  - anti-abstraction-guard
  - minimum_2_sources
---

# Rules Distill

Slash command: `/rules-distill`

Scans skills for repeated principles and proposes promotions to permanent `rules/` files.
Nothing is written without explicit user approval per item.

---

## Step 1 — Scan

Read every file matching `.claude/skills/**/*.md`.

For each file, extract statements that function as constraints, rules, or principles:
- Lines starting with `-`, `*`, or numbered lists inside constraint sections
- Frontmatter `constraints:` entries
- Imperative sentences in body sections ("Always X", "Never Y", "Require Z")

Ignore: examples, output format descriptions, phase names, and narrative explanations.

---

## Step 2 — Group

Group extracted statements by semantic similarity. Two statements are semantically similar if they enforce the same behavior, even with different wording.

Discard any group that appears in only one skill.

---

## Step 3 — Anti-Abstraction Guard

For each group, apply this filter before proceeding:

Reject the group if the principle is:
- Vague enough to apply to everything ("write clean code", "be thorough", "think carefully")
- Not actionable (cannot be verified as followed or violated)
- Already present verbatim in an existing `rules/` file

A principle passes the guard only if it is specific, testable, and not already captured.

---

## Step 4 — Present Proposals

For each group that passed the guard, output one line:

```
PRINCIPLE: [exact principle text]
SOURCES: [skill1.md, skill2.md, ...]
ACTION: [Append to rules/X.md | New file rules/Y.md]
STATUS: Pending approval
```

After listing all proposals, ask:
> "Which of these should I promote? Reply with the numbers or 'none'. I will write them one at a time."

---

## Step 5 — Write (one at a time, after approval)

For each approved item:
1. If `ACTION` is "Append": read the target file first, then append the principle under the appropriate heading.
2. If `ACTION` is "New file": create the file with a title, the principle, and a brief rationale.
3. Confirm to the user after each write before proceeding to the next.

Never batch-write all approved items in one pass. One write, one confirmation.

---

## What This Skill Does NOT Do

- It does not modify skill files
- It does not delete anything
- It does not write without explicit per-item approval
- It does not promote vague principles regardless of how many skills contain them
