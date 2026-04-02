#!/usr/bin/env python3
"""
test-loop-detection.py — Verification test for hooks/tool-loop-detection.py

Tests:
  1. 10 identical calls → WARNING in output (non-blocking)
  2. 30 identical calls → CIRCUIT BREAKER (exit 2)
  3. Ping-pong: 6 alternating calls → CIRCUIT BREAKER (exit 2)
  4. benign tools (Read) → always pass through (no tracking)

Usage:
  python3 .claude/scripts/test-loop-detection.py

Exit 0 = all tests passed
Exit 1 = one or more tests failed
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "tool-loop-detection.py"
BASE_DIR = Path(__file__).parent.parent.parent
STATE_FILE = BASE_DIR / ".sdlc" / "state" / "loop-state.json"


def run_hook(tool_name: str, tool_input: dict, tool_response: dict, state=None):  # -> tuple[int, str, str]
    """Run the hook with given inputs. Returns (exit_code, stdout, stderr)."""
    if state is not None:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(state))

    payload = json.dumps({
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_response": tool_response,
    })

    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        env={**os.environ, "CLAUDE_HOOK_PROFILE": "standard"},
    )
    return result.returncode, result.stdout, result.stderr


def reset_state() -> None:
    if STATE_FILE.exists():
        STATE_FILE.write_text(json.dumps({"window": [], "circuit_broken": False}))


def build_state_with_n_identical(n: int, tool: str = "Bash") -> dict:
    """Build a loop-state with N identical fingerprints already in window."""
    import hashlib
    params = {"command": "echo test"}
    outcome = {"output": "test"}
    params_str = json.dumps(params, sort_keys=True)[:500]
    outcome_str = json.dumps(outcome, sort_keys=True)[:200]
    raw = f"{tool}:{params_str}:{outcome_str}"
    fp = hashlib.sha256(raw.encode()).hexdigest()[:16]
    window = [{"hash": fp, "tool": tool, "ts": 1000 + i} for i in range(n)]
    return {"window": window, "circuit_broken": False}


def test_warning_at_10() -> bool:
    """Test: 10 identical calls → warning in output."""
    reset_state()
    # Pre-fill 9 identical entries
    state = build_state_with_n_identical(9)

    exit_code, stdout, stderr = run_hook(
        "Bash",
        {"command": "echo test"},
        {"output": "test"},
        state=state,
    )
    passed = exit_code == 0 and "WARNING" in stdout
    print(f"  {'✓' if passed else '✗'} test_warning_at_10: exit={exit_code}, warning={'yes' if 'WARNING' in stdout else 'no'}")
    return passed


def test_circuit_breaker_at_30() -> bool:
    """Test: 30 identical calls → circuit breaker (exit 2)."""
    reset_state()
    state = build_state_with_n_identical(29)

    exit_code, stdout, stderr = run_hook(
        "Bash",
        {"command": "echo test"},
        {"output": "test"},
        state=state,
    )
    passed = exit_code == 2 and "CIRCUIT BREAKER" in stderr
    print(f"  {'✓' if passed else '✗'} test_circuit_breaker_at_30: exit={exit_code}, circuit_breaker={'yes' if 'CIRCUIT BREAKER' in stderr else 'no'}")
    return passed


def test_benign_tool_passthrough() -> bool:
    """Test: Read tool always passes through."""
    reset_state()
    state = build_state_with_n_identical(29, tool="Read")

    # Even with 29 identical Read entries, should pass
    exit_code, stdout, stderr = run_hook(
        "Read",
        {"file_path": "/some/file.py"},
        {"content": "some content"},
        state=state,
    )
    passed = exit_code == 0
    print(f"  {'✓' if passed else '✗'} test_benign_tool_passthrough: exit={exit_code}")
    return passed


def test_ping_pong_detection() -> bool:
    """Test: 6 alternating calls → circuit breaker."""
    import hashlib

    def make_fp(tool, cmd):
        params = {"command": cmd}
        params_str = json.dumps(params, sort_keys=True)[:500]
        raw = f"{tool}:{params_str}:"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    fp_a = make_fp("Bash", "echo a")
    fp_b = make_fp("Bash", "echo b")
    # Build [A, B, A, B, A] — 5 entries. Hook will append B → [A,B,A,B,A,B] → ping-pong
    window = [
        {"hash": fp_a, "tool": "Bash", "ts": 0},
        {"hash": fp_b, "tool": "Bash", "ts": 1},
        {"hash": fp_a, "tool": "Bash", "ts": 2},
        {"hash": fp_b, "tool": "Bash", "ts": 3},
        {"hash": fp_a, "tool": "Bash", "ts": 4},
    ]
    state = {"window": window, "circuit_broken": False}

    exit_code, stdout, stderr = run_hook(
        "Bash",
        {"command": "echo b"},
        {},
        state=state,
    )
    passed = exit_code == 2 and "PING-PONG" in stderr
    print(f"  {'✓' if passed else '✗'} test_ping_pong_detection: exit={exit_code}, ping_pong={'yes' if 'PING-PONG' in stderr else 'no'}")
    return passed


def main() -> None:
    print("=== tool-loop-detection.py verification ===\n")
    results = [
        test_warning_at_10(),
        test_circuit_breaker_at_30(),
        test_benign_tool_passthrough(),
        test_ping_pong_detection(),
    ]
    reset_state()
    passed = sum(results)
    total = len(results)
    print(f"\n{'✅' if passed == total else '❌'} {passed}/{total} tests passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
