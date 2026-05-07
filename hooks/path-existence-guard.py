#!/usr/bin/env python3
"""
path-existence-guard.py — PreToolUse hook for Edit / Write / Read

Validates that the target path of an Edit / Read operation exists. For Write
operations, validates that the PARENT directory exists (so we don't create
files in hallucinated directories).

Why this exists:
    LLMs frequently hallucinate file paths under pressure. Editing a non-existent
    file with create_if_missing semantics silently creates rogue files; reading
    one wastes tool calls. This hook catches both before they happen.

Behavior:
    - Edit / Read on a path that does not exist → BLOCK with helpful suggestion
    - Write on a path whose parent directory does not exist → BLOCK
    - All other tools → pass-through (exit 0)

Allowed exceptions (Write only — file may not exist yet):
    - Path is under a known-creation manifest: .sdlc/state/, /tmp/, .claude/state/
    - Path matches an env-allowed prefix: PATH_EXISTENCE_ALLOWLIST (colon-separated)

Performance budget: < 50ms.

Profile gating:
    PROFILE=minimal → no-op
"""

import json
import os
import sys
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)

CREATION_ALLOWLIST_PREFIXES = (
    ".sdlc/state/",
    ".claude/state/",
    "/tmp/",
    "var/log/",
)


def parse_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def get_tool(payload: dict) -> str:
    return payload.get("tool_name") or payload.get("toolName") or ""


def get_input(payload: dict) -> dict:
    return (
        payload.get("tool_input")
        or payload.get("toolInput")
        or payload.get("input")
        or {}
    )


def project_root() -> Path:
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


def is_creation_allowlisted(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    rel_str = str(rel).replace(os.sep, "/")
    if any(rel_str.startswith(p) for p in CREATION_ALLOWLIST_PREFIXES):
        return True
    extra = os.environ.get("PATH_EXISTENCE_ALLOWLIST", "")
    for prefix in (p.strip() for p in extra.split(":") if p.strip()):
        if rel_str.startswith(prefix):
            return True
    return False


def block(message: str) -> None:
    print(json.dumps({
        "decision": "block",
        "reason": f"[path-existence-guard] {message}",
    }))
    sys.exit(0)


def allow() -> None:
    print(json.dumps({"continue": True}))
    sys.exit(0)


def main() -> None:
    payload = parse_payload()
    tool = get_tool(payload)
    if tool not in ("Edit", "Write", "Read"):
        allow()

    inp = get_input(payload)
    raw_path = inp.get("file_path") or inp.get("path") or ""
    if not raw_path:
        allow()

    target = Path(raw_path)
    if not target.is_absolute():
        target = project_root() / target

    if tool == "Read":
        if not target.exists():
            block(
                f"Read target does not exist: {target}\n"
                "Use Glob/Grep to find the real path before Read, or correct the path."
            )
        allow()

    if tool == "Edit":
        if not target.exists():
            block(
                f"Edit target does not exist: {target}\n"
                "Edit requires an existing file. Use Write to create new files, "
                "or Glob to confirm the real path."
            )
        allow()

    # tool == "Write"
    parent = target.parent
    if parent.exists():
        allow()

    root = project_root()
    if is_creation_allowlisted(target, root):
        allow()

    block(
        f"Write parent directory does not exist: {parent}\n"
        "Verify the path or run mkdir explicitly first. If this is an intentional "
        "new directory, add a prefix to PATH_EXISTENCE_ALLOWLIST or place under "
        f"one of: {', '.join(CREATION_ALLOWLIST_PREFIXES)}."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never block tool use on hook bug — fail open
        print(json.dumps({"continue": True}))
        sys.exit(0)
