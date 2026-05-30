#!/usr/bin/env python3
"""guides/emit-criteria-hook.py — PostToolUse hook: emit criteria.md after spec.md write.

Fires on Write|Edit targeting openspec/changes/*/spec.md.
Derives change-dir from the target path and calls emit_criteria.py.
Fail-open: any error exits 0 (never blocks tool use).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

SPEC_SUFFIX = "spec.md"


def project_root() -> Path:
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0

    tool_input = (
        payload.get("tool_input")
        or payload.get("toolInput")
        or payload.get("input")
        or {}
    )
    target = tool_input.get("file_path") or tool_input.get("path") or ""
    if not target:
        return 0

    root = project_root()
    target_path = Path(target) if Path(target).is_absolute() else root / target
    rel = None
    try:
        rel = target_path.relative_to(root)
    except ValueError:
        return 0

    parts = rel.parts
    if len(parts) != 4:
        return 0
    if parts[0] != "openspec" or parts[1] != "changes":
        return 0
    if parts[3] != SPEC_SUFFIX:
        return 0

    change_dir = root / "openspec" / "changes" / parts[2].split("/")[0]
    change_dir = target_path.parent

    emit_script = root / "scripts" / "spec" / "emit_criteria.py"
    if not emit_script.is_file():
        return 0

    try:
        subprocess.run(
            [sys.executable, str(emit_script), str(change_dir)],
            cwd=str(root),
            timeout=10,
        )
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
