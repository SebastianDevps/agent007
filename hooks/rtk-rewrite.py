#!/usr/bin/env python3
"""
rtk-rewrite.py — PreToolUse hook (matcher: Bash)
Python port of rtk-rewrite.sh — cross-platform (macOS / Linux / Windows).

Rewrites eligible shell commands to run under RTK when available.
  REWRITE  if: RTK found AND command starts with an approved binary
  SKIP     if: RTK not found (silent passthrough)
  SKIP     if: command already starts with "rtk"
  SKIP     if: command contains pipes (|) or redirects (>, <)
  SKIP     if: command ends with / invokes a script (.sh, .py, .js)
  SKIP     if: command contains deploy / publish / release

Ultra-compact mode (-u) is applied automatically to high-noise commands.

Input  (stdin): Claude Code PreToolUse JSON
Output (stdout): {"continue": true}           — passthrough
                 {"tool_input": {"command": "rtk ..."}} — rewritten
"""

import json
import os
import platform
import shutil
import sys
from typing import Optional

# ── Approved leading binaries ──────────────────────────────────────────────────
APPROVED = {
    "git", "npm", "pnpm", "cargo", "pytest", "vitest",
    "docker", "kubectl", "bun", "npx",
    "eslint", "tsc", "jest", "playwright", "go", "rspec", "curl",
}

# ── Commands that get ultra-compact mode (-u) ──────────────────────────────────
ULTRA_COMPACT_PREFIXES = (
    "git log",
    "docker ps",
    "docker logs",
    "kubectl",
    "npm list",
    "pnpm list",
)

# ── Guards: substrings that force passthrough ──────────────────────────────────
PASSTHROUGH_SUBSTRINGS = ("|", ">", "<", "deploy", "publish", "release")
SCRIPT_EXTENSIONS      = (".sh", ".py", ".js")


def passthrough() -> None:
    print(json.dumps({"continue": True}))
    sys.exit(0)


def find_rtk() -> Optional[str]:
    """Return path to rtk binary or None if not available."""
    # 1. System PATH
    rtk = shutil.which("rtk")
    if rtk:
        return rtk

    # 2. Local .claude/bin/ (installed by rtk-bootstrap.py)
    hook_dir   = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.dirname(hook_dir)
    ext        = ".exe" if platform.system() == "Windows" else ""
    local      = os.path.join(plugin_dir, "bin", f"rtk{ext}")
    if os.path.isfile(local) and os.access(local, os.X_OK):
        return local

    return None


def main() -> None:
    raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        passthrough()

    # ── RTK availability ───────────────────────────────────────────────────────
    rtk_path = find_rtk()
    if not rtk_path:
        passthrough()

    # ── Extract command ────────────────────────────────────────────────────────
    cmd: str = (data.get("tool_input") or {}).get("command", "").strip()
    if not cmd:
        passthrough()

    # ── Guard: already prefixed ────────────────────────────────────────────────
    if cmd.startswith("rtk ") or cmd == "rtk":
        passthrough()

    # ── Guard: pipes, redirects, deploy context ────────────────────────────────
    for sub in PASSTHROUGH_SUBSTRINGS:
        if sub in cmd:
            passthrough()

    # ── Guard: script invocation ───────────────────────────────────────────────
    lead_token = cmd.split()[0] if cmd.split() else ""
    for ext in SCRIPT_EXTENSIONS:
        if lead_token.endswith(ext):
            passthrough()

    # ── Guard: approved binary only ────────────────────────────────────────────
    binary = lead_token.split(os.sep)[-1]  # strip path prefix if any
    if binary not in APPROVED:
        passthrough()

    # ── Build rewritten command ────────────────────────────────────────────────
    use_ultra = any(cmd.startswith(prefix) for prefix in ULTRA_COMPACT_PREFIXES)
    flag      = "-u " if use_ultra else ""
    new_cmd   = f"{rtk_path} {flag}{cmd}"

    # ── Emit rewrite ───────────────────────────────────────────────────────────
    output = dict(data)
    output.setdefault("tool_input", {})["command"] = new_cmd
    print(json.dumps(output))


if __name__ == "__main__":
    main()
