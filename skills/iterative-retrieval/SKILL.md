---
name: iterative-retrieval
description: "Progressive context refinement for multi-agent orchestration — sends a minimal seed, collects context gaps, enriches incrementally. Finds the minimum sufficient context set before execution."
disable-model-invocation: true
auto-activate: when spawning subagents for sdd-apply or complex multi-file tasks
version: 1.0.0
when:
  - task_type: [feature, refactor]
    pipeline: [medium, complex]
  - phase: [sdd-apply, sdd-verify]
---

# Iterative Retrieval — Progressive Context Refinement

**Purpose**: Solve the subagent context problem. Too much context causes context rot and diluted attention. Too little causes wrong assumptions. This protocol finds the minimum sufficient context set through structured rounds before the subagent executes its main task.

**When to use**: Before spawning any subagent that will read 4+ files or perform multi-file writes. Always used by the orchestrator, never invoked directly by the subagent.

---

## Protocol Rounds

### Round 0 — Seed Prompt

The orchestrator spawns the subagent with only:
- The task description (1–3 sentences, from the SDD task or feature request).
- The entry point: the primary file or module the task starts from.
- The artifact store reference (topic_key or file path) for the relevant spec/design.

Do NOT include: full file contents, dependency trees, or "helpful background".

The seed prompt ends with:
> "Before executing, return a CONTEXT_GAP_REPORT listing what you need. Do not implement yet."

---

### Round 1 — Context Gap Report

The subagent responds with a structured gap report. Format is strict:

```
CONTEXT_GAP_REPORT
------------------
NEEDS: <file path or concept>  | REASON: <why it blocks execution>      | ALTERNATIVE: <if unavailable, I can X>
NEEDS: <file path or concept>  | REASON: <why it blocks execution>      | ALTERNATIVE: <none — required>
...
READY_TO_EXECUTE: false
```

If the subagent already has enough context from the seed:
```
CONTEXT_GAP_REPORT
------------------
READY_TO_EXECUTE: true
```

**Orchestrator action on Round 1:**
- Read each `NEEDS` line.
- Provide exactly what was requested — no extras.
- If an item has `ALTERNATIVE: <none — required>` and it cannot be provided, escalate to the human before proceeding.

---

### Round 2 — Enriched Context Delivery

The orchestrator sends a second prompt containing only the items from the gap report. Format:

```
CONTEXT_DELIVERY
----------------
<file path>: <contents or summary>
<concept>: <explanation>
...

Proceed with execution now. Return results per the task contract.
```

The subagent executes the main task and returns results.

---

### Round 3 — Optional Second Gap (if needed)

If after Round 2 the subagent returns another `CONTEXT_GAP_REPORT` (rare — indicates the first gap report was incomplete), repeat the enrichment once more.

**Budget rule**: Maximum 3 rounds total. After Round 3, the orchestrator sends:
> "Execute with the context available. Document any assumptions made in your result."

Never let retrieval loop forever. Incomplete context with documented assumptions is better than an infinite retrieval cycle.

---

## Budget Summary

| Round | Orchestrator sends | Subagent returns |
|-------|--------------------|------------------|
| 0 | Seed: task + entry point + artifact ref | CONTEXT_GAP_REPORT or READY |
| 1 | Exactly the requested files/concepts | Execution result |
| 2 (optional) | Second gap items | Execution result |
| 3 (hard cap) | "Execute anyway" instruction | Result + documented assumptions |

---

## Why Not Dump Full Context Upfront

Full-context dumps cause three failure modes:
1. **Attention dilution**: the model attends to irrelevant files and misses critical ones.
2. **Stale context**: files sent upfront may differ from files the subagent will actually write, causing coherence errors.
3. **Budget exhaustion**: large context leaves no room for the subagent's own reasoning and output.

Iterative retrieval shifts control to the subagent — it tells the orchestrator what it needs, so context is always intentional.

---

## Integration with SDD Apply

When launching `sdd-apply`, the orchestrator uses this protocol instead of pre-loading all spec + design + tasks content:

1. Seed: task description from `sdd/{change}/tasks` (topic key reference only) + entry-point file.
2. Let the subagent declare what it needs from spec/design.
3. Deliver only declared sections.
4. Subagent executes and writes `apply-progress`.

This keeps each apply batch lean and prevents context bleed between batches.
