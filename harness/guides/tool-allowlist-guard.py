#!/usr/bin/env python3
"""
tool-allowlist-guard.py — PreToolUse hook for Bash

Inspired by shadcn-ui SKILL.md pattern: each skill declares an `allowed-tools`
whitelist in its frontmatter (e.g., `Bash(npx shadcn@latest *)`). When that
skill is the active context, only Bash commands matching the whitelist may run.

Behavior:
    - Read the active-skill marker (if any) from .claude/state/active-skill.json
    - If no active skill → pass-through (no whitelist enforced)
    - If active skill has `allowed-tools` patterns:
        * Match the proposed Bash command against any pattern
        * Match → allow
        * No match → BLOCK with a helpful message
    - If active skill exists but has NO `allowed-tools` declared → pass-through
      (skills opt in to enforcement; not declaring is "all bash allowed")

Pattern matching:
    Each entry is a glob-ish "Bash(<pattern>)" form. The pattern after the
    "Bash(" prefix is matched as a prefix on the command string, with `*`
    treated as a wildcard. Examples:
        Bash(git status)        → matches exactly "git status"
        Bash(git *)             → matches any "git ..."
        Bash(npx shadcn@* *)    → matches "npx shadcn@latest info" etc.

State file format (.claude/state/active-skill.json):
    {"name": "<skill-name>", "allowed_tools": ["Bash(git *)", "Bash(npm test)"]}

Performance budget: < 30ms (single file read + regex match).

Profile gating:
    PROFILE=minimal → no-op
"""

from __future__ import annotations

import fnmatch
import json
import os
import sys
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)


def parse_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def project_root() -> Path:
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


def load_active_skill(root: Path) -> dict | None:
    state_path = root / ".claude" / "state" / "active-skill.json"
    if not state_path.exists():
        return None
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def extract_pattern(entry: str) -> str | None:
    """Extract the inner pattern from `Bash(<pattern>)`."""
    entry = entry.strip()
    if not entry.startswith("Bash(") or not entry.endswith(")"):
        return None
    return entry[len("Bash("):-1]


def matches_any(command: str, patterns: list[str]) -> bool:
    cmd = command.strip()
    for raw in patterns:
        pattern = extract_pattern(raw)
        if pattern is None:
            continue
        # fnmatch treats * as wildcard. Anchor at start.
        if fnmatch.fnmatchcase(cmd, pattern) or fnmatch.fnmatchcase(cmd, pattern + "*"):
            return True
        # Also support prefix-only patterns without trailing *
        if not pattern.endswith("*") and cmd == pattern:
            return True
        if pattern.endswith("*") and cmd.startswith(pattern[:-1]):
            return True
    return False


def block(message: str) -> None:
    print(json.dumps({
        "decision": "block",
        "reason": f"[tool-allowlist-guard] {message}",
    }))
    sys.exit(0)


def allow() -> None:
    print(json.dumps({"continue": True}))
    sys.exit(0)


def main() -> None:
    payload = parse_payload()
    tool = payload.get("tool_name") or payload.get("toolName") or ""
    if tool != "Bash":
        allow()

    inp = (
        payload.get("tool_input")
        or payload.get("toolInput")
        or payload.get("input")
        or {}
    )
    command = inp.get("command") or ""
    if not command:
        allow()

    root = project_root()
    skill = load_active_skill(root)
    if not skill:
        allow()

    allowed = skill.get("allowed_tools") or skill.get("allowed-tools") or []
    if not isinstance(allowed, list) or not allowed:
        allow()

    if matches_any(command, allowed):
        allow()

    name = skill.get("name", "<unknown>")
    block(
        f"Skill '{name}' has an allowed-tools whitelist that does not match this command:\n"
        f"  Command: {command}\n"
        f"  Whitelist: {', '.join(allowed)}\n"
        "If this command is legitimate, update the skill's frontmatter `allowed-tools` "
        "or clear .claude/state/active-skill.json to deactivate enforcement."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Fail open
        print(json.dumps({"continue": True}))
        sys.exit(0)
