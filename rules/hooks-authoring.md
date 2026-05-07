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

- Hook scripts live in `.claude/hooks/`
- Register them in `.claude/settings.json` under `hooks`
- Each hook receives a JSON payload on stdin; exit code 0 = allow, non-zero = block
- Keep hooks fast: no network calls, no heavy computation
- A hook that does too much is a sign it should be split into multiple focused hooks
