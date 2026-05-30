# Hooks Authoring Rules

## The Core Principle

Hooks are deterministic. Prompt rules are probabilistic.

An LLM follows a CLAUDE.md checklist ~80% of the time. A hook enforces behavior 100% of the time.
When a behavior is non-negotiable, it belongs in a hook — not in a rule that can be forgotten.

## Decision Heuristic

**Use a hook when:**
- The behavior must never be skipped, regardless of context
- It fires on a specific tool event: `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`
- It is a safety gate (block dangerous commands, detect secrets, enforce quality)
- Skipping it even once would cause real harm (data loss, leaked secrets, broken pipeline)

**Use a CLAUDE.md rule when:**
- The behavior is contextual — the model needs to judge when and how to apply it
- It guides HOW to do something, not WHETHER to do it
- It describes a preference, style, or convention (naming, structure, tone)
- The cost of occasionally missing it is low

**Use a skill when:**
- The behavior is a multi-step protocol invoked on demand
- It requires sequential phases with state between steps
- It is too long or conditional to fit in a rule

## Anti-Pattern

Adding a "please remember to X" rule to CLAUDE.md when X is non-negotiable is the most common mistake.
If you catch yourself writing "always", "never", or "must" about a tooling behavior → that's a hook.

## Examples

| Behavior | Wrong placement | Correct placement |
|---|---|---|
| Block `git commit --no-verify` | CLAUDE.md rule | `block-no-verify.py` hook |
| Format code after every save | CLAUDE.md rule | `format-on-save.py` hook |
| Prevent committing `.env` files | CLAUDE.md rule | `pre-commit-guard.py` hook |
| Choose between refactor approaches | hook | CLAUDE.md rule |
| Prefer guard clauses over nesting | hook | CLAUDE.md rule (patterns.md) |
| Run debugging protocol step-by-step | hook | `systematic-debugging` skill |
| Name booleans with `is`/`has` prefix | hook | CLAUDE.md rule (coding-style.md) |

## Writing a Hook

- Hook scripts live in `.claude/harness/`
- Register them in `.claude/settings.json` under `hooks`
- Each hook receives a JSON payload on stdin; exit code 0 = allow, non-zero = block
- Keep hooks fast: no network calls, no heavy computation
- A hook that does too much is a sign it should be split into multiple focused hooks

## Pattern-matching safety gates: classify by EXECUTOR, not by quotes

> Distilled from safety-guard hardening (P0.4 + P0.4b, 2026-05-27).

A safety gate that pattern-matches dangerous strings (`rm -rf`, `DROP TABLE`, `git push --force`) must decide whether a match is a REAL operation or an inert string (a search pattern, a doc example). Two heuristics, one right:

**WRONG — "is the match inside quotes?"** A dangerous string inside quotes is NOT inherently safe. `rg 'DROP TABLE' migrations/` is safe (search pattern) but `psql -c 'DROP TABLE users'` is destructive (SQL passed to an executor). Both have the token inside quotes. Quote-detection allows both → lets real destruction through. It ALSO failed for `bash -c 'rm -rf /tmp'` (quoted rm passed to bash executor).

**RIGHT — "what tool executes this segment?"** Maintain a READ-TOOL allowlist (`rg`, `grep`, `cat`, `echo`, `find`, `bat`, `head`, `tail`, ...). A dangerous token is inert ONLY if the segment STARTS WITH a read-only tool. Anything else (`psql`, `mysql`, `bash -c`, `sh -c`, raw `rm`) executes → block.

**Compound commands:** split on sequencing operators (`&&`, `||`, `;`) into independent commands first, then split each independent command on `|` into pipeline stages. The two operators are NOT equivalent:

- `&&`, `||`, `;` = **sequencing** — each side is an independent command evaluated in isolation (current behaviour for the non-pipe cases).
- `|` = **data flow** — stdout of the left stage becomes stdin of the right stage. A dangerous string produced upstream CAN be consumed by a downstream executor.

**Pipeline data-flow rule (P0.4c — CLOSED):** for each pipe-connected group of stages, if ANY stage contains a dangerous token AND at least one stage is NOT a read-tool (i.e. a real executor that would receive the piped data) → BLOCK. An all-read-tool pipeline (`echo 'DROP TABLE' | grep`) is inert — no executor consumes the payload.

Examples now blocked: `printf 'DROP TABLE' | psql mydb`, `echo 'rm -rf /tmp' | sh`, `echo 'DROP DATABASE' | mysql -u root`.

**Remaining open gap:** variable indirection and command substitution still defeat the gate. `X='DROP TABLE'; psql -c "$X"` and `psql -c "$(echo 'DROP TABLE x')"` — the dangerous token is never visible as a literal in the command string. This requires abstract data-flow analysis, not pattern matching. Document it; don't pretend the gate catches it.

**Honesty in block messages:** never tell the user "type X to override" unless the hook actually parses X. A PreToolUse hook only sees the current tool call — it cannot read prior chat. If there's no real override, say so and list the actual escape hatches (non-rm commands, `find -delete`, profile narrowing). A lying block message erodes trust and pushes users to bypass the gate entirely.

**Orchestrator note:** when you spec a fix for a safety gate, do NOT assert "approach X works for case Y" without verifying — that assumption can be wrong (the P0.4b spec wrongly claimed quote-detection was fine for `rm`; it wasn't for `bash -c 'rm -rf'`). VERIFY_NOT_ASSUME applies to the instructions you give subagents, not just to their output.
