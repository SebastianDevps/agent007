#!/usr/bin/env python3
# CONTRACT EXCEPTION (v7-F1): multi-event (SessionStart + PostToolUse + Stop) — telemetry cross-cut
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


def extract_context_tokens(payload: dict):
    """Real source of tokens: payload['transcript_path'] is a JSONL with one
    line per message. Each assistant message has message.usage with:
       input_tokens + cache_creation_input_tokens + cache_read_input_tokens
    The sum is the CURRENT context size on that turn. We tail the file and
    use the most recent usage block.

    NOTE: PostToolUse payload itself does NOT carry context_window — earlier
    versions of this hook assumed it did, that was wrong. Confirmed empirically
    against Claude Code v0.x.

    Returns (used, total) or (None, None) if unavailable."""
    transcript = payload.get("transcript_path") or ""
    if not transcript or not os.path.exists(transcript):
        return None, None
    try:
        size = os.path.getsize(transcript)
        # Tail the last ~256KB — usage block is in every assistant message
        read_from = max(0, size - 262_144)
        with open(transcript, "rb") as f:
            f.seek(read_from)
            tail_bytes = f.read()
        # Decode lossy and split into lines; skip first partial line
        lines = tail_bytes.decode("utf-8", errors="replace").splitlines()
        if read_from > 0 and lines:
            lines = lines[1:]
        # Walk lines in reverse to find newest message.usage
        for line in reversed(lines):
            if not line.strip():
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = ev.get("message")
            if not isinstance(msg, dict):
                continue
            usage = msg.get("usage")
            if not isinstance(usage, dict):
                continue
            ipt = int(usage.get("input_tokens") or 0)
            cct = int(usage.get("cache_creation_input_tokens") or 0)
            crt = int(usage.get("cache_read_input_tokens") or 0)
            used = ipt + cct + crt
            if used > 0:
                return used, None  # total is inferred from model in caller
        return None, None
    except (OSError, ValueError):
        return None, None


def infer_context_total(model: str) -> int:
    """Map model id to its context window size. Defaults to 200k."""
    m = (model or "").lower()
    if "[1m]" in m or "1m" in m:
        return 1_000_000
    return 200_000


def extract_model(payload: dict) -> str:
    """Pull model id from payload — Claude Code may put it in several places.
    Falls back to env."""
    candidates = [
        payload.get("model"),
        payload.get("model_id"),
        (payload.get("model_info") or {}).get("id") if isinstance(payload.get("model_info"), dict) else None,
        (payload.get("session") or {}).get("model") if isinstance(payload.get("session"), dict) else None,
        (payload.get("hook_event_data") or {}).get("model") if isinstance(payload.get("hook_event_data"), dict) else None,
        os.environ.get("CLAUDE_MODEL", ""),
    ]
    for c in candidates:
        if c and isinstance(c, str):
            return c
    return ""


def persist_tokens(root: Path, used, total, model: str) -> None:
    """Write a small snapshot file the statusLine reads. Single file, atomic
    overwrite — fast (<5ms). statusline.sh reads this every status refresh."""
    if used is None or total is None or total <= 0:
        return
    snap = {
        "ts": now_iso(),
        "tokens_used": used,
        "tokens_total": total,
        "pct": round(used / total * 100, 1),
        "model": model,
    }
    try:
        path = root / ".sdlc" / "state" / "tokens.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(snap), encoding="utf-8")
    except OSError:
        pass


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
        # Pull real tokens from the transcript JSONL referenced in payload
        used, total = extract_context_tokens(payload)
        if used is None:
            used = env_int("CLAUDE_CONTEXT_TOKENS", 0)
        # Total context window: inferred from model since transcript doesn't carry it
        model = extract_model(payload)
        if not total:
            total = infer_context_total(model)
        ev = {
            **base,
            "type": "tool_use",
            "tool": tool,
            "tokens_now": used or 0,
        }
        if total:
            ev["tokens_total"] = total
        if file_target:
            ev["file"] = file_target
            if detect_reference_load(tool, file_target):
                ev["reference_load"] = True
        append_event(root, ev)
        # Side-effect: persist a snapshot for statusline.sh to read
        persist_tokens(root, used, total, model)
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
