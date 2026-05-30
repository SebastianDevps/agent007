#!/usr/bin/env python3
"""
lifecycle-clock-in.py — SessionStart hook for lifecycle telemetry (REQ-1).

Appends a clock-in line to session-log.jsonl, emits recovery preamble if last
session ended within LIFECYCLE_RECOVERY_WINDOW_HOURS (default 4h, sentinel 0
suppresses preamble), and overwrites session.md with the active task.

PROFILE=minimal → instant exit, no side effects.
Fail-open: any exception → exit 0 with {"continue": true}.
Coexists with guides/session-recover.py (disjoint sources, no coupling).
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_HOOK_DIR = Path(__file__).parent
if str(_HOOK_DIR) not in sys.path:
    sys.path.insert(0, str(_HOOK_DIR))

from _lifecycle_common import (  # noqa: E402
    DEFAULT_RECOVERY_WINDOW_HOURS,
    LIFECYCLE_RECOVERY_WINDOW_HOURS,
    TAIL_LINES,
    append_jsonl,
    now_iso,
    parse_payload,
    project_root,
    read_index_with_fallback,
)

if os.environ.get("CLAUDE_HOOK_PROFILE") == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)


def _parse_recovery_window() -> int:
    raw = os.environ.get(LIFECYCLE_RECOVERY_WINDOW_HOURS, "")
    if not raw:
        return DEFAULT_RECOVERY_WINDOW_HOURS
    try:
        value = int(raw)
        return value if value >= 0 else DEFAULT_RECOVERY_WINDOW_HOURS
    except (ValueError, TypeError):
        return DEFAULT_RECOVERY_WINDOW_HOURS


def _parse_recovery_window_s() -> Optional[int]:
    """Return recovery window in seconds for JSONL schema (null if env parse fails)."""
    raw = os.environ.get(LIFECYCLE_RECOVERY_WINDOW_HOURS, "")
    if not raw:
        return DEFAULT_RECOVERY_WINDOW_HOURS * 3600
    try:
        value = int(raw)
        return max(0, value) * 3600
    except (ValueError, TypeError):
        return None


def _parse_iso(ts_str: str) -> Optional[datetime]:
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _tail_jsonl(path: Path, n: int) -> list:
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        result = []
        for line in lines[-n:]:
            if not line.strip():
                continue
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return result
    except OSError:
        return []


def _find_last_clock_out(events: list) -> Optional[dict]:
    for event in reversed(events):
        if event.get("type") == "clock-out":
            return event
    return None


def _humanize_gap(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}h {minutes}m" if minutes else f"{hours}h"


def _build_preamble(last_clock_out: dict, gap_seconds: int, root: Path) -> str:
    age = _humanize_gap(gap_seconds)
    parts = [f"## Lifecycle recovery — sesion previa cerro hace {age}"]

    index = read_index_with_fallback(root)
    active = [c for c in (index or {}).get("changes", []) if c.get("status") != "archived"][:3]
    parts.append("\n### Active task (de openspec/changes/_index.json)")
    if active:
        for task in active:
            parts.append(
                f"- **wip**: {task.get('name','?')} "
                f"(last_phase: {task.get('last_phase','?')}, status: {task.get('status','?')})"
            )
    else:
        parts.append("- unknown (index unavailable)")

    prev_sid = last_clock_out.get("session_id", "unknown")
    duration_s = last_clock_out.get("duration_s")
    duration_str = _humanize_gap(duration_s) if isinstance(duration_s, int) else "unknown"
    parts.append(f"\n### Previous clock-out")
    parts.append(f"- session_id: {prev_sid}")
    parts.append(f"- duration_s: {duration_str}")
    parts.append("- closed_cleanly: yes")
    parts.append("\n_To suppress this preamble, set `LIFECYCLE_RECOVERY_WINDOW_HOURS=0` in env._")
    return "\n".join(parts)


def _derive_active_task(root: Path) -> str:
    index = read_index_with_fallback(root)
    if not index:
        return "ninguna"
    for change in index.get("changes", []):
        if change.get("status") != "archived":
            return change.get("name", "ninguna")
    return "ninguna"


def _update_session_md(root: Path, active_task: str) -> None:
    session_md = root / ".sdlc" / "state" / "session.md"
    session_md.parent.mkdir(parents=True, exist_ok=True)
    session_md.write_text(
        f"## Session started\n{now_iso()}\n\n## Active task\n{active_task}\n",
        encoding="utf-8",
    )


def main() -> dict:
    payload = parse_payload()
    session_id = payload.get("session_id") or os.environ.get("CLAUDE_SESSION_ID", "")
    cwd = payload.get("cwd") or os.getcwd()

    root = project_root()
    session_log = root / ".sdlc" / "state" / "session-log.jsonl"
    session_log.parent.mkdir(parents=True, exist_ok=True)

    events = _tail_jsonl(session_log, TAIL_LINES)
    last_clock_out = _find_last_clock_out(events)

    recovery_window_s = _parse_recovery_window() * 3600
    now_dt = datetime.now(timezone.utc)
    last_session_end = None
    last_session_id = None
    gap_seconds = None
    within_recovery_window = False

    if last_clock_out:
        last_session_end = last_clock_out.get("ts")
        last_session_id = last_clock_out.get("session_id")
        last_dt = _parse_iso(last_session_end) if last_session_end else None
        if last_dt:
            gap_seconds = int((now_dt - last_dt).total_seconds())
            # Negative gap = clock skew → treat as fresh session
            if gap_seconds >= 0 and recovery_window_s > 0:
                within_recovery_window = gap_seconds < recovery_window_s

    append_jsonl(session_log, {
        "ts": now_dt.isoformat(),
        "session_id": session_id,
        "type": "clock-in",
        "cwd": cwd,
        "last_session_end": last_session_end,
        "recovery_window_s": _parse_recovery_window_s(),
    })

    active_task = _derive_active_task(root)
    _update_session_md(root, active_task)

    if within_recovery_window and last_clock_out:
        preamble = _build_preamble(last_clock_out, gap_seconds, root)
        return {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": preamble}}

    return {"continue": True}


if __name__ == "__main__":
    try:
        result = main()
        print(json.dumps(result or {"continue": True}))
    except Exception as exc:
        print(exc, file=sys.stderr)
        print(json.dumps({"continue": True}))
        sys.exit(0)
