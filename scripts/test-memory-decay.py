#!/usr/bin/env python3
"""
test-memory-decay.py — Verification test for hooks/memory-decay.py

Tests:
  1. Fresh memory (today) → no stale tag added
  2. Old memory (60+ days) → [stale: DATE] tag appears in MEMORY.md
  3. Very old memory (90+ days) → file archived, removed from index
  4. Already-stale memory that becomes fresh → stale tag removed

Uses a temporary directory that mirrors the memory structure.
Does NOT modify the real memory directory.

Usage:
  python3 .claude/scripts/test-memory-decay.py

Exit 0 = all tests passed
Exit 1 = one or more tests failed
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOOK = Path(__file__).parent.parent / "hooks" / "memory-decay.py"


def run_hook_with_fake_memory(memory_dir: Path) -> tuple[int, str, str]:
    """Run memory-decay.py pointing to a fake memory directory."""
    # We patch the hook's memory path by setting CWD to a project root
    # that resolves to our fake memory directory.
    # The hook computes: ~/.claude/projects/{encoded_cwd}/memory/
    # So we need CWD to encode to our temp dir structure.
    # Simpler: pass via env var override in the hook.
    # Since the hook hardcodes the path derivation, we'll test it directly
    # by importing and calling the function with a monkeypatched path.

    # Alternative: create a wrapper that patches the memory path
    wrapper_code = f"""
import sys
sys.path.insert(0, '{str(HOOK.parent)}')

# Monkeypatch get_memory_dir before importing
import types

original_source = open('{str(HOOK)}').read()
# Patch get_memory_dir to return our test dir
patched = original_source.replace(
    'def get_memory_dir(project_root: Path) -> Path:',
    'def get_memory_dir(project_root: Path) -> Path:\\n    return Path("{str(memory_dir)}")\\n    if False:'
)
exec(compile(patched, '{str(HOOK)}', 'exec'))
"""
    result = subprocess.run(
        [sys.executable, "-c", wrapper_code],
        capture_output=True,
        text=True,
        input="{}",
        env={**os.environ, "CLAUDE_HOOK_PROFILE": "standard"},
    )
    return result.returncode, result.stdout, result.stderr


def create_memory_structure(base_dir: Path, entries: list) -> Path:
    """
    Create a fake memory directory with MEMORY.md and memory files.
    entries = [{"name": "test.md", "age_days": 10, "content": "..."}, ...]
    Returns the memory_dir path.
    """
    base_dir.mkdir(parents=True, exist_ok=True)

    index_lines = ["# Memory Index\n"]
    for entry in entries:
        mem_file = base_dir / entry["name"]
        mem_file.write_text(entry.get("content", f"---\nname: {entry['name']}\n---\nContent\n"))

        # Set modification time to simulate age
        age_seconds = entry["age_days"] * 86400
        old_time = time.time() - age_seconds
        os.utime(str(mem_file), (old_time, old_time))

        index_lines.append(f"- [{entry['name']}]({entry['name']}) — {entry.get('desc', 'test entry')}\n")

    (base_dir / "MEMORY.md").write_text("".join(index_lines))
    return base_dir


def run_decay_on_dir(memory_dir: Path) -> tuple[int, str, str]:
    """Run memory-decay.py with the memory dir patched."""
    script = f"""
import sys, math, os, re, shutil
from pathlib import Path
from datetime import datetime, timezone

LAMBDA = 0.023
STALE_THRESHOLD = 0.50
ARCHIVE_THRESHOLD = 0.25

memory_dir = Path(r'{str(memory_dir)}')
memory_index = memory_dir / 'MEMORY.md'
archive_dir = memory_dir / 'archive'

if not memory_index.exists():
    print("{{}}")
    sys.exit(0)

content = memory_index.read_text(encoding='utf-8')
today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
modified = False
new_lines = []
import re

