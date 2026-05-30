#!/usr/bin/env python3
"""
state-sync.py — Stop Hook: Multi-target State Synchronization

Evolved from stop-state-sync.py. Writes to:
  1. .sdlc/state/session.md  (primary session state)
  2. .sdlc/state/progress.md (task progress log)
  3. MASTER_GUIDE.md         (active task status line)

Sources:
  - .sdlc/state/session.md  (read existing to preserve structure)
  - .claude/.session-state.json (legacy fallback)

Behavior:
  - NEVER blocks the stop — exit 0 always, even on error
  - Skips update if ralph is active
  - Output: {} (empty JSON) — side-effect only
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
        if os.path.isdir(os.path.join(current, ".claude")):
            return current
        current = os.path.dirname(current)
    return os.getcwd()


PROJECT_ROOT = _find_project_root()

# New paths (v5)
SESSION_MD_FILE = os.path.join(PROJECT_ROOT, ".sdlc", "state", "session.md")
MASTER_GUIDE_FILE = os.path.join(PROJECT_ROOT, "MASTER_GUIDE.md")

# Legacy fallback
LEGACY_SESSION_JSON = os.path.join(PROJECT_ROOT, ".claude", ".session-state.json")
LEGACY_STATE_MD = os.path.join(PROJECT_ROOT, ".claude", "STATE.md")


# ---------------------------------------------------------------------------
# Load session state (try new path, fall back to legacy)
# ---------------------------------------------------------------------------

def load_session_state() -> Optional[dict]:
    """Load session state from JSON sidecar if it exists."""
    for path in [LEGACY_SESSION_JSON]:  # legacy only — new session.json is markdown-based
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
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


def build_summary_bullets(state: Optional[dict]) -> list:
    """Build 2-3 summary bullets from session state data."""
    bullets = []
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if state:
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
        bullets.append(f"Sesión finalizada ({timestamp})")

    return bullets


# ---------------------------------------------------------------------------
# Target 1: .sdlc/state/session.md
# ---------------------------------------------------------------------------

def update_session_md(bullets: list) -> None:
    """Update or create .sdlc/state/session.md with session summary."""
    os.makedirs(os.path.dirname(SESSION_MD_FILE), exist_ok=True)

    bullet_lines = "\n".join(f"- {b}" for b in bullets)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if os.path.exists(SESSION_MD_FILE):
        with open(SESSION_MD_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace or append "Resumen de Última Sesión" section
        section_header = "## Resumen de Última Sesión"
        pattern = re.compile(
            r"(## Resumen de Última Sesión\s*\n)([^#]*)",
            re.DOTALL
        )

        def replacer(m):
            return m.group(1) + bullet_lines + "\n"

        new_content, count = re.subn(pattern, replacer, content)

        if count == 0:
            new_content = content.rstrip() + f"\n\n{section_header}\n{bullet_lines}\n"
    else:
        new_content = f"""# Session State

## Tarea Activa
ninguna

## Tareas Completadas
(ninguna)

## Decisiones Tomadas
(ninguna)

## Resumen de Última Sesión
{bullet_lines}
"""

    with open(SESSION_MD_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)


# ---------------------------------------------------------------------------
# Target 3: MASTER_GUIDE.md status line
# ---------------------------------------------------------------------------

def update_master_guide_status(bullets: list) -> None:
    """Update active task status line in MASTER_GUIDE.md if it exists."""
    if not os.path.exists(MASTER_GUIDE_FILE):
        return

    with open(MASTER_GUIDE_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status_line = f"**Last session**: {timestamp} | {bullets[0] if bullets else 'no activity'}"

    # Replace existing status line or insert after first heading
    status_pattern = re.compile(r'\*\*Last session\*\*:.*\n')
    if status_pattern.search(content):
        new_content = status_pattern.sub(status_line + "\n", content)
    else:
        # Insert after first # heading
        heading_match = re.search(r'^(#[^\n]+\n)', content, re.MULTILINE)
        if heading_match:
            insert_pos = heading_match.end()
            new_content = content[:insert_pos] + "\n" + status_line + "\n" + content[insert_pos:]
        else:
            new_content = content  # No heading found, skip

    with open(MASTER_GUIDE_FILE, "w", encoding="utf-8") as f:
        f.write(new_content)


# ---------------------------------------------------------------------------
# Legacy: also update .claude/STATE.md if it exists (backward compat)
# ---------------------------------------------------------------------------

def update_legacy_state_md(bullets: list) -> None:
    """Update legacy STATE.md for backward compatibility."""
    if not os.path.exists(LEGACY_STATE_MD):
        return

    with open(LEGACY_STATE_MD, "r", encoding="utf-8") as f:
        content = f.read()

    section_header = "## Resumen de Última Sesión"
    bullet_lines = "\n".join(f"- {b}" for b in bullets)

    pattern = re.compile(
        r"(## Resumen de Última Sesión\s*\n)([^#]*)",
        re.DOTALL
    )

    def replacer(m):
        return m.group(1) + bullet_lines + "\n"

    new_content, count = re.subn(pattern, replacer, content)

    if count == 0:
        new_content = content.rstrip() + f"\n\n{section_header}\n{bullet_lines}\n"

    with open(LEGACY_STATE_MD, "w", encoding="utf-8") as f:
        f.write(new_content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        state = load_session_state()

        if not (state and is_ralph_active(state)):
            bullets = build_summary_bullets(state)
            update_session_md(bullets)
            update_master_guide_status(bullets)
            update_legacy_state_md(bullets)
    except Exception:
        pass  # Never block the stop

    print("{}")


if __name__ == "__main__":
    main()
