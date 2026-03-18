#!/usr/bin/env python3
"""
context-window-guard.py — PostToolUse Hook: Context Window Monitor

Behavior:
- Reads JSON from stdin (PostToolUse payload)
- Extracts context_window.remaining_percentage or context_window_tokens_remaining
- If no context window data in payload → exits silently (exit 0)
- WARNING threshold: ≤30% remaining
- CRITICAL threshold: ≤15% remaining
- Debounce: /tmp/agent007-ctx-{session_id}-warned.json
  - Skips repeat warning until 5 tool-uses have passed since last warn
  - CRITICAL bypasses debounce
- Output: hookSpecificOutput.additionalContext with advisory message
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------

THRESHOLD_WARNING = 30.0   # ≤ this % → WARNING
THRESHOLD_CRITICAL = 15.0  # ≤ this % → CRITICAL
DEBOUNCE_TOOL_USES = 5     # minimum tool-uses between repeated warnings


# ---------------------------------------------------------------------------
# Stdin parsing
# ---------------------------------------------------------------------------

def read_stdin_payload() -> Optional[dict]:
    """Read and parse JSON from stdin. Returns None on any error."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        return json.loads(raw)
    except Exception:
        return None


def extract_remaining_percentage(payload: dict) -> Optional[float]:
    """
    Extract the remaining context window percentage from the payload.

    Checks:
    1. payload["context_window"]["remaining_percentage"]
    2. payload["context_window_tokens_remaining"] (raw tokens — percentage not computable without total)
    3. payload["hook_event_data"]["context_window"]["remaining_percentage"]
    """
    if not payload:
        return None

    # Primary: nested context_window object
    ctx = payload.get("context_window")
    if isinstance(ctx, dict):
        pct = ctx.get("remaining_percentage")
        if pct is not None:
            try:
                return float(pct)
            except (TypeError, ValueError):
                pass

        # Compute from raw tokens if total is available
        remaining = ctx.get("tokens_remaining")
        total = ctx.get("tokens_total")
        if remaining is not None and total and total > 0:
            try:
                return float(remaining) / float(total) * 100.0
            except (TypeError, ValueError):
                pass

    # Fallback: hook_event_data wrapper
    event_data = payload.get("hook_event_data") or {}
    ctx2 = event_data.get("context_window")
    if isinstance(ctx2, dict):
        pct = ctx2.get("remaining_percentage")
        if pct is not None:
            try:
                return float(pct)
            except (TypeError, ValueError):
                pass

    return None


def extract_session_id(payload: dict) -> str:
    """Extract session ID from payload, fallback to 'default'."""
    if not payload:
        return "default"
    session_id = (
        payload.get("session_id")
        or (payload.get("hook_event_data") or {}).get("session_id")
        or "default"
    )
    return str(session_id).replace("/", "_").replace("\\", "_")[:64]


# ---------------------------------------------------------------------------
# Debounce
# ---------------------------------------------------------------------------

def _debounce_file(session_id: str) -> str:
    return f"/tmp/agent007-ctx-{session_id}-warned.json"


def load_debounce_state(session_id: str) -> dict:
    """Load debounce state from /tmp. Returns empty dict on any error."""
    try:
        path = _debounce_file(session_id)
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_debounce_state(session_id: str, state: dict) -> None:
    """Persist debounce state. Silent-fails."""
    try:
        with open(_debounce_file(session_id), "w", encoding="utf-8") as f:
            json.dump(state, f)
    except Exception:
        pass


def should_warn(session_id: str, is_critical: bool) -> bool:
    """
    Return True if we should emit a warning now.
    CRITICAL always bypasses debounce.
    WARNING: only if ≥ DEBOUNCE_TOOL_USES tool-uses since last warn.
    """
    if is_critical:
        return True

    state = load_debounce_state(session_id)
    tool_uses_since_warn = state.get("tool_uses_since_warn", DEBOUNCE_TOOL_USES + 1)
    return tool_uses_since_warn >= DEBOUNCE_TOOL_USES


def record_tool_use(session_id: str, warned: bool) -> None:
    """
    Increment tool_uses_since_warn counter. Reset to 0 if we just warned.
    """
    state = load_debounce_state(session_id)
    if warned:
        state["tool_uses_since_warn"] = 0
        state["last_warned_at"] = datetime.now(timezone.utc).isoformat()
    else:
        current = state.get("tool_uses_since_warn", DEBOUNCE_TOOL_USES + 1)
        state["tool_uses_since_warn"] = current + 1
    save_debounce_state(session_id, state)


# ---------------------------------------------------------------------------
# Output builders
# ---------------------------------------------------------------------------

def build_warning_output(pct: float) -> dict:
    pct_display = round(pct, 1)
    return {
        "hookSpecificOutput": {
            "additionalContext": (
                f"⚠️ Context window al {pct_display}% restante. "
                "Considera: commit parcial, delegar a subagente, "
                "o resumir progreso en STATE.md antes de continuar."
            )
        }
    }


def build_critical_output(pct: float) -> dict:
    pct_display = round(pct, 1)
    return {
        "hookSpecificOutput": {
            "additionalContext": (
                f"🔴 CRÍTICO: Context al {pct_display}%. "
                "Acción inmediata: 1) Skill('commit') "
                "2) Spawn subagente para continuar "
                "3) Actualizar STATE.md"
            )
        }
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        payload = read_stdin_payload()
        remaining_pct = extract_remaining_percentage(payload)

        if remaining_pct is None:
            # No context window data — exit silently
            sys.exit(0)

        session_id = extract_session_id(payload or {})
        is_critical = remaining_pct <= THRESHOLD_CRITICAL
        is_warning = remaining_pct <= THRESHOLD_WARNING

        if not is_warning and not is_critical:
            # Context is fine
            record_tool_use(session_id, warned=False)
            sys.exit(0)

        emit = should_warn(session_id, is_critical)
        record_tool_use(session_id, warned=emit)

        if emit:
            if is_critical:
                output = build_critical_output(remaining_pct)
            else:
                output = build_warning_output(remaining_pct)
            print(json.dumps(output))

    except Exception:
        pass  # Never block tool use

    sys.exit(0)


if __name__ == "__main__":
    main()
