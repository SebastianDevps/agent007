#!/usr/bin/env python3
"""
lifecycle-clock-out.py — Stop hook (REQ-2).

Fires on the Stop event. Appends a clock-out line to .sdlc/state/session-log.jsonl,
computes duration_s from the matching clock-in (same session_id), and creates or
updates .sdlc/state/session-summary-<YYYY-MM-DD>.md (SC-2.4 AMENDADO: append trailing
line if file already exists, do not overwrite).

Fail-open: any exception is caught, logged to stderr, exit 0.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# PROFILE=minimal short-circuit — no file I/O
if os.environ.get("CLAUDE_HOOK_PROFILE") == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)

# Make sibling imports available
_sensors_dir = Path(__file__).parent
if str(_sensors_dir) not in sys.path:
    sys.path.insert(0, str(_sensors_dir))

from _lifecycle_common import (  # noqa: E402
    DEFAULT_RECOVERY_WINDOW_HOURS,
    TAIL_LINES,
    append_jsonl,
    now_iso,
    parse_payload,
    project_root,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_matching_clock_in(log_path: Path, session_id: str):
    """Read tail of session-log.jsonl and return ts of last matching clock-in.

    Returns an ISO-8601 string or None.
    """
    if not log_path.exists():
        return None
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
        tail = lines[-TAIL_LINES:]
        for raw in reversed(tail):
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if entry.get("type") == "clock-in" and entry.get("session_id") == session_id:
                return entry.get("ts")
    except (IOError, OSError):
        pass
    return None


def _count_tool_calls(budget_path: Path, session_id: str):
    """Count tool_use entries in context-budget.jsonl for this session_id.

    Returns int >= 0 if matching entries found, or None if file absent,
    unreadable, or contains no entries for this session_id (indeterminate).
    """
    if not budget_path.exists():
        return None
    try:
        lines = budget_path.read_text(encoding="utf-8").splitlines()
        tail = lines[-500:]
        count = 0
        found_session = False
        for raw in tail:
            raw = raw.strip()
            if not raw:
                continue
            try:
                entry = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if entry.get("type") == "tool_use" and entry.get("session_id") == session_id:
                found_session = True
                count += 1
        # No matching session_id entries → indeterminate (not "zero tools used")
        if not found_session:
            return None
        return count
    except (IOError, OSError):
        return None


def _compute_duration_s(clock_in_ts: str):
    """Compute integer seconds between clock_in_ts and now. Returns int >= 0."""
    try:
        clock_in_dt = datetime.fromisoformat(clock_in_ts)
        delta = datetime.now(timezone.utc) - clock_in_dt
        return max(0, int(delta.total_seconds()))
    except (ValueError, TypeError):
        return None


def _ensure_session_summary(state_dir: Path, ts: str, session_id: str, duration_s):
    """Create scaffold if absent, append trailing line if present (SC-2.4 AMENDADO)."""
    today = datetime.now().strftime("%Y-%m-%d")
    summary_path = state_dir / f"session-summary-{today}.md"
    state_dir.mkdir(parents=True, exist_ok=True)

    if not summary_path.exists():
        scaffold = (
            "## What we worked on\n\n"
            "## Decisions\n\n"
            "## Files touched\n\n"
            "## Next steps\n"
        )
        summary_path.write_text(scaffold, encoding="utf-8")
    else:
        # SC-2.4 AMENDADO: append single trailing line preserving all prior content
        duration_label = f"{duration_s}s" if duration_s is not None else "unknown"
        trailing = f"\n> Clock-out @ {ts}, duration: {duration_label}\n"
        with summary_path.open("a", encoding="utf-8") as fh:
            fh.write(trailing)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    payload = parse_payload()

    session_id = (
        payload.get("session_id")
        or os.environ.get("CLAUDE_SESSION_ID", "")
    )

    root = project_root()
    state_dir = root / ".sdlc" / "state"
    log_path = state_dir / "session-log.jsonl"
    budget_path = state_dir / "context-budget.jsonl"

    clock_in_ts = _find_matching_clock_in(log_path, session_id)
    duration_s = _compute_duration_s(clock_in_ts) if clock_in_ts else None
    tool_calls = _count_tool_calls(budget_path, session_id)

    ts = now_iso()
    event = {
        "ts": ts,
        "session_id": session_id,
        "type": "clock-out",
        "duration_s": duration_s,
        "tool_calls": tool_calls,
    }

    stop_reason = payload.get("stop_reason")
    if stop_reason is not None:
        event["stop_reason"] = stop_reason

    append_jsonl(log_path, event)
    _ensure_session_summary(state_dir, ts, session_id, duration_s)

    return {"continue": True}


if __name__ == "__main__":
    try:
        result = main()
        print(json.dumps(result or {"continue": True}))
    except Exception as exc:
        print(exc, file=sys.stderr)
        print(json.dumps({"continue": True}))
        sys.exit(0)
