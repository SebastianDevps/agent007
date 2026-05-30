#!/usr/bin/env python3
"""harness/sentinels/cache-pulse.py — v7.2 Ola 26 cache-hit measurement.

Fires on `Stop`. Parses the current session transcript JSONL, aggregates
`usage.cache_*` fields across all assistant turns, computes a
hit ratio, and appends one record to .sdlc/state/cache-metrics.jsonl.

Best-effort: exits 0 even on parse failures. Measurement is non-critical;
losing one record is fine — losing the session is not.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
METRICS_PATH = PROJECT_ROOT / ".sdlc" / "state" / "cache-metrics.jsonl"
TARGET_EVENT = "Stop"
USAGE_KEYS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_int(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return 0


def _extract_usage(entry: dict) -> dict | None:
    """Return usage dict if this is an assistant message with usage, else None."""
    message = entry.get("message")
    if not isinstance(message, dict):
        return None
    if message.get("role") != "assistant":
        return None
    usage = message.get("usage")
    if not isinstance(usage, dict):
        return None
    return usage


def parse_transcript(transcript_path: str) -> dict[str, int]:
    """Aggregate cache usage stats across assistant turns in the JSONL."""
    stats = {
        "input_tokens_total": 0,
        "cache_read_tokens_total": 0,
        "cache_creation_tokens_total": 0,
        "output_tokens_total": 0,
        "turns": 0,
        "turns_with_cache_read": 0,
    }
    path = Path(transcript_path)
    if not path.is_file():
        return stats
    try:
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    entry = json.loads(raw)
                except (json.JSONDecodeError, ValueError):
                    continue
                if not isinstance(entry, dict):
                    continue
                usage = _extract_usage(entry)
                if usage is None:
                    continue
                stats["turns"] += 1
                cache_read = _safe_int(usage.get("cache_read_input_tokens"))
                cache_create = _safe_int(usage.get("cache_creation_input_tokens"))
                stats["input_tokens_total"] += _safe_int(usage.get("input_tokens"))
                stats["cache_read_tokens_total"] += cache_read
                stats["cache_creation_tokens_total"] += cache_create
                stats["output_tokens_total"] += _safe_int(usage.get("output_tokens"))
                if cache_read > 0:
                    stats["turns_with_cache_read"] += 1
    except OSError:
        return stats
    return stats


def compute_hit_ratio(stats: dict[str, int]) -> float:
    """Cache hit ratio: cache_read / (input + cache_read + cache_creation).

    Returns 0.0 when there is no measurable input traffic to avoid div-by-zero.
    """
    denom = (
        stats["input_tokens_total"]
        + stats["cache_read_tokens_total"]
        + stats["cache_creation_tokens_total"]
    )
    if denom <= 0:
        return 0.0
    return stats["cache_read_tokens_total"] / denom


def append_jsonl(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, separators=(",", ":")) + "\n")


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0
    if payload.get("hook_event_name") != TARGET_EVENT:
        return 0

    transcript_path = payload.get("transcript_path")
    session_id = payload.get("session_id") or ""
    if not transcript_path or not os.path.isfile(transcript_path):
        return 0

    stats = parse_transcript(transcript_path)
    if stats["turns"] == 0:
        return 0

    hit_ratio = compute_hit_ratio(stats)
    record = {
        "ts": _iso_utc_now(),
        "session_id": session_id,
        **stats,
        "hit_ratio": round(hit_ratio, 4),
    }

    try:
        append_jsonl(METRICS_PATH, record)
    except OSError:
        return 0

    short_id = session_id[:8] if session_id else "unknown"
    print(
        f"[cache-pulse] session={short_id} "
        f"hit_ratio={hit_ratio:.1%} turns={stats['turns']}"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        # Sentinel must never fail loud — measurement is best-effort.
        sys.exit(0)
