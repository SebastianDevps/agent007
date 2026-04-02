#!/usr/bin/env python3
"""
memory-decay.py — SessionStart hook

Applies temporal decay to auto-memory entries so stale memories don't
pollute future sessions with outdated context.

Decay formula: weight = e^(-λ × days)  where λ = 0.023 (30-day half-life)
  weight < 0.10  (>30 days)  → mark entry as [stale: YYYY-MM-DD] in MEMORY.md
  weight < 0.05  (>60 days)  → archive memory file to memory/archive/

Memory path: ~/.claude/projects/{encoded_project_path}/memory/MEMORY.md
  Encoding: project path with / replaced by -

Behavior:
  - NEVER blocks the session start — exit 0 always, even on error
  - Reads modification time of each memory file to calculate age
  - Updates MEMORY.md in-place (adds [stale] tag to index entries)
  - Moves archived files to memory/archive/ subdirectory
  - Output: {} (empty JSON) — side-effect only

Performance budget: < 100ms
"""

import json
import math
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print("{}")
    sys.exit(0)

LAMBDA = 0.023          # decay constant → half-life ≈ 30 days
STALE_THRESHOLD = 0.50  # weight below this → [stale] tag (triggered at ~30 days)
ARCHIVE_THRESHOLD = 0.25  # weight below this → move to archive/ (triggered at ~60 days)


def find_project_root() -> Path:
    current = Path(os.getcwd())
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    return Path(os.getcwd())


def get_memory_dir(project_root: Path) -> Path:
    """Construct the Claude memory directory path for this project."""
    home = Path(os.path.expanduser("~"))
    # Encode project path: replace / with -
    encoded = str(project_root).replace("/", "-")
    return home / ".claude" / "projects" / encoded / "memory"


def decay_weight(days_old: float) -> float:
    return math.exp(-LAMBDA * days_old)


def get_file_age_days(file_path: Path) -> float:
    """Return file age in days based on modification time."""
    try:
        mtime = file_path.stat().st_mtime
        now = datetime.now(timezone.utc).timestamp()
        return (now - mtime) / 86400
    except Exception:
        return 0.0


def parse_memory_entries(content: str) -> list:
    """Parse MEMORY.md index lines into list of dicts."""
    entries = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [") and "](" in stripped:
            entries.append({"raw": line, "is_entry": True})
        else:
            entries.append({"raw": line, "is_entry": False})
    return entries


def extract_file_ref(line: str):  # -> Optional[str]
    """Extract filename from a markdown link: - [Title](file.md) — ..."""
    match = re.search(r'\[.*?\]\((.+?)\)', line)
    return match.group(1) if match else None


def apply_stale_tag(line: str, date_str: str) -> str:
    """Add or update [stale: DATE] tag on a MEMORY.md index line."""
    # Remove existing stale tag if present
    cleaned = re.sub(r'\s*\[stale:[^\]]*\]', '', line).rstrip()
    return f"{cleaned} [stale: {date_str}]"


def remove_stale_tag(line: str) -> str:
    return re.sub(r'\s*\[stale:[^\]]*\]', '', line).rstrip()


def main() -> None:
    try:
        project_root = find_project_root()
        memory_dir = get_memory_dir(project_root)
        memory_index = memory_dir / "MEMORY.md"

        if not memory_index.exists():
            print("{}")
            sys.exit(0)

        archive_dir = memory_dir / "archive"
        content = memory_index.read_text(encoding="utf-8")
        entries = parse_memory_entries(content)

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        modified = False

        new_lines = []
        for entry in entries:
            if not entry["is_entry"]:
                new_lines.append(entry["raw"])
                continue

            line = entry["raw"]
            file_ref = extract_file_ref(line)

            if not file_ref:
                new_lines.append(line)
                continue

            memory_file = memory_dir / file_ref

            if not memory_file.exists():
                # File gone — remove from index
                modified = True
                continue

            age_days = get_file_age_days(memory_file)
            weight = decay_weight(age_days)

            if weight < ARCHIVE_THRESHOLD:
                # Archive the memory file
                archive_dir.mkdir(parents=True, exist_ok=True)
                dest = archive_dir / memory_file.name
                shutil.move(str(memory_file), str(dest))
                # Remove line from index (archived)
                modified = True
                continue

            if weight < STALE_THRESHOLD:
                # Mark as stale in index
                if "[stale:" not in line:
                    line = apply_stale_tag(line, today_str)
                    modified = True
            else:
                # Fresh enough — remove stale tag if it had one
                if "[stale:" in line:
                    line = remove_stale_tag(line)
                    modified = True

            new_lines.append(line)

        if modified:
            new_content = "\n".join(new_lines)
            # Ensure single trailing newline
            new_content = new_content.rstrip() + "\n"
            memory_index.write_text(new_content, encoding="utf-8")

    except Exception:
        pass  # Never block session start

    print("{}")


if __name__ == "__main__":
    main()
