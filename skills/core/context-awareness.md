---
name: context-awareness
description: "Reference documentation for context detection patterns. Logic implemented in session-orchestrator. Use when reviewing task detection rules."
invokable: false
auto-inject: true
priority: highest
version: 3.1.0
references:
  - references/detection-algorithm.md
  - references/examples.md
  - references/configuration.md
---

# Context Awareness

Auto-injected at the start of every task. Classifies user input into `(taskType, risk, stack)` and routes to the correct workflow. Implementation lives in `session-orchestrator`; this file is the contract every agent must respect in hot context.

---

## Hard Rules

1. **Detect context BEFORE acting.** Never start coding before classifying `taskType` and `risk`.
2. **Announce the routing decision** before invoking any skill or expert: `🎯 [target] | Risk: [low|medium|high|critical]`.
3. **Critical risk requires explicit user "yes"** before proceeding. Document rollback first.
4. **User overrides win.** If the user specifies `--risk=X` or names a workflow, honor it.
5. **One question, one stop.** If two task types match equally, ask one clarifying question and wait.

---

## Task Type — Quick Reference

| Type | Keywords |
|------|----------|
| `feature` | implement, add, create, build, new |
| `bug` | bug, error, fix, broken, not working |
| `refactor` | refactor, restructure, improve, clean up |
| `consult` | how, what, why, should I, mejor manera |
| `review` | review, audit, check, revisar |

Explicit commands override keywords: `/consult` → consult, `/review` → review. Default when ambiguous: `consult`.

---

## Risk — Decision Order (first match wins)

| Risk | Trigger |
|------|---------|
| **critical** | touches auth, payments, or DB schema/migrations |
| **high** | crosses bounded contexts OR touches a critical path |
| **medium** | exposes a new endpoint OR touches >3 files |
| **low** | none of the above |

`consult` and `review` are risk-agnostic (`n/a`).

---

## Routing Matrix

| Task | low | medium | high | critical |
|------|-----|--------|------|----------|
| feature | feature-development-fast-track | feature-development-standard | feature-development-full-pipeline | feature-development-critical |
| bug | bug-fixing-simple | bug-fixing-standard | bug-fixing-systematic | bug-fixing-critical |
| refactor | refactoring-simple | refactoring-standard | refactoring-architectural | refactoring-critical |
| consult | consultation-pipeline (any risk) |||| 
| review | code-review-pipeline (any risk) ||||

---

## Workflow (every task, no exceptions)

1. **Parse** user input → keywords, patterns, entities.
2. **Detect taskType** — keywords table above. If ambiguous → ask one question, stop.
3. **Assess risk** — apply the decision order. Auth/payments/schema short-circuit to `critical`.
4. **Detect stack** — file markers (`nest-cli.json`, `data-source.ts`, `package.json` deps).
5. **Route** via the matrix → name the target workflow.
6. **Announce**: `🎯 <workflow> | Risk: <level>`.
7. **If critical → ask explicit confirmation** with rollback summary. Wait for "yes".
8. **Activate** the routed workflow. Inject Context Awareness as step 1.

---

## Anti-Patterns

- ❌ Starting to code on "Add validation" without classifying.
- ❌ Skipping the routing announcement because "the task seems obvious".
- ❌ Treating an `auth/` change as `medium` because the diff is small — auth is always `critical`.
- ❌ Routing a multi-file refactor to `refactoring-simple` to save time.
- ❌ Proceeding on `critical` without explicit user confirmation.
- ❌ Inventing a workflow name not present in the routing matrix.
- ❌ Logging the decision but not announcing it to the user.

---

## Need → Reference

| When you need... | Read |
|------------------|------|
| Full algorithm pseudocode (parse, detect, assess, route) | `references/detection-algorithm.md` |
| Worked end-to-end examples per task type | `references/examples.md` |
| Logging schema, config (`orchestrator.config.json`), override rules | `references/configuration.md` |

References are lazy-loaded — only read them when you need that specific detail.
