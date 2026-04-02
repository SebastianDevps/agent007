#!/usr/bin/env python3
"""
sdd-guard.py — Merged SDD Hook: PreToolUse (block reward hacking) + PostToolUse (auto-run tests)

PreToolUse handler:
  Blocks edits that reduce assertion count while tests are failing.
  Decision matrix:
    Tests passing + any edit          → ALLOW
    Tests failing + assertions same+  → ALLOW (fixing code)
    Tests failing + assertions fewer  → DENY (reward hacking)
    No test state                     → ALLOW

PostToolUse handler:
  Fires after every Edit or Write operation. Runs tests in background (~10ms blocking).
  Results are injected as additionalContext into Claude's next message.

Ported from ai-framework (Dario-Arcos). Merged for Agent007 v5.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from typing import Optional

STATE_DIR = "/tmp/agent007-sdd"
PID_FILE = os.path.join(STATE_DIR, "test-runner.pid")
RESULT_FILE = os.path.join(STATE_DIR, "last-test-result.json")
TTL_SECONDS = 600  # 10 minutes

# ---------------------------------------------------------------------------
# Shared: assertion detection
# ---------------------------------------------------------------------------

ASSERTION_PATTERNS = [
    # JavaScript/TypeScript (Jest/Vitest)
    r'expect\s*\(',
    r'\.toBe\s*\(',
    r'\.toEqual\s*\(',
    r'\.toStrictEqual\s*\(',
    r'\.toHaveLength\s*\(',
    r'\.toBeCalledWith\s*\(',
    r'\.toThrow\s*\(',
    r'assert\s*\(',
    # Python (pytest/unittest)
    r'assert\s+',
    r'assertEqual\s*\(',
    r'assertRaises\s*\(',
    r'assertTrue\s*\(',
    r'assertFalse\s*\(',
    # Go
    r't\.Error\s*\(',
    r't\.Errorf\s*\(',
    r't\.Fatal\s*\(',
    r'require\.Equal\s*\(',
    r'assert\.Equal\s*\(',
    # Rust
    r'assert_eq!\s*\(',
    r'assert_ne!\s*\(',
    r'assert!\s*\(',
]

ASSERTION_RE = re.compile("|".join(ASSERTION_PATTERNS), re.MULTILINE)

TEST_FILE_PATTERNS = [
    r'\.test\.(ts|tsx|js|jsx)$',
    r'\.spec\.(ts|tsx|js|jsx)$',
    r'_test\.go$',
    r'test_.*\.py$',
    r'.*_test\.py$',
    r'\.test\.rs$',
]
TEST_FILE_RE = re.compile("|".join(TEST_FILE_PATTERNS))

EXEMPT_PATTERNS = [
    ".claude/", ".git/", "node_modules/", "dist/", ".worktrees/",
    "__pycache__/", ".pytest_cache/", "coverage/", ".nyc_output/",
    "docs/", "README", "CHANGELOG", "LICENSE", ".md"
]

SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs"}


def is_test_file(path: str) -> bool:
    return bool(TEST_FILE_RE.search(path))


def is_source_file(path: str) -> bool:
    if not path:
        return False
    if any(pat in path for pat in EXEMPT_PATTERNS):
        return False
    _, ext = os.path.splitext(path)
    return ext in SOURCE_EXTENSIONS


def count_assertions(content: str) -> int:
    return len(ASSERTION_RE.findall(content))


def read_current_file_content(file_path: str) -> str:
    try:
        with open(file_path) as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


# ---------------------------------------------------------------------------
# Shared: test state persistence
# ---------------------------------------------------------------------------

def read_test_state() -> Optional[dict]:
    """Read last test run state."""
    if not os.path.exists(RESULT_FILE):
        return None
    try:
        with open(RESULT_FILE) as f:
            result = json.load(f)
        if time.time() - result.get("timestamp", 0) > TTL_SECONDS:
            return None
        return result
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# PreToolUse: anti-reward-hacking guard
# ---------------------------------------------------------------------------

def handle_pre_tool_use(input_data: dict) -> None:
    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not is_test_file(file_path):
        sys.exit(0)

    test_state = read_test_state()
    if not test_state:
        sys.exit(0)

    tests_passing = test_state.get("passed", True)
    if tests_passing:
        sys.exit(0)

    current_content = read_current_file_content(file_path)
    current_assertions = count_assertions(current_content)

    if tool_name == "Write":
        new_content = tool_input.get("content", "")
    elif tool_name == "Edit":
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")
        new_content = current_content.replace(old_string, new_string, 1)
    else:
        new_content = current_content

    new_assertions = count_assertions(new_content)

    if new_assertions < current_assertions:
        reduction = current_assertions - new_assertions
        output = {
            "decision": "block",
            "reason": (
                f"BLOCKED: Tests are failing and this edit reduces assertions "
                f"from {current_assertions} to {new_assertions} ({reduction} fewer).\n\n"
                f"This pattern indicates reward hacking — weakening tests to make them pass "
                f"instead of fixing the code.\n\n"
                f"Required actions:\n"
                f"1. Fix the code to make the existing tests pass\n"
                f"2. Do NOT reduce assertion count while tests are failing\n"
                f"3. If the test is genuinely wrong, fix it — but only increase assertion precision\n\n"
                f"Last test output:\n{test_state.get('output', '')[:1000]}"
            )
        }
        print(json.dumps(output))
        sys.exit(2)

    sys.exit(0)


# ---------------------------------------------------------------------------
# PostToolUse: auto-run tests in background
# ---------------------------------------------------------------------------

def detect_test_command(cwd: str) -> Optional[str]:
    """Detect the test command for the current project."""
    pkg_json = os.path.join(cwd, "package.json")
    if os.path.exists(pkg_json):
        try:
            with open(pkg_json) as f:
                pkg = json.load(f)
            scripts = pkg.get("scripts", {})
            if "test" in scripts:
                if os.path.exists(os.path.join(cwd, "bun.lockb")):
                    return "bun test --timeout 30000 2>&1 | head -100"
                elif os.path.exists(os.path.join(cwd, "pnpm-lock.yaml")):
                    return "pnpm test --passWithNoTests 2>&1 | head -100"
                else:
                    return "npm test -- --passWithNoTests 2>&1 | head -100"
        except (json.JSONDecodeError, OSError):
            pass

    if os.path.exists(os.path.join(cwd, "pyproject.toml")) or \
       os.path.exists(os.path.join(cwd, "pytest.ini")) or \
       os.path.exists(os.path.join(cwd, "setup.cfg")):
        return "python -m pytest --tb=short -q 2>&1 | head -100"

    if os.path.exists(os.path.join(cwd, "go.mod")):
        return "go test ./... 2>&1 | head -100"

    if os.path.exists(os.path.join(cwd, "Cargo.toml")):
        return "cargo test 2>&1 | head -100"

    return None


def is_already_running() -> bool:
    """Check if a test worker is already running."""
    os.makedirs(STATE_DIR, exist_ok=True)
    if not os.path.exists(PID_FILE):
        return False
    try:
        with open(PID_FILE) as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return True
    except (ValueError, OSError, ProcessLookupError):
        return False


def run_tests_background(test_cmd: str, cwd: str) -> None:
    """Fork test process, ~10ms blocking."""
    os.makedirs(STATE_DIR, exist_ok=True)

    worker_script = f"""
