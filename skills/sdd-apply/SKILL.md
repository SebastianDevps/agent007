---
name: sdd-apply
description: "Apply phase protocol for SDD changes. Enforces proposal validation gate before any file writes. Plugin-local — overrides user-global sdd-apply behavior for this repo."
version: 1.0
---

# sdd-apply — Apply Phase Protocol

## Specialist Routing (MANDATORY)

Before executing ANY task wave, classify each task by domain. For each domain matched, the wave MUST be delegated to the corresponding specialist agent via the Agent tool — NOT done inline.

| Domain | Specialist | Trigger keywords |
|---|---|---|
| UI / component / page / animation / visual | `frontend-ux-expert` | astro, jsx, tsx, react, component, page, ui, animation, hero, landing, layout, css, tailwind, gsap, motion |
| API / endpoint / database / schema / migration / resilience | `backend-db-expert` | nestjs, controller, service, repository, dto, entity, typeorm, migration, redis, queue |
| Tests / CI / Docker / Kubernetes / monitoring | `platform-expert` | docker, k8s, github actions, jest, vitest, playwright, lighthouse |
| Auth / JWT / OWASP / PII / encryption | `security-expert` | auth, jwt, oauth, password, token, owasp, pii, vulnerability |
| Code review / quality audit | `code-reviewer` | review, audit, quality check |
| Architecture / boundary / pattern audit | `architect-reviewer` | architecture, boundary, pattern review, cross-cutting |
| Docs / readme / changelog / API docs | `docs-architect` | readme, getting started, onboarding doc, docs site |
| Outage / breach / pager / incident | `incident-responder` | outage, sev1, sev2, p0, p1, postmortem, breach |
| Observability / SLI / SLO / OTel | `observability-engineer` | metrics, logs, traces, sli, slo, opentelemetry, dashboard, alert |

**Inline implementation is permitted ONLY for:**
- Wave 0 (pre-flight): reads, audits, baseline captures, dir creation
- Glue tasks: build scripts, JSON parsers, file format conversions, prebuild wiring (no domain expertise needed)
- Single-file mechanical edits in a known glue path (no UI/visual decisions)

**Hard prohibitions (anti-pattern):**
- Consolidating multi-task UI work into one inline pass "for efficiency" — this defeats the skill-resolver
- Inline `Skill('foo')` invocations — the resolver injects skills automatically; explicit calls duplicate work and break on rename
- Writing >50 LOC of UI/visual code inline without dispatching frontend-ux-expert
- Doing the architect-reviewer/code-reviewer's job inline ("looks fine to me" without dispatching the actual reviewer)

If a wave has 2+ tasks of the same domain, dispatch the specialist ONCE with all of them — not one dispatch per task (that's also wasteful).

**If you cannot dispatch a specialist (no `Agent` tool in your allowlist):** return `status: needs_specialist` with `recommended_specialist: <agent-name>` in the envelope and STOP. The orchestrator (which has the `Agent` tool) will re-dispatch. Do NOT fall back to inline implementation — that's the consolidation anti-pattern. Do NOT return `status: blocked` — that's the loop-gate halt and would trigger feedback-loop machinery you don't want.

Failure mode to watch for: rationalizing inline work with "efficiency", "simpler", "I already know how". Those are the rationalizations the Iron Law would flag for TDD — same family.

## Proposal Validation Gate (MANDATORY FIRST STEP)

Before making any file changes, run the proposal validator:

```bash
python scripts/verify/validate_proposal.py openspec/changes/<change>/proposal.md
```

- If the validator exits non-zero, surface its stderr output and **abort immediately**.
- No partial apply must occur. Do NOT write any files if validation fails.
- The `<change>` placeholder is resolved from the active change name (passed via `--change` flag or `.sdlc/state/active-change`).

This gate converts scope compliance from probabilistic (LLM remembers to check) to deterministic (Python exits 1).

## Protocol

### Step 1 — Read artifacts

Read these artifacts in order before writing any code:

1. `openspec/changes/<change>/tasks.md` — task list with `[x]` marks (skip completed tasks)
2. `openspec/changes/<change>/spec.md` — acceptance criteria for each REQ
3. `openspec/changes/<change>/design.md` — architecture decisions and implementation notes

### Step 2 — Check apply-progress

Search for existing `apply-progress` artifact:
- Engram: `mem_search("sdd/<change>/apply-progress")` → `mem_get_observation`
- File: `openspec/changes/<change>/apply-progress.md`

If found: read it, identify the last completed task, resume from the next task. Do NOT repeat completed tasks.

### Step 3 — Implement tasks

Execute tasks in dependency order (see tasks.md dependency graph). For each task:

1. Declare the task being implemented
2. Read all files the task specifies under "Files read"
3. Write or edit only the files the task specifies under "Files written"
4. Run the task's "Verify cmd" and capture output
5. Mark the task `[x]` in the progress artifact
6. Persist progress immediately (do not batch — enables crash recovery)

### Step 4 — Persist progress

After each completed task, save progress to the active artifact store:
- Engram: `mem_save(title="sdd/<change>/apply-progress", topic_key="sdd/<change>/apply-progress")`
- File: append to `openspec/changes/<change>/apply-progress.md`

### Step 5 — Gate per block

After completing each REQ block, run:

```bash
python3 -m unittest discover tests/
```

If any test fails: STOP. Return `partial` with the failing task identified.

## Conventions

- Python 3.9 compatible: use `typing.Optional`, `typing.Tuple` — NOT `str | None` or `tuple[bool, str]`
- stdlib only — no pip dependencies
- Named exports only (Python: no `__all__` hiding)
- Max 200 lines/file, 20 lines/function
- No magic numbers — named constants

## Result Contract

Return a `SubagentResponseV1` JSON envelope:

```json
{
  "status": "done | partial | blocked | needs_specialist",
  "artifact_ref": "file:openspec/changes/<change>/apply-progress.md",
  "executive_summary": "<tasks done> / <total> tasks completed",
  "next_recommended": "sdd-verify",
  "recommended_specialist": "<agent-name, only when status=needs_specialist>",
  "skill_resolution": "injected",
  "risks": [],
  "cost_signals": {"tokens_used": 0, "duration_ms": 0}
}
```

- `blocked` = loop-gate halt (sentinel writes feedback, orchestrator injects on next dispatch).
- `needs_specialist` = dispatch redirect (orchestrator must re-dispatch the specialist named in `recommended_specialist`; no auto-loop, no feedback).
