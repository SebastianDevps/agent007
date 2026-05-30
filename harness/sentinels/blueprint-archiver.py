#!/usr/bin/env python3
"""harness/sentinels/blueprint-archiver.py — v7.2 Ola 31 auto-archive.

Fires on `Stop`. Moves completed Ola blueprints from .sdlc/blueprints/ to
.sdlc/archive/v7-blueprints/ when a git commit references the Ola number.

A blueprint is 'completed' when:
  - Its filename matches the Ola pattern: r'^v\\d+(\\.\\d+)?-ola\\d+.*\\.md$'
  - AND a git commit exists referencing that Ola number (e.g., "OLA17")
  - AND the basename is NOT in the canonical whitelist

Best-effort: exits 0 always. Supports --dry-run to print would-be archives
without moving any file.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BLUEPRINTS_DIR = PROJECT_ROOT / ".sdlc" / "blueprints"
ARCHIVE_DIR = PROJECT_ROOT / ".sdlc" / "archive" / "v7-blueprints"
TARGET_EVENT = "Stop"

CANONICAL_PATTERNS: tuple[str, ...] = (
    "RELEASE",
    "PROPOSAL",
    "research",
    "SESSION",
    "decisions",
    "HARDENING",
    "v7-software-engineering-os.md",
)

OLA_PATTERN = re.compile(
    r"^v(\d+(?:\.\d+)?)-(?:ola)?(\d+)[-.].*\.md$",
    re.IGNORECASE,
)

GIT_LOG_TIMEOUT_SEC = 3
GRACE_PERIOD_HOURS = 24  # blueprint must be 24h old AND its commit 24h old


def is_canonical(name: str) -> bool:
    lower = name.lower()
    return any(pat.lower() in lower for pat in CANONICAL_PATTERNS)


def _git_log_text() -> str:
    """Returns oneline log of commits OLDER than the grace period."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"--before={GRACE_PERIOD_HOURS}.hours.ago"],
            capture_output=True,
            text=True,
            timeout=GIT_LOG_TIMEOUT_SEC,
            cwd=str(PROJECT_ROOT),
        )
        return result.stdout or ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def has_commit_referencing_ola(ola_num: str, log_text: str) -> bool:
    upper = log_text.upper()
    patterns = (f"OLA{ola_num}", f"OLA-{ola_num}", f"OLA {ola_num}")
    return any(p in upper for p in patterns)


def _is_file_old_enough(path: Path) -> bool:
    """File mtime must be older than grace period."""
    import time
    try:
        age_hours = (time.time() - path.stat().st_mtime) / 3600
        return age_hours >= GRACE_PERIOD_HOURS
    except OSError:
        return False


def find_completed(log_text: str) -> list[Path]:
    if not BLUEPRINTS_DIR.is_dir():
        return []
    completed: list[Path] = []
    for path in BLUEPRINTS_DIR.iterdir():
        if not path.is_file() or not path.name.endswith(".md"):
            continue
        if is_canonical(path.name):
            continue
        match = OLA_PATTERN.match(path.name)
        if not match:
            continue
        ola_num = match.group(2)
        if not has_commit_referencing_ola(ola_num, log_text):
            continue
        if not _is_file_old_enough(path):
            continue
        completed.append(path)
    return completed


def archive(paths: list[Path]) -> list[str]:
    if not paths:
        return []
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    moved: list[str] = []
    for path in paths:
        target = ARCHIVE_DIR / path.name
        if target.exists():
            continue
        try:
            shutil.move(str(path), str(target))
            moved.append(path.name)
        except (OSError, shutil.Error):
            continue
    return moved


def _read_payload() -> dict:
    try:
        data = json.load(sys.stdin)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def main(argv: list[str]) -> int:
    dry_run = "--dry-run" in argv
    if not dry_run:
        if _read_payload().get("hook_event_name") != TARGET_EVENT:
            return 0

    log_text = _git_log_text()
    candidates = find_completed(log_text)

    if dry_run:
        print(f"[blueprint-archiver] DRY RUN — would archive {len(candidates)}:")
        for path in candidates:
            print(f"  - {path.name}")
        return 0

    moved = archive(candidates)
    if moved:
        print(
            f"[blueprint-archiver] archived {len(moved)} blueprints "
            f"to {ARCHIVE_DIR.relative_to(PROJECT_ROOT)}/"
        )
        for name in moved:
            print(f"  - {name}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception:
        sys.exit(0)
