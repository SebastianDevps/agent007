#!/usr/bin/env python3
"""
test-hooks.py — Hook regression tester (zero external deps)

Runs each hook with simulated stdin payloads from fixtures/*.json. Verifies
the hook's stdout decision matches the expected outcome. Catches regressions
like the mutation-guard fingerprint bug before they hit a real session.

Test format (fixtures/<hook-name>--<scenario>.json):
{
  "hook": "path-existence-guard",        # script in .claude/hooks/<hook>.py
  "stdin": { ... payload sent to hook },
  "env": { "KEY": "VALUE" },             # optional env overrides
  "expect": {
    "decision": "block" | "allow",       # "allow" matches {continue: true}
    "reason_contains": "..."             # optional substring match in reason
  }
}

Exit code:
  0 = all tests pass
  1 = at least one failure or runtime error

Run:
  .claude/scripts/lifecycle/test-hooks.py             # all fixtures
  .claude/scripts/lifecycle/test-hooks.py --filter mutation-guard
  .claude/scripts/lifecycle/test-hooks.py --quiet
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIXTURES_DIR = Path(__file__).parent / "fixtures"
HOOKS_DIR = ROOT / ".claude" / "hooks"


class TestResult:
    def __init__(self, name: str, ok: bool, message: str = "") -> None:
        self.name = name
        self.ok = ok
        self.message = message


def load_fixtures(filter_str: str | None) -> list[Path]:
    if not FIXTURES_DIR.is_dir():
        return []
    files = sorted(p for p in FIXTURES_DIR.glob("*.json"))
    if filter_str:
        files = [p for p in files if filter_str in p.name]
    return files


def run_hook(hook_name: str, stdin_payload: dict, env_overrides: dict) -> tuple[int, str, str]:
    hook_path = HOOKS_DIR / f"{hook_name}.py"
    if not hook_path.exists():
        return -1, "", f"hook script not found: {hook_path}"
    env = os.environ.copy()
    env.update(env_overrides or {})
    proc = subprocess.run(
        ["python3", str(hook_path)],
        input=json.dumps(stdin_payload).encode(),
        capture_output=True,
        env=env,
        cwd=str(ROOT),
        timeout=10,
    )
    return proc.returncode, proc.stdout.decode(errors="replace"), proc.stderr.decode(errors="replace")


def parse_decision(stdout: str) -> tuple[str, str]:
    """Map hook stdout JSON to ('block'|'allow', reason)."""
    stdout = stdout.strip()
    if not stdout:
        return "allow", ""  # silent exit = allow
    try:
        out = json.loads(stdout.splitlines()[-1])
    except json.JSONDecodeError:
        return "unknown", stdout
    if isinstance(out, dict):
        if out.get("decision") == "block":
            return "block", str(out.get("reason", ""))
        if out.get("continue") is True:
            return "allow", ""
        # `{}` or `{"hookSpecificOutput": ...}` = silent allow (no decision = pass)
        if "decision" not in out and out.get("continue") is None:
            return "allow", ""
    return "unknown", stdout


def evaluate(fixture: Path, expected: dict, decision: str, reason: str, exit_code: int) -> TestResult:
    name = fixture.stem
    want_decision = expected.get("decision", "allow")
    if decision != want_decision:
        return TestResult(
            name, False,
            f"expected decision={want_decision}, got decision={decision} (exit {exit_code}); reason={reason[:160]}",
        )
    want_reason = expected.get("reason_contains")
    if want_reason and want_reason not in reason:
        return TestResult(
            name, False,
            f"reason did not contain '{want_reason}'; got: {reason[:200]}",
        )
    return TestResult(name, True)


def run_one(fixture: Path) -> TestResult:
    try:
        spec = json.loads(fixture.read_text(encoding="utf-8"))
    except Exception as e:
        return TestResult(fixture.stem, False, f"could not load fixture: {e}")
    hook = spec.get("hook")
    if not hook:
        return TestResult(fixture.stem, False, "fixture missing 'hook' field")
    rc, stdout, stderr = run_hook(hook, spec.get("stdin") or {}, spec.get("env") or {})
    if rc < 0:
        return TestResult(fixture.stem, False, stderr.strip() or "hook execution failed")
    decision, reason = parse_decision(stdout)
    return evaluate(fixture, spec.get("expect") or {}, decision, reason, rc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", default=None, help="substring filter on fixture name")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    fixtures = load_fixtures(args.filter)
    if not fixtures:
        print(f"No fixtures found in {FIXTURES_DIR}{' matching filter' if args.filter else ''}.", file=sys.stderr)
        return 1

    results: list[TestResult] = []
    for fx in fixtures:
        results.append(run_one(fx))

    passed = sum(1 for r in results if r.ok)
    failed = len(results) - passed

    if not args.quiet or failed:
        print(f"test-hooks.py — {len(results)} fixtures")
        for r in results:
            mark = "✓" if r.ok else "✗"
            line = f"  {mark} {r.name}"
            if not r.ok:
                line += f"\n    {r.message}"
            print(line if r.ok else line, file=sys.stdout if r.ok else sys.stderr)

    print()
    if failed:
        print(f"FAIL — {failed} failed, {passed} passed", file=sys.stderr)
        return 1
    print(f"OK — {passed} passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