import subprocess, json, os, time

result_file = {repr(RESULT_FILE)}
pid_file = {repr(PID_FILE)}

try:
    proc = subprocess.run(
        {repr(test_cmd)},
        shell=True,
        capture_output=True,
        text=True,
        cwd={repr(cwd)},
        timeout=120
    )
    output = (proc.stdout + proc.stderr)[:8192]
    passed = proc.returncode == 0

    with open(result_file, 'w') as f:
        json.dump({{
            'passed': passed,
            'output': output,
            'returncode': proc.returncode,
            'timestamp': time.time(),
            'command': {repr(test_cmd)}
        }}, f)
finally:
    try:
        os.remove(pid_file)
    except OSError:
        pass
"""

    script_file = tempfile.mktemp(suffix=".py", prefix="agent007-test-")
    try:
        with open(script_file, "w") as f:
            f.write(worker_script)

        proc = subprocess.Popen(
            [sys.executable, script_file],
            start_new_session=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        with open(PID_FILE, "w") as f:
            f.write(str(proc.pid))

    except OSError:
        pass


def handle_post_tool_use(input_data: dict) -> None:
    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not is_source_file(file_path):
        sys.exit(0)

    cwd = os.getcwd()
    test_cmd = detect_test_command(cwd)

    if not test_cmd:
        sys.exit(0)

    if not is_already_running():
        run_tests_background(test_cmd, cwd)

    last_result = read_test_state()
    if last_result and not last_result.get("passed", True):
        output = {
            "hookSpecificOutput": {
                "additionalContext": (
                    f"TESTS FAILING (from last run after previous edit):\n"
                    f"Command: {last_result.get('command', 'unknown')}\n"
                    f"Output:\n{last_result.get('output', '')[:2000]}\n\n"
                    f"Fix the failing tests before claiming completion."
                )
            }
        }
        print(json.dumps(output))

    sys.exit(0)


# ---------------------------------------------------------------------------
# Main: route by hook type
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    hook_type = input_data.get("hook_event_name", "")

    if hook_type == "PreToolUse":
        handle_pre_tool_use(input_data)
    elif hook_type == "PostToolUse":
        handle_post_tool_use(input_data)
    else:
        # Fallback: try to detect from context
        # PreToolUse events have no tool_response; PostToolUse do
        if "tool_response" in input_data:
            handle_post_tool_use(input_data)
        else:
            handle_pre_tool_use(input_data)


if __name__ == "__main__":
    main()
