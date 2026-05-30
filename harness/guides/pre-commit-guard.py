#!/usr/bin/env python3
"""
pre-commit-guard.py — PreToolUse hook (matcher: Bash)

Intercepts `git commit` commands before execution to enforce:
  1. No staged secrets (API_KEY=, SECRET=, PASSWORD=, TOKEN= with hardcoded values)
  2. No .env files in staged area
  3. No debugger statements
  4. Warnings for console.log/debug/warn (ask, not block)
  5. Commit message format: tipo|TASK-ID|YYYYMMDD|descripción

Decision protocol:
  CRITICAL (secrets, .env staged)  → {"decision": "block", "reason": "..."}
  WARNING  (console.log, format)   → {"decision": "ask",   "reason": "..."}
  CLEAN                            → passthrough (stdout = original stdin)

Input  (stdin): Claude Code PreToolUse JSON with tool_name=Bash
Output (stdout):
  block/ask → JSON decision
  passthru  → original stdin unchanged

Performance: < 50ms (subprocess to `git diff --cached`)
"""

import json
import os
import re
import subprocess
import sys
from typing import List, Optional

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Secrets: KEY/SECRET/PASSWORD/TOKEN followed by = and a non-placeholder value
_SECRET_RE = re.compile(
    r'(?:API_KEY|SECRET(?:_KEY)?|PASSWORD|TOKEN|PRIVATE_KEY)\s*=\s*["\']?(?!your_|<|{|placeholder|example|changeme|xxx|test)[A-Za-z0-9+/._\-]{8,}',
    re.IGNORECASE,
)

_DEBUGGER_RE = re.compile(r'^\+.*\bdebugger\b', re.MULTILINE)

_CONSOLE_RE  = re.compile(r'^\+.*\bconsole\.(log|debug|warn)\s*\(', re.MULTILINE)

# Agent007 pipe-delimited commit format: tipo|TASK-ID|YYYYMMDD|descripción
# tipo: feat|fix|refactor|docs|test|chore|perf|style|ci|build|revert|wip
_COMMIT_MSG_RE = re.compile(
    r'^(feat|fix|refactor|docs|test|chore|perf|style|ci|build|revert|wip)\|'
    r'[A-Z0-9_\-]+\|'
    r'20\d{6}\|'
    r'.{3,}',
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_git_commit(command: str) -> bool:
    """Return True if the bash command is a git commit invocation."""
    stripped = command.strip()
    return bool(
        re.match(r'git\s+commit\b', stripped) or
        re.match(r'git\s+-C\s+\S+\s+commit\b', stripped)
    )


def _get_staged_diff() -> str:  # noqa: E302
    """Return the full diff of staged files. Empty string on failure."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--unified=0"],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def _get_staged_filenames() -> List[str]:
    """Return list of staged file paths."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=10,
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def _extract_commit_message(command: str) -> Optional[str]:
    """Extract -m '...' or -m "..." from the git commit command."""
    m = re.search(r'-m\s+["\'](.+?)["\']', command, re.DOTALL)
    if m:
        return m.group(1).strip()
    m = re.search(r'-m\s+(\S+)', command)
    if m:
        return m.group(1).strip()
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    raw = sys.stdin.read()

    try:
        data = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, ValueError):
        sys.stdout.write(raw)
        sys.exit(0)

    tool_name = data.get("tool_name") or data.get("toolName") or ""
    if tool_name != "Bash":
        sys.stdout.write(raw)
        sys.exit(0)

    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    command = tool_input.get("command") or ""

    if not _is_git_commit(command):
        sys.stdout.write(raw)
        sys.exit(0)

    # --- Staged file checks ---
    staged_files = _get_staged_filenames()
    diff = _get_staged_diff()

    issues_critical: List[str] = []
    issues_warnings: List[str] = []

    # 1. .env files staged
    env_staged = [f for f in staged_files if os.path.basename(f) == ".env" or f.endswith("/.env")]
    if env_staged:
        issues_critical.append(f".env file(s) staged: {', '.join(env_staged)}")

    # 2. Secrets in diff
    secret_matches = _SECRET_RE.findall(diff)
    if secret_matches:
        preview = secret_matches[0][:60] + ("..." if len(secret_matches[0]) > 60 else "")
        issues_critical.append(
            f"Potential secret detected in staged changes: `{preview}` "
            f"({len(secret_matches)} match(es))"
        )

    # 3. Debugger statements
    if _DEBUGGER_RE.search(diff):
        issues_critical.append("debugger statement found in staged changes")

    # 4. console.log / console.debug / console.warn
    console_matches = _CONSOLE_RE.findall(diff)
    if console_matches:
        methods = list({m for m in console_matches})
        # Find which files contain them
        console_files: List[str] = []
        current_file = ""
        for line in diff.splitlines():
            if line.startswith("diff --git"):
                parts = line.split(" b/")
                current_file = parts[-1] if len(parts) > 1 else ""
            elif _CONSOLE_RE.match(line) and current_file and current_file not in console_files:
                console_files.append(current_file)
        file_list = ", ".join(console_files) if console_files else "staged files"
        issues_warnings.append(
            f"console.{'/'.join(methods)} found in {file_list} — consider removing debug output"
        )

    # 5. Commit message format validation
    commit_msg = _extract_commit_message(command)
    if commit_msg is not None and not _COMMIT_MSG_RE.match(commit_msg):
        issues_warnings.append(
            f"Commit message '{commit_msg[:60]}' does not match Agent007 format: "
            f"tipo|TASK-ID|YYYYMMDD|descripción  "
            f"(e.g. feat|GAP-007|20260329|Add pre-commit guard)"
        )

    # --- Decision ---
    if issues_critical:
        sys.stderr.write(f"pre-commit-guard: BLOCKED — {'; '.join(issues_critical)}\n")
        sys.stderr.flush()
        response = {
            "decision": "block",
            "reason": (
                "Pre-commit guard blocked this commit:\n" +
                "\n".join(f"  • {i}" for i in issues_critical) +
                ("\n\nAlso noted (warnings):\n" + "\n".join(f"  • {w}" for w in issues_warnings) if issues_warnings else "")
            ),
        }
        sys.stdout.write(json.dumps(response))
        sys.exit(0)

    if issues_warnings:
        sys.stderr.write(f"pre-commit-guard: WARN — {'; '.join(issues_warnings)}\n")
        sys.stderr.flush()
        response = {
            "decision": "ask",
            "reason": (
                "Pre-commit guard found the following issues:\n" +
                "\n".join(f"  • {w}" for w in issues_warnings) +
                "\n\nProceed with commit anyway?"
            ),
        }
        sys.stdout.write(json.dumps(response))
        sys.exit(0)

    # All clean — passthrough
    sys.stdout.write(raw)
    sys.exit(0)


if __name__ == "__main__":
    main()
