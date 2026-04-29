#!/usr/bin/env python3
"""
SessionStart Hook — Manifest Staleness Detector
Detects when project dependencies or config have changed since last session.
Suggests running project-init if staleness is detected.

Ported from ai-framework (Dario-Arcos).

Two-phase approach (performance-critical):
  Phase 1: os.stat() only — zero file reads — checks mtime of manifest files
  Phase 2: MD5 comparison — only for mtime-changed candidates
Expected execution: <200ms on session start.
"""

import hashlib
import json
import os
import sys
import tempfile
import time

STATE_DIR = os.path.join(tempfile.gettempdir(), "agent007-sdd")
MANIFEST_STATE_FILE = os.path.join(STATE_DIR, "manifest-hashes.json")
STALE_DAYS_THRESHOLD = 30  # Suggest re-init if rules > 30 days old

# Manifest files to monitor (mtime check only in Phase 1)
MANIFEST_FILES = [
    "package.json",
    "package-lock.json",
    "bun.lockb",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "requirements.txt",
    "Cargo.toml",
    "go.mod",
    "tsconfig.json",
    "docker-compose.yml",
    "docker-compose.yaml",
]

def md5_file(path: str) -> str:
    """Compute MD5 of a file."""
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return ""

def phase1_stat(cwd: str) -> dict[str, float]:
    """Phase 1: stat() only — returns {path: mtime} for files that exist."""
    result = {}
    for manifest in MANIFEST_FILES:
        full_path = os.path.join(cwd, manifest)
        try:
            stat = os.stat(full_path)
            result[manifest] = stat.st_mtime
        except OSError:
            pass
    return result

def load_state() -> dict:
    """Load saved manifest state."""
    os.makedirs(STATE_DIR, exist_ok=True)
    if not os.path.exists(MANIFEST_STATE_FILE):
        return {}
    try:
        with open(MANIFEST_STATE_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def save_state(state: dict):
    """Save manifest state."""
    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        with open(MANIFEST_STATE_FILE, "w") as f:
            json.dump(state, f)
    except OSError:
        pass

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        input_data = {}

    cwd = os.getcwd()
    saved_state = load_state()

    # Phase 1: stat all manifests
    current_mtimes = phase1_stat(cwd)

    if not current_mtimes:
        # No manifests found — might be a non-project directory
        sys.exit(0)

    # Compare mtimes to detect candidates for Phase 2
    saved_mtimes = saved_state.get("mtimes", {})
    changed_files = []

    for manifest, mtime in current_mtimes.items():
        if saved_mtimes.get(manifest, 0) != mtime:
            changed_files.append(manifest)

    if not changed_files and saved_state:
        # Nothing changed since last session
        sys.exit(0)

    # Phase 2: MD5 comparison only for changed candidates
    saved_hashes = saved_state.get("hashes", {})
    actually_changed = []

    for manifest in changed_files:
        full_path = os.path.join(cwd, manifest)
        new_hash = md5_file(full_path)
        old_hash = saved_hashes.get(manifest, "")
        if new_hash != old_hash:
            actually_changed.append(manifest)
        # Update saved hash regardless
        saved_hashes[manifest] = new_hash

    # Save updated state
    new_state = {
        "mtimes": current_mtimes,
        "hashes": saved_hashes,
        "last_check": time.time()
    }
    save_state(new_state)

    if not actually_changed:
        sys.exit(0)

    # Manifests actually changed — build advisory message
    changed_list = ", ".join(actually_changed)
    context_msg = (
        f"📦 Project dependencies changed since last session: {changed_list}\n"
        f"Consider running `npm install` / `pip install` / equivalent if you haven't already.\n"
        f"If project configuration seems stale, the project-init skill can refresh it."
    )

    output = {
        "hookSpecificOutput": {
            "additionalContext": context_msg
        }
    }

    print(json.dumps(output))
    sys.exit(0)

if __name__ == "__main__":
    main()
