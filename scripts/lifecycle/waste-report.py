#!/usr/bin/env python3
"""
waste-report.py — Plugin overhead audit

Reads .sdlc/state/context-budget.jsonl (written by context-tick.py) and
reports:

  - Top 5 most-loaded files this period
  - References hit-rate (loaded / exists)
  - Sessions per day
  - Average tool calls per session
  - p50 / p95 / p99 of tokens-at-stop (if telemetry has it)
  - Top 10 NEVER-loaded references (candidates to delete)

Default period: last 7 days. Override with --days N.

Run:
  .claude/scripts/lifecycle/waste-report.py
  .claude/scripts/lifecycle/waste-report.py --days 30
  .claude/scripts/lifecycle/waste-report.py --json

This is an audit tool — it answers "is the plugin paying its keep?"
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JSONL = ROOT / ".sdlc" / "state" / "context-budget.jsonl"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return p.parse_args()


def load_events(cutoff: datetime) -> list[dict]:
    if not JSONL.exists():
        return []
    out = []
    for line in JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = ev.get("ts")
        if not ts:
            continue
        try:
            t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            continue
        if t < cutoff:
            continue
        out.append(ev)
    return out


def find_all_references(plugin_root: Path) -> set[str]:
    """All references/<x>.md files that exist in the plugin."""
    skills = plugin_root / ".claude" / "skills"
    if not skills.is_dir():
        return set()
    return {
        str(p.relative_to(plugin_root))
        for p in skills.rglob("references/*.md")
    }


def percentile(values: list[int], pct: float) -> int:
    if not values:
        return 0
    s = sorted(values)
    k = int(round((len(s) - 1) * pct / 100))
    return s[max(0, min(k, len(s) - 1))]


def main() -> int:
    args = parse_args()
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    events = load_events(cutoff)

    if not events:
        msg = f"No telemetry found in last {args.days} day(s).\n"
        msg += f"Expected file: {JSONL}\n"
        msg += "Make sure context-tick.py is registered in settings.json."
        if args.json:
            print(json.dumps({"error": msg}))
        else:
            print(msg, file=sys.stderr)
        return 1

    # Filter
    sessions = {ev.get("session_id", "?") for ev in events}
    tool_uses = [ev for ev in events if ev.get("type") == "tool_use"]
    stops = [ev for ev in events if ev.get("type") == "session_stop"]

    # Top files
    file_counter = Counter(ev["file"] for ev in tool_uses if ev.get("file"))
    top_files = file_counter.most_common(5)

    # References hit rate
    refs_loaded = {
        ev["file"] for ev in tool_uses
        if ev.get("reference_load") and ev.get("file")
    }
    refs_exist = find_all_references(ROOT)
    # Normalize: file paths in events may be absolute or relative
    refs_loaded_norm = {
        f if f.startswith(".claude/") else f.split(".claude/", 1)[-1]
        for f in refs_loaded
    }
    refs_loaded_norm = {
        ".claude/" + f if not f.startswith(".claude/") else f
        for f in refs_loaded_norm if f
    }
    hit_rate = (
        len(refs_loaded_norm & refs_exist) / len(refs_exist) * 100
        if refs_exist else 0
    )
    never_loaded = sorted(refs_exist - refs_loaded_norm)[:10]

    # Token stats
    tokens_at_stop = [
        ev["tokens_at_stop"] for ev in stops
        if isinstance(ev.get("tokens_at_stop"), int) and ev["tokens_at_stop"] > 0
    ]
    p50 = percentile(tokens_at_stop, 50)
    p95 = percentile(tokens_at_stop, 95)
    p99 = percentile(tokens_at_stop, 99)

    # Tool calls per session
    calls_per_sess: dict[str, int] = {}
    for ev in tool_uses:
        sid = ev.get("session_id", "?")
        calls_per_sess[sid] = calls_per_sess.get(sid, 0) + 1
    avg_calls = sum(calls_per_sess.values()) / max(1, len(calls_per_sess))

    report = {
        "period_days": args.days,
        "sessions": len(sessions),
        "tool_uses": len(tool_uses),
        "avg_tool_calls_per_session": round(avg_calls, 1),
        "top_files": [{"file": f, "count": c} for f, c in top_files],
        "references_total": len(refs_exist),
        "references_loaded": len(refs_loaded_norm & refs_exist),
        "references_hit_rate_pct": round(hit_rate, 1),
        "references_never_loaded_top10": never_loaded,
        "tokens_at_stop_p50": p50,
        "tokens_at_stop_p95": p95,
        "tokens_at_stop_p99": p99,
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"waste-report.py — last {args.days} day(s)")
    print(f"  Sessions:               {report['sessions']}")
    print(f"  Tool uses:              {report['tool_uses']}")
    print(f"  Avg calls / session:    {report['avg_tool_calls_per_session']}")
    print()
    print(f"  Top 5 most-loaded files:")
    for entry in report["top_files"]:
        print(f"    {entry['count']:>4}× {entry['file']}")
    print()
    print(f"  References hit rate:    {report['references_loaded']} / {report['references_total']} ({report['references_hit_rate_pct']}%)")
    if never_loaded:
        print(f"  Never-loaded references (delete candidates):")
        for ref in never_loaded:
            print(f"    - {ref}")
    print()
    if tokens_at_stop:
        print(f"  Tokens at session stop:")
        print(f"    p50: {p50:,}")
        print(f"    p95: {p95:,}")
        print(f"    p99: {p99:,}")
    else:
        print("  Tokens at session stop: no telemetry yet (CLAUDE_CONTEXT_TOKENS env not set)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