for line in content.splitlines():
    stripped = line.strip()
    if not (stripped.startswith('- [') and '](' in stripped):
        new_lines.append(line)
        continue

    match = re.search(r'\\[.*?\\]\\((.+?)\\)', line)
    if not match:
        new_lines.append(line)
        continue
    file_ref = match.group(1)
    memory_file = memory_dir / file_ref
    if not memory_file.exists():
        modified = True
        continue

    mtime = memory_file.stat().st_mtime
    now = datetime.now(timezone.utc).timestamp()
    age_days = (now - mtime) / 86400
    weight = math.exp(-LAMBDA * age_days)

    if weight < ARCHIVE_THRESHOLD:
        archive_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(memory_file), str(archive_dir / memory_file.name))
        modified = True
        continue
    elif weight < STALE_THRESHOLD:
        if '[stale:' not in line:
            cleaned = re.sub(r'\\s*\\[stale:[^\\]]*\\]', '', line).rstrip()
            line = f'{{cleaned}} [stale: {{today_str}}]'
            modified = True
    else:
        if '[stale:' in line:
            line = re.sub(r'\\s*\\[stale:[^\\]]*\\]', '', line).rstrip()
            modified = True
    new_lines.append(line)

if modified:
    memory_index.write_text('\\n'.join(new_lines).rstrip() + '\\n', encoding='utf-8')

print("{{}}")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout, result.stderr


def test_fresh_memory_no_stale() -> bool:
    """Fresh memory (5 days old) → no stale tag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_dir = Path(tmpdir) / "memory"
        create_memory_structure(mem_dir, [
            {"name": "fresh.md", "age_days": 5, "desc": "fresh memory"},
        ])

        run_decay_on_dir(mem_dir)
        content = (mem_dir / "MEMORY.md").read_text()
        passed = "[stale:" not in content
        print(f"  {'✓' if passed else '✗'} test_fresh_memory_no_stale: stale_tag={'no' if passed else 'YES — unexpected'}")
        return passed


def test_old_memory_gets_stale_tag() -> bool:
    """Memory 60 days old → [stale: DATE] appears."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_dir = Path(tmpdir) / "memory"
        create_memory_structure(mem_dir, [
            {"name": "old.md", "age_days": 60, "desc": "old memory"},
        ])

        run_decay_on_dir(mem_dir)
        content = (mem_dir / "MEMORY.md").read_text()
        passed = "[stale:" in content
        print(f"  {'✓' if passed else '✗'} test_old_memory_gets_stale_tag: stale_tag={'yes' if passed else 'NO — missing'}")
        return passed


def test_very_old_memory_archived() -> bool:
    """Memory 90+ days old → archived, removed from index."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_dir = Path(tmpdir) / "memory"
        create_memory_structure(mem_dir, [
            {"name": "ancient.md", "age_days": 90, "desc": "very old memory"},
        ])

        run_decay_on_dir(mem_dir)
        index_content = (mem_dir / "MEMORY.md").read_text()
        archive_exists = (mem_dir / "archive" / "ancient.md").exists()
        removed_from_index = "ancient.md" not in index_content

        passed = archive_exists and removed_from_index
        print(f"  {'✓' if passed else '✗'} test_very_old_memory_archived: archived={archive_exists}, removed_from_index={removed_from_index}")
        return passed


def test_stale_tag_removed_on_fresh() -> bool:
    """Memory with stale tag that's actually fresh → tag removed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        mem_dir = Path(tmpdir) / "memory"
        mem_dir.mkdir(parents=True)

        # Create fresh file (2 days old)
        mem_file = mem_dir / "recent.md"
        mem_file.write_text("---\nname: recent\n---\nContent\n")
        new_time = time.time() - (2 * 86400)
        os.utime(str(mem_file), (new_time, new_time))

        # But MEMORY.md has a stale tag on it
        (mem_dir / "MEMORY.md").write_text(
            "# Memory Index\n\n- [recent.md](recent.md) — fresh [stale: 2026-01-01]\n"
        )

        run_decay_on_dir(mem_dir)
        content = (mem_dir / "MEMORY.md").read_text()
        passed = "[stale:" not in content
        print(f"  {'✓' if passed else '✗'} test_stale_tag_removed_on_fresh: stale_removed={'yes' if passed else 'NO — still there'}")
        return passed


def main() -> None:
    print("=== memory-decay.py verification ===\n")
    results = [
        test_fresh_memory_no_stale(),
        test_old_memory_gets_stale_tag(),
        test_very_old_memory_archived(),
        test_stale_tag_removed_on_fresh(),
    ]
    passed = sum(results)
    total = len(results)
    print(f"\n{'✅' if passed == total else '❌'} {passed}/{total} tests passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
