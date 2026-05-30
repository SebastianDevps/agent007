# Testing Scope & CI Gate Hygiene

> Distilled from P1.3 agent-behavior-test work (2026-05-27), where a test that asserted on an out-of-scope concern (Agent007 mirror parity) turned the entire `make verify` chain RED — blocking unrelated sandbox verification.

## The core rule

**A CI gate must not hard-fail on a concern outside its scope.** If `make verify` gates sandbox work, a test that fails because of a *deferred* or *out-of-scope* gap breaks the gate for everyone, including work that has nothing to do with that gap.

## Three states for a known-incomplete check

When you write a test for something that is KNOWN to be incomplete (deferred work, out-of-scope mirror, planned feature), pick the right pytest state:

| State | When | Effect on `make verify` |
|---|---|---|
| `assert ...` (hard fail) | The gap is IN SCOPE and must block now | RED — blocks everything. Use only when the gap is the thing being fixed. |
| `@pytest.mark.xfail(reason=..., strict=False)` | The gap is KNOWN and DEFERRED — track it, don't block | GREEN (xfail counts as expected). XPASS when fixed → signal to remove marker. |
| `@pytest.mark.skip(reason=...)` | The test can't run at all (missing dep, wrong OS) | GREEN but INVISIBLE — no signal when the blocker clears. Avoid for deferred-gap tracking. |

**Default for deferred gaps: `xfail`, not `skip`, not hard-fail.**
- `skip` hides the gap (no signal when it's fixed).
- hard-fail blocks unrelated work.
- `xfail` documents the gap, keeps the gate green, and AUTO-SIGNALS via XPASS when the gap closes.

## Why xfail beats "decouple the gate"

A tempting alternative is to move the failing test out of the `verify` chain into a separate target. But then the test only runs when someone remembers to run it. `xfail` keeps it IN the chain (runs every time) without breaking the chain — strictly better for drift detection.

## Scope-import smell

Before wiring a test into the gate, ask: **does this test assert on something the current scope owns?**
- Sandbox-scope work → tests must assert on sandbox state only.
- A test asserting on `Agent007/` (distribution mirror) inside the sandbox gate imports an out-of-scope concern. Either xfail it (if the mirror is deferred) or move it to a distribution-specific gate.

## Doc-line false-positives in static checks

When a test greps agent/skill bodies for an anti-pattern string (e.g. `Skill('` inline calls), remember the bodies often DOCUMENT the anti-pattern ("Do NOT invoke `Skill('name')` inline"). A naive substring check false-positives on the documentation. Use a doc-exception allowlist (lines containing "do not", "never", "recommend", "delegate to") — but know it's not airtight: `recommend X then Skill('foo')` slips past. Acceptable for a baseline drift test; document the looseness.

## Source

- `tests/agents/test_agent_role_contracts.py` (124 behavior tests + 1 xfail mirror-parity gate)
- P1.3 resolution context, 2026-05-27
