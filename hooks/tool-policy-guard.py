#!/usr/bin/env python3
"""
tool-policy-guard.py — PreToolUse hook (Write | Edit | Bash)

Enforces tool_profile policies per active agent.
Complements safety-guard.py (which blocks destructive ops) by
blocking profile-inappropriate operations before they happen.

Profiles:
  minimal: Read, Glob, Grep, Bash (read-only commands: ls, cat, find, grep, git status/log/diff)
  coding:  + Write, Edit, Bash (all), Agent
  full:    everything allowed

Agent profile is read from .sdlc/state/session.json → stateJson.activeAgentProfile
OR from CLAUDE_AGENT_PROFILE env var (set by subagent-context.py if active).

Fallback: if no agent profile detected → allow (fail-open to not block normal usage).

Exit codes:
  0 = allow
  2 = block (profile violation)

Performance budget: < 20ms
"""

import json
import os
import re
import sys
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    sys.exit(0)

# Tools allowed per profile
PROFILES = {
    "minimal": {
        "tools": {"Read", "Glob", "Grep"},
        "bash_readonly": True,  # Only read-only bash commands
    },
    "coding": {
        "tools": {"Read", "Glob", "Grep", "Write", "Edit", "Bash", "Agent"},
        "bash_readonly": False,
    },
    "full": {
        "tools": None,  # None = everything allowed
        "bash_readonly": False,
    },
}

BASH_READONLY_PATTERNS = (
    r"^\s*(ls|cat|head|tail|find|grep|rg|git\s+(status|log|diff|branch|show)|echo|pwd|which|type|wc|sort|uniq|python3?\s+-c|node\s+-e)",
)


def find_project_root():
    current = Path(os.getcwd())
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    return Path(os.getcwd())


def get_active_agent_profile():
    """Read active agent's tool_profile from env or session state."""
    # Priority 1: env var (set by orchestrators)
    env_profile = os.environ.get("CLAUDE_AGENT_PROFILE", "").lower()
    if env_profile in PROFILES:
        return env_profile

    # Priority 2: session.json activeAgentProfile
    try:
        project_root = find_project_root()
        session_path = project_root / ".sdlc" / "state" / "session.json"
        if session_path.exists():
            state = json.loads(session_path.read_text())
            profile = state.get("stateJson", {}).get("activeAgentProfile", "")
            if profile in PROFILES:
                return profile
    except Exception:
        pass

    return None  # Unknown — fail-open


def is_bash_readonly(command: str) -> bool:
    for pattern in BASH_READONLY_PATTERNS:
        if re.match(pattern, command, re.IGNORECASE):
            return True
    return False


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name") or data.get("toolName") or ""
    tool_input = data.get("tool_input") or data.get("toolInput") or {}

    agent_profile_name = get_active_agent_profile()

    # Fail-open: if no agent profile detected, allow everything
    if agent_profile_name is None:
        sys.exit(0)

    policy = PROFILES[agent_profile_name]

    # Full profile: always allow
    if policy["tools"] is None:
        sys.exit(0)

    # Check if tool is in allowed set
    if tool_name not in policy["tools"] and tool_name != "Bash":
        if tool_name in ("Write", "Edit") and tool_name not in policy["tools"]:
            msg = (
                f"[tool-policy-guard] BLOCKED — profile violation\n"
                f"Active agent profile: '{agent_profile_name}'\n"
                f"Tool '{tool_name}' is not allowed in '{agent_profile_name}' profile.\n"
                f"Allowed tools: {sorted(policy['tools'])}\n"
                f"To use Write/Edit, the agent must have profile 'coding' or 'full'."
            )
            print(msg, file=sys.stderr)
            sys.exit(2)

    # Check Bash restrictions for minimal profile
    if tool_name == "Bash" and policy.get("bash_readonly"):
        command = tool_input.get("command", "")
        if command and not is_bash_readonly(command):
            msg = (
                f"[tool-policy-guard] BLOCKED — profile violation\n"
                f"Active agent profile: '{agent_profile_name}'\n"
                f"Bash command not allowed in '{agent_profile_name}' profile "
                f"(only read-only commands permitted).\n"
                f"Command: {command[:100]}\n"
                f"Allowed: ls, cat, find, grep, git status/log/diff, etc.\n"
                f"To run write operations, the agent must have profile 'coding' or 'full'."
            )
            print(msg, file=sys.stderr)
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
