# /evolve — Promote Instincts to Skills

Review instinct clusters and promote high-confidence patterns into reusable skills.

---

## Usage

```
/evolve                    # interactive review of all skill candidates
/evolve --domain <domain>  # focus on a specific domain
/evolve --auto             # auto-promote all candidates with confidence ≥ 0.8
/evolve --list             # list candidates without promoting
```

---

## Step 1 — Run cluster analysis

```bash
node .claude/scripts/instinct-engine.js cluster
```

Output: list of domains with instinct count, eligible count, and promotion status.

## Step 2 — Review candidates

For each skill candidate in `.claude/instincts/evolved/`:

1. Read the evolved instinct YAML
2. Assess: Is this a reusable pattern worth formalizing?
3. Present to user:

```
## Skill Candidate: [domain]

Trigger: [when this applies]
Action:  [what to do]
Confidence: [X%] · Evidence: [N observations]
Based on instincts: [list of source instinct IDs]

Promote to skill? [Y]es / [N]o / [E]dit first
```

## Step 3 — On approval

If user approves, create a new skill file at `.claude/skills/domain/<id>/SKILL.md`:

```markdown
---
name: [derived from instinct id]
description: "[action summary]"
domain: [domain tag]
confidence: [inherited from instinct]
origin: evolved-instinct
promoted: [ISO timestamp]
---

# [Skill Name]

## Trigger
[when this applies]

## Action
[what to do — from instinct action field]

## Evidence
Evolved from [N] observations over [M] sessions.
Source instincts: [list]
```

Then move the evolved instinct from `evolved/` to archive (keep `.yaml` with `promoted: true`).

## Step 4 — On rejection

If user rejects:
- Mark the evolved instinct with `rejected: true` in YAML
- Apply decay: `node .claude/scripts/instinct-engine.js decay [id]`

---

## Confidence Gate

**NEVER auto-promote** instincts with confidence < 0.7 without explicit user confirmation.

At confidence ≥ 0.9 (core): offer auto-promotion with a single `[Enter]` confirm.

---

## Cluster Rules

| Condition | Result |
|-----------|--------|
| ≥ 3 instincts in same domain with confidence ≥ 0.5 | Cluster formed |
| Cluster present + user runs /evolve | Skill candidate shown |
| User confirms | SKILL.md created in `.claude/skills/domain/` |
| User rejects | Instinct decayed, candidate archived |
