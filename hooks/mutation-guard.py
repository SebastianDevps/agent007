#!/usr/bin/env python3
"""
mutation-guard.py — PreToolUse hook (Write | Edit | Bash)

Prevents duplicate mutations by fingerprinting file operations.
Inspired by OpenClaw's fail-closed mutation deduplication.

Behavior:
  - Write/Edit: fingerprint = SHA-256(file_path + operation + content[:500])
  - Bash (write-intent only): fingerprint = SHA-256(command[:500])
  - If fingerprint matches last operation on same file → BLOCK with helpful message
  - If no fingerprint info → allow with CAUTION flag
  - Fail-closed: when in doubt, allow (not block) — false positives are worse here

State file: .sdlc/state/mutation-state.json
  { "fingerprints": { "file_path": "last_hash" } }

Exit codes:
  0 = allow
  2 = block (duplicate mutation)

Performance budget: < 20ms
"""

import hashlib
import json
import os
import sys
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    sys.exit(0)

# Bash patterns that indicate a write-intent operation worth fingerprinting
WRITE_INTENT_PATTERNS = (
    "npm install", "npm i ", "pnpm install", "pnpm add",
    "pip install", "pip3 install",
    "git commit",
    "yarn add", "bun add",
)


def find_project_root() -> Path:
    current = Path(os.getcwd())
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    return Path(os.getcwd())


def load_state(state_path: Path) -> dict:
    try:
        if state_path.exists():
            return json.loads(state_path.read_text())
    except Exception:
        pass
    return {"fingerprints": {}}


def save_state(state_path: Path, state: dict) -> None:
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def build_write_fingerprint(file_path: str, content: str) -> str:
    raw = f"write:{file_path}:{content[:500]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def build_edit_fingerprint(file_path: str, old_string: str, new_string: str) -> str:
    raw = f"edit:{file_path}:{old_string[:200]}:{new_string[:200]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def build_bash_fingerprint(command: str) -> str:
    raw = f"bash:{command[:500]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def is_write_intent_bash(command: str) -> bool:
    cmd_lower = command.lower()
    return any(pattern in cmd_lower for pattern in WRITE_INTENT_PATTERNS)


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    tool_name = data.get("tool_name") or data.get("toolName") or ""
    tool_input = data.get("tool_input") or data.get("toolInput") or {}

    project_root = find_project_root()
    state_path = project_root / ".sdlc" / "state" / "mutation-state.json"
    state = load_state(state_path)

    fingerprint = None
    key = None  # State key to store fingerprint under

    if tool_name == "Write":
        file_path = tool_input.get("file_path", "")
        content = tool_input.get("content", "")
        if file_path and content:
            fingerprint = build_write_fingerprint(file_path, content)
            key = file_path

    elif tool_name == "Edit":
        file_path = tool_input.get("file_path", "")
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")
        if file_path and (old_string or new_string):
            fingerprint = build_edit_fingerprint(file_path, old_string, new_string)
            key = f"edit:{file_path}"

    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        if command and is_write_intent_bash(command):
            fingerprint = build_bash_fingerprint(command)
            key = f"bash:{command[:80]}"

    # No fingerprint computed — allow without tracking
    if fingerprint is None or key is None:
        sys.exit(0)

    existing = state["fingerprints"].get(key)

    if existing == fingerprint:
        # Duplicate mutation — block
        msg = (
            f"[mutation-guard] DUPLICATE MUTATION BLOCKED\n"
            f"Operation: {tool_name} on '{key}'\n"
            f"This exact operation was already applied in this session (fingerprint: {fingerprint}).\n"
            f"Skip this operation — the change is already in place.\n"
            f"If you intended a different change, modify the content first."
        )
        print(msg, file=sys.stderr)
        sys.exit(2)

    # New or different mutation — record and allow
    state["fingerprints"][key] = fingerprint
    save_state(state_path, state)
    sys.exit(0)


if __name__ == "__main__":
    main()
