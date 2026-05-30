"""_platform.py — cross-platform helpers for the gent007 harness.

All path returns are pathlib.Path so callers can use forward-slash semantics
even when the underlying OS uses backslash separators.

Tool availability is checked once and cached for the process lifetime via
lru_cache. No third-party dependencies; pure stdlib only.

The leading underscore marks this module as a shared internal helper for
the harness — consumers import it as `from _platform import has_tool, ...`
after adding the harness directory to sys.path, or via relative imports
where applicable.
"""

from __future__ import annotations

import os
import platform
import shutil
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------

def is_windows() -> bool:
    """True on native Windows (cmd / PowerShell / python.exe)."""
    return os.name == "nt"


def is_mac() -> bool:
    """True on macOS (Darwin)."""
    return sys.platform == "darwin"


def is_linux() -> bool:
    """True on Linux (including WSL). Use is_wsl() to distinguish."""
    return sys.platform.startswith("linux")


@lru_cache(maxsize=1)
def is_wsl() -> bool:
    """True if running under Windows Subsystem for Linux.

    Detection reads /proc/version for the 'microsoft' marker.
    Cached for the process lifetime.
    """
    if not is_linux():
        return False
    try:
        with open("/proc/version", "r", encoding="utf-8", errors="ignore") as fh:
            return "microsoft" in fh.read().lower()
    except OSError:
        return False


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def home_dir() -> Path:
    """User home directory. Path.home() resolves USERPROFILE on Windows."""
    return Path.home()


def temp_dir() -> Path:
    """System temp directory. Replaces hardcoded '/tmp/' literals."""
    return Path(tempfile.gettempdir())


def claude_projects_dir() -> Path:
    """Layout where Claude Code stores per-project state.

    Identical on all platforms: ~/.claude/projects/<slug>/...
    """
    return home_dir() / ".claude" / "projects"


def find_transcript_for_session(
    session_id: str,
    project_slug: Optional[str] = None,
) -> Optional[Path]:
    """Locate the JSONL transcript file for a given session_id.

    project_slug defaults to the current cwd's encoded slug (Mac/Linux:
    replace '/' with '-'). Returns None if no matching file is found.
    """
    projects = claude_projects_dir()
    if not projects.is_dir():
        return None

    if project_slug is None:
        cwd = str(Path.cwd())
        project_slug = cwd.replace(os.sep, "-").replace("/", "-")

    # Search the slug-specific dir first, then fall back to any project dir
    candidates = [projects / project_slug] if project_slug else []
    candidates.extend(p for p in projects.iterdir() if p.is_dir())

    seen: set[Path] = set()
    for base in candidates:
        if base in seen or not base.is_dir():
            continue
        seen.add(base)
        match = base / f"{session_id}.jsonl"
        if match.is_file():
            return match
        # Fallback: nested under sessions/
        nested = base / "sessions" / f"{session_id}.jsonl"
        if nested.is_file():
            return nested
    return None


def find_hook_root(start: Optional[Path] = None) -> Optional[Path]:
    """Walk up from start (default cwd) until finding a `.claude/harness` dir.

    Returns the parent of that .claude dir (the project root), or None if
    not found. Replaces the POSIX while-loop embedded in settings.json.
    """
    current = (start or Path.cwd()).resolve()
    for ancestor in (current, *current.parents):
        if (ancestor / ".claude" / "harness").is_dir():
            return ancestor
    return None


# ---------------------------------------------------------------------------
# Tool availability
# ---------------------------------------------------------------------------

@lru_cache(maxsize=32)
def has_tool(name: str) -> bool:
    """True if `name` is on PATH and executable. shutil.which handles
    .exe/.cmd resolution on Windows. Cached for the process lifetime.
    """
    return shutil.which(name) is not None


def python_executable() -> str:
    """Resolve the python interpreter name to use in shell commands.

    Returns 'python3' if available, else 'python'. Windows ships 'python'
    but not 'python3' by default; Unix typically ships both.
    """
    return "python3" if has_tool("python3") else "python"


def shell_for_scripts() -> str:
    """Path to bash, or empty string if unavailable (Windows native).

    Callers must check the return value before invoking subprocess with
    bash scripts — never assume a shell exists.
    """
    return shutil.which("bash") or ""
