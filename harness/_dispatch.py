#!/usr/bin/env python3
"""_dispatch.py — single entry point for harness hooks.

Resolves a hook script relative to this file's directory (the harness root),
then runs it with the current Python interpreter, passing stdin/stdout/stderr
through transparently. Exits with the child's exit code.

Usage from settings.json:
    python3 .claude/harness/_dispatch.py guides/path-existence-guard.py

The dispatcher does the HOOK_ROOT discovery that the previous POSIX
while-loop did inline — but in cross-platform Python.
"""

from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("_dispatch.py: missing hook script argument\n")
        return 2

    harness_dir = Path(__file__).resolve().parent
    project_root = harness_dir.parent.parent
    rel_script = sys.argv[1]
    script_path = (harness_dir / rel_script).resolve()

    # Containment check: script must live under harness_dir
    try:
        script_path.relative_to(harness_dir)
    except ValueError:
        sys.stderr.write(
            f"_dispatch.py: refusing to run script outside harness: {script_path}\n"
        )
        return 2

    if not script_path.is_file():
        sys.stderr.write(f"_dispatch.py: script not found: {script_path}\n")
        return 2

    # Chdir to project root so relative paths inside hooks still resolve
    # (mirrors the old `cd "$HOOK_ROOT" && python3 ...` behavior).
    os.chdir(project_root)

    completed = subprocess.run(
        [sys.executable, str(script_path), *sys.argv[2:]],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
