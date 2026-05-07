#!/usr/bin/env python3
"""
context-tick.py — Telemetry hook (SessionStart + PostToolUse)

Persists per-session telemetry as JSONL so we can audit what the plugin
actually costs in production. Inspired by claude-mem's session tracking.

Captures:
  - SessionStart: session_id, model, timestamp, model_budget
  - PostToolUse: tool_name, file_target (for Read/Edit/Write), token estimate
                  if CLAUDE_CONTEXT_TOKENS env is set
  - Stop:        session_id, total_tool_calls, references_loaded[], duration_seconds

Output: .sdlc/state/context-budget.jsonl (append-only)
        each line is a JSON event with type field

Profile gating: PROFILE=minimal → no-op
Performance budget: < 10ms per call (append + flush)

Why JSONL not JSON:
  Append-only is atomic per line — no read-modify-write race when multiple
  hooks fire concurrently. waste-report.py reads it back as a stream.
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)


def project_root() -> Path:
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def jsonl_path(root: Path) -> Path:
    p = root / ".sdlc" / "state" / "context-budget.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def append_event(root: Path, event: dict) -> None:
    try:
        path = jsonl_path(root)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except OSError:
        pass


def parse_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def hook_event(payload: dict) -> str:
    """Best-effort detection of which lifecycle event fired."""
    if "tool_name" in payload or "toolName" in payload:
        return "post_tool_use"
    if payload.get("event") == "SessionStart" or "session_id" in payload and not payload.get("tool_name"):
        return "session_start"
    if payload.get("event") == "Stop" or payload.get("type") == "stop":
        return "stop"
    return "unknown"


def env_int(name: str, default: int = 0) -> int:
    raw = os.environ.get(name, "")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def detect_reference_load(tool_name: str, file_path: str) -> bool:
    return tool_name == "Read" and "/references/" in (file_path or "")


def main() -> None:
    payload = parse_payload()
    root = project_root()
    event_type = hook_event(payload)

    base = {
        "ts": now_iso(),
        "session_id": payload.get("session_id")
            or (payload.get("hook_event_data") or {}).get("session_id")
            or os.environ.get("CLAUDE_SESSION_ID", "unknown"),
    }

    if event_type == "session_start":
        append_event(root, {
            **base,
            "type": "session_start",
            "model": os.environ.get("CLAUDE_MODEL", ""),
            "model_budget": env_int("CLAUDE_MAX_TOKENS", 200_000),
            "tokens_at_start": env_int("CLAUDE_CONTEXT_TOKENS", 0),
        })
    elif event_type == "post_tool_use":
        tool = payload.get("tool_name") or payload.get("toolName") or ""
        inp = (
            payload.get("tool_input")
            or payload.get("toolInput")
            or payload.get("input")
            or {}
        )
        file_target = inp.get("file_path") or inp.get("path") or ""
        ev = {
            **base,
            "type": "tool_use",
            "tool": tool,
            "tokens_now": env_int("CLAUDE_CONTEXT_TOKENS", 0),
        }
        if file_target:
            ev["file"] = file_target
            if detect_reference_load(tool, file_target):
                ev["reference_load"] = True
        append_event(root, ev)
    elif event_type == "stop":
        append_event(root, {
            **base,
            "type": "session_stop",
            "tokens_at_stop": env_int("CLAUDE_CONTEXT_TOKENS", 0),
        })
    # else: unknown event — silent skip

    print(json.dumps({"continue": True}))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Telemetry must never block tool use
        print(json.dumps({"continue": True}))
        sys.exit(0)
