#!/usr/bin/env python3
"""
stop-state-sync.py — Stop Hook: Serialize sessionState → STATE.md

Behavior:
- Reads .claude/.session-state.json (if exists)
- Updates "Resumen de Última Sesión" in .claude/STATE.md with real data
- NEVER blocks the stop — exit 0 always, even on error
- Output: {} (empty JSON) — side-effect only
- If ralph is active (detected in previousSkill or recent taskHistory) → skip STATE.md update
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _find_project_root() -> str:
    """Walk up from this file's directory to find the Agent007 project root."""
    current = os.path.dirname(os.path.abspath(__file__))
    while current != os.path.dirname(current):
        claude_dir = os.path.join(current, ".claude")
        if os.path.isdir(claude_dir):
            return current
        current = os.path.dirname(current)
    return os.getcwd()


PROJECT_ROOT = _find_project_root()
SESSION_STATE_FILE = os.path.join(PROJECT_ROOT, ".claude", ".session-state.json")
STATE_MD_FILE = os.path.join(PROJECT_ROOT, ".claude", "STATE.md")


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def load_session_state() -> Optional[dict]:
    """Load .session-state.json, return dict or None on any error."""
    try:
        if not os.path.exists(SESSION_STATE_FILE):
            return None
        with open(SESSION_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def is_ralph_active(state: dict) -> bool:
    """Return True if ralph appears to be running based on session state."""
    if not state:
        return False
    previous_skill = (state.get("previousSkill") or "").lower()
    if "ralph" in previous_skill:
        return True
    task_history = state.get("taskHistory") or []
    recent = task_history[-5:] if len(task_history) >= 5 else task_history
    for entry in recent:
        skill = (entry.get("skill") or "").lower()
        if "ralph" in skill:
            return True
    return False


def build_summary_bullets(state: dict) -> list:
    """Build 2-3 summary bullets from session state data."""
    bullets = []
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    previous_skill = state.get("previousSkill")
    if previous_skill:
        bullets.append(f"Última skill activada: `{previous_skill}` ({timestamp})")

    task_history = state.get("taskHistory") or []
    if task_history:
        recent = task_history[-3:]
        skills_used = [e.get("skill", "?") for e in recent if e.get("skill")]
        if skills_used:
            bullets.append(f"Skills recientes: {' → '.join(skills_used)}")

    active_context = state.get("activeContext") or {}
    context_parts = [f"{k}={v}" for k, v in active_context.items() if v]
    if context_parts:
        bullets.append(f"Contexto activo: {', '.join(context_parts)}")

    if not bullets:
        bullets.append(f"Sesión finalizada sin actividad registrada ({timestamp})")

    return bullets


def update_state_md(bullets: list) -> None:
    """Replace the 'Resumen de Última Sesión' section in STATE.md."""
    if not os.path.exists(STATE_MD_FILE):
        return

    with open(STATE_MD_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    section_header = "## Resumen de Última Sesión"
    bullet_lines = "\n".join(f"- {b}" for b in bullets)

    # Find and replace the section content up to the next ## or end of file
    pattern = re.compile(
        r"(## Resumen de Última Sesión\s*\n)([^#]*)",
        re.DOTALL
    )

    def replacer(m):
        return m.group(1) + bullet_lines + "\n"

    new_content, count = re.subn(pattern, replacer, content)

    if count == 0:
        # Section not found — append it
        new_content = content.rstrip() + f"\n\n{section_header}\n{bullet_lines}\n"

    with open(STATE_MD_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        state = load_session_state()

        if state and not is_ralph_active(state):
            bullets = build_summary_bullets(state)
            update_state_md(bullets)
    except Exception:
        pass  # Never block the stop

    # Output empty JSON — hook output protocol
    print("{}")


if __name__ == "__main__":
    main()
