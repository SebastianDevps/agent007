#!/usr/bin/env python3
"""
welcome.py — SessionStart Hook: Deterministic Status Banner

Delegates ecosystem state collection to agent007-init.js and prints
a single formatted line to stderr:

  Agent007 v5 | 28 skills | 5 agents | branch: main | RTK: ✓ | Task: none

No ASCII art. No marker file gating.
Always emits valid JSON (empty object) to avoid additionalContext noise.
"""

import json
import os
import subprocess
import sys


def _find_project_root() -> str:
    cwd = os.getcwd()
    current = cwd
    while current != os.path.dirname(current):
        if os.path.isdir(os.path.join(current, ".claude")):
            return current
        current = os.path.dirname(current)
    return cwd


def main() -> None:
    try:
        sys.stdin.read()
    except Exception:
        pass

    project_root = _find_project_root()
    init_script = os.path.join(project_root, ".claude", "scripts", "agent007-init.js")

    banner = "Agent007 v5"  # fallback if script fails

    try:
        result = subprocess.run(
            ["node", init_script, "--oneline"],
            capture_output=True,
            text=True,
            timeout=1.5,  # generous — init targets < 50ms but allow cold start
        )
        if result.returncode == 0 and result.stdout.strip():
            banner = result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass  # use fallback banner — never block session start

    sys.stderr.write(banner + "\n")
    sys.stderr.flush()

    print(json.dumps({}))
    sys.exit(0)


if __name__ == "__main__":
    main()
