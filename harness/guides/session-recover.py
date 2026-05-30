#!/usr/bin/env python3
# CONTRACT EXCEPTION (v7-F1): filesystem mutation (state files) — target: SP-1 effectors
"""
session-recover.py — SessionStart hook for cross-session continuity

Claude Code does not expose a PreCompact event. Instead of trying to dump
state at compaction time (impossible), we rely on context-tick.py persisting
events continuously to .sdlc/state/context-budget.jsonl. This hook fires at
the START of every session, reads recent tail of that JSONL, and emits an
`additionalContext` block summarizing what the previous session was doing.

Effect for the user:
  Every new session opens with a "you were working on X — last 5 files
  touched were …" preamble. No reliance on the LLM remembering anything.

Recovery scope:
  - Only emit recovery if last activity is within RECENT_HOURS (default 4)
  - Skip if last_event was a clean session_stop AND user hasn't logged
    intent in the last 30 minutes (treat it as "fresh start")

Profile gating: PROFILE=minimal → no-op
Performance budget: < 30ms (read tail of JSONL, no parse-everything)
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print("{}")
    sys.exit(0)

RECENT_HOURS = int(os.environ.get("SESSION_RECOVER_HOURS", "4"))
MAX_FILES_REPORTED = 8
MAX_DECISIONS_REPORTED = 5
TAIL_LINES = 200  # last 200 events should cover most sessions


def project_root() -> Path:
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


def jsonl_path(root: Path) -> Path:
    return root / ".sdlc" / "state" / "context-budget.jsonl"


def session_state_path(root: Path) -> Path:
    return root / ".sdlc" / "state" / "session.md"


def tail_events(path: Path, n: int) -> list[dict]:
    if not path.exists():
        return []
    try:
        # Memory-efficient tail: read entire file (typical < 10MB), keep last n lines
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        out = []
        for line in lines[-n:]:
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out
    except OSError:
        return []


def parse_ts(ev: dict):
    ts = ev.get("ts")
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def humanize_age(dt: datetime) -> str:
    delta = datetime.now(timezone.utc) - dt
    secs = int(delta.total_seconds())
    if secs < 60:
        return f"{secs}s ago"
    if secs < 3600:
        return f"{secs // 60}m ago"
    if secs < 86400:
        return f"{secs // 3600}h ago"
    return f"{secs // 86400}d ago"


def summarize(events: list[dict]) -> dict:
    """Group events from the most recent prior session."""
    if not events:
        return {}

    # Walk backwards, group by session_id, stop after we've covered the most
    # recent prior session that is NOT the current one (we don't have current
    # session_id at SessionStart, so use the last session that closed OR the
    # last session with activity).
    by_session: dict[str, list[dict]] = {}
    for ev in events:
        sid = ev.get("session_id", "?")
        by_session.setdefault(sid, []).append(ev)

    # Pick the session with the most recent timestamp
    latest_sid = max(
        by_session,
        key=lambda s: max((parse_ts(e) or datetime.min.replace(tzinfo=timezone.utc))
                          for e in by_session[s]),
    )
    sess_events = by_session[latest_sid]

    files_touched = []
    seen_files = set()
    tools_used = {}
    last_ts = None
    started_ts = None
    closed = False

    for ev in sess_events:
        t = parse_ts(ev)
        if t and (last_ts is None or t > last_ts):
            last_ts = t
        if t and (started_ts is None or t < started_ts):
            started_ts = t
        if ev.get("type") == "session_stop":
            closed = True
        if ev.get("type") == "tool_use":
            tool = ev.get("tool", "?")
            tools_used[tool] = tools_used.get(tool, 0) + 1
            f = ev.get("file")
            if f and f not in seen_files:
                seen_files.add(f)
                files_touched.append(f)

    return {
        "session_id": latest_sid,
        "started_ts": started_ts,
        "last_ts": last_ts,
        "closed": closed,
        "tools_used": tools_used,
        "files_touched": files_touched[:MAX_FILES_REPORTED],
        "tool_call_total": sum(tools_used.values()),
    }


def onboarding_marker_path(root: Path) -> Path:
    return root / ".sdlc" / "state" / "onboarding-seen.json"


def build_onboarding_message() -> str:
    return (
        "## Bienvenido a Agent007 — primer arranque\n\n"
        "Sos un sistema de orquestación: clasificás el pedido, lo ruteás, ejecutás con "
        "verificación y persistís estado en archivos. Antes de codear, anunciá la decisión "
        "de routing: `🎯 [target] | Risk: [low|medium|high|critical]`.\n\n"
        "**Dónde está todo (lazy-load, no lo importes entero):**\n"
        "- Skills → `.claude/skills/INDEX.md`\n"
        "- Agentes → `.claude/agents/INDEX.md`\n"
        "- Comandos → `.claude/commands/INDEX.md`\n"
        "- Navegación del proyecto → `CONTEXT.md`\n"
        "- Reglas (coding/security/git) → `.claude/rules/<topic>.md`\n\n"
        "**Pipeline (una decisión por pedido):** trivial → `Skill('generate')`+`Skill('verify')`; "
        "substancial/multi-archivo/riesgo → `/sdd-new <change>`.\n\n"
        "_Este preámbulo aparece solo en el primer arranque. No vuelve a mostrarse._"
    )


def maybe_emit_onboarding(root: Path) -> str:
    """Return the onboarding preamble on the very first run, else ''.

    First-run = no marker file yet. Writing the marker makes this idempotent
    so the preamble shows exactly once per project checkout.
    """
    marker = onboarding_marker_path(root)
    if marker.exists():
        return ""
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(
            json.dumps({"seen_ts": datetime.now(timezone.utc).isoformat()}) + "\n",
            encoding="utf-8",
        )
    except OSError:
        return ""  # can't persist the marker → stay silent rather than nag every session
    return build_onboarding_message()


def read_session_md(root: Path) -> str:
    p = session_state_path(root)
    if not p.exists():
        return ""
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        return ""
    # Trim aggressively — only the first 600 chars (active task header)
    return text[:600].strip()


def build_recovery_message(summary: dict, session_md_excerpt: str) -> str:
    if not summary or summary.get("last_ts") is None:
        return ""

    age = humanize_age(summary["last_ts"])
    line1 = f"## Previous session ({age})"
    parts = [line1]

    if session_md_excerpt:
        parts.append("### Active task (from session.md)\n```\n" + session_md_excerpt + "\n```")

    if summary.get("files_touched"):
        files_block = "\n".join(f"- `{f}`" for f in summary["files_touched"])
        parts.append(f"### Last files touched ({len(summary['files_touched'])} of {summary['tool_call_total']} tool calls)\n{files_block}")

    if summary.get("tools_used"):
        tool_top = sorted(summary["tools_used"].items(), key=lambda x: -x[1])[:5]
        tools_block = " · ".join(f"{t}: {c}" for t, c in tool_top)
        parts.append(f"### Tool mix\n{tools_block}")

    if not summary.get("closed"):
        parts.append("⚠️ **Previous session did not close cleanly** — consider running `mem_session_summary` early in this one to capture remaining state.")

    parts.append("_To suppress this recovery preamble, set `SESSION_RECOVER_HOURS=0` in env._")
    return "\n\n".join(parts)


def main() -> None:
    root = project_root()

    # First-run onboarding takes precedence: a brand-new checkout has no prior
    # session context, so emit the entry-path preamble (once) instead of bailing.
    onboarding = maybe_emit_onboarding(root)
    if onboarding:
        out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": onboarding}}
        print(json.dumps(out))
        sys.exit(0)

    events = tail_events(jsonl_path(root), TAIL_LINES)

    summary = summarize(events)
    if not summary or summary.get("last_ts") is None:
        print("{}")
        sys.exit(0)

    age_hours = (datetime.now(timezone.utc) - summary["last_ts"]).total_seconds() / 3600
    if age_hours > RECENT_HOURS:
        # Too old — assume fresh start, don't pollute context
        print("{}")
        sys.exit(0)

    excerpt = read_session_md(root)
    msg = build_recovery_message(summary, excerpt)
    if not msg:
        print("{}")
        sys.exit(0)

    out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}}
    print(json.dumps(out))
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("{}")
        sys.exit(0)
