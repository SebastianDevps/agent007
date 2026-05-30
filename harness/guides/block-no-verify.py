#!/usr/bin/env python3
"""
block-no-verify.py — PreToolUse hook (matcher: Bash)

Blocks any git command that includes --no-verify flag, which would
bypass pre-commit and commit-msg hooks.

Input  (stdin): Claude Code PreToolUse JSON with tool_name=Bash
Output (stdout):
  block    → {"decision": "block", "reason": "..."}
  passthru → original stdin unchanged

Performance: < 5ms (no subprocess — pure string check)
"""

import json
import re
import sys


def main() -> None:
    raw = sys.stdin.read()

    try:
        data = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, ValueError):
        sys.stdout.write(raw)
        sys.exit(0)

    tool_name = data.get("tool_name") or data.get("toolName") or ""
    if tool_name != "Bash":
        sys.stdout.write(raw)
        sys.exit(0)

    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    command = tool_input.get("command") or ""

    # Check if it's a git command containing --no-verify
    is_git = re.match(r'\s*git\b', command)
    has_no_verify = re.search(r'--no-verify\b', command)

    if is_git and has_no_verify:
        sys.stderr.write(f"block-no-verify: BLOCKED — --no-verify detected in: {command[:80]}\n")
        sys.stderr.flush()
        response = {
            "decision": "block",
            "reason": (
                "The --no-verify flag bypasses pre-commit quality checks. "
                "Fix the underlying issue instead of skipping validation. "
                "If this is intentional, ask the user to run the command manually."
            ),
        }
        sys.stdout.write(json.dumps(response))
        sys.exit(0)

    sys.stdout.write(raw)
    sys.exit(0)


if __name__ == "__main__":
    main()
