#!/usr/bin/env python3
"""
test-mutation-guard.py — Verification test for hooks/mutation-guard.py

Tests:
  1. Write same content twice → second is BLOCKED (exit 2)
  2. Write different content to same file → allowed (exit 0)
  3. Edit same old/new strings twice → second is BLOCKED
  4. Bash npm install twice → second is BLOCKED
  5. Bash read-only command → always allowed (not tracked)

Usage:
  python3 .claude/scripts/test-mutation-guard.py

Exit 0 = all tests passed
Exit 1 = one or more tests failed
"""

import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "mutation-guard.py"
BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / ".sdlc" / "state" / "mutation-state.json"


def run_hook(tool_name: str, tool_input: dict) -> tuple[int, str, str]:
    payload = json.dumps({"tool_name": tool_name, "tool_input": tool_input})
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_HOOK_PROFILE": "standard"},
    )
    return result.returncode, result.stdout, result.stderr


def reset_state() -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"fingerprints": {}}))


def test_duplicate_write_blocked() -> bool:
    """Write same content twice → second call blocked."""
    reset_state()
    tool_input = {"file_path": "/tmp/test.ts", "content": "const x = 1;"}

    code1, _, _ = run_hook("Write", tool_input)
    code2, _, stderr2 = run_hook("Write", tool_input)

    passed = code1 == 0 and code2 == 2 and "DUPLICATE" in stderr2
    print(f"  {'✓' if passed else '✗'} test_duplicate_write_blocked: first={code1}, second={code2}, msg={'yes' if 'DUPLICATE' in stderr2 else 'no'}")
    return passed


def test_different_write_allowed() -> bool:
    """Write different content to same file → allowed."""
    reset_state()

    code1, _, _ = run_hook("Write", {"file_path": "/tmp/test.ts", "content": "const x = 1;"})
    code2, _, _ = run_hook("Write", {"file_path": "/tmp/test.ts", "content": "const x = 2;"})

    passed = code1 == 0 and code2 == 0
    print(f"  {'✓' if passed else '✗'} test_different_write_allowed: first={code1}, second={code2}")
    return passed


def test_duplicate_edit_blocked() -> bool:
    """Same edit twice → second blocked."""
    reset_state()
    tool_input = {
        "file_path": "/tmp/test.ts",
        "old_string": "const x = 1;",
        "new_string": "const x = 2;",
    }

    code1, _, _ = run_hook("Edit", tool_input)
    code2, _, stderr2 = run_hook("Edit", tool_input)

    passed = code1 == 0 and code2 == 2 and "DUPLICATE" in stderr2
    print(f"  {'✓' if passed else '✗'} test_duplicate_edit_blocked: first={code1}, second={code2}")
    return passed


def test_duplicate_npm_install_blocked() -> bool:
    """npm install same packages twice → second blocked."""
    reset_state()
    tool_input = {"command": "npm install lodash"}

    code1, _, _ = run_hook("Bash", tool_input)
    code2, _, stderr2 = run_hook("Bash", tool_input)

    passed = code1 == 0 and code2 == 2 and "DUPLICATE" in stderr2
    print(f"  {'✓' if passed else '✗'} test_duplicate_npm_install_blocked: first={code1}, second={code2}")
    return passed


def test_readonly_bash_not_tracked() -> bool:
    """ls or cat commands → always allowed, not tracked."""
    reset_state()
    tool_input = {"command": "ls -la"}

    code1, _, _ = run_hook("Bash", tool_input)
    code2, _, _ = run_hook("Bash", tool_input)

    passed = code1 == 0 and code2 == 0
    print(f"  {'✓' if passed else '✗'} test_readonly_bash_not_tracked: first={code1}, second={code2}")
    return passed


def main() -> None:
    print("=== mutation-guard.py verification ===\n")
    results = [
        test_duplicate_write_blocked(),
        test_different_write_allowed(),
        test_duplicate_edit_blocked(),
        test_duplicate_npm_install_blocked(),
        test_readonly_bash_not_tracked(),
    ]
    reset_state()
    passed = sum(results)
    total = len(results)
    print(f"\n{'✅' if passed == total else '❌'} {passed}/{total} tests passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
