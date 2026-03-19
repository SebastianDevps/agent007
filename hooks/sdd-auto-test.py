#!/usr/bin/env python3
"""
PostToolUse Hook — Continuous Background Test Runner (SDD Auto-Test)
Fires after every Edit or Write operation. Runs tests in background (~10ms blocking).
Results are injected as additionalContext into Claude's next message.

Ported from ai-framework (Dario-Arcos). Novel technique: fire-and-forget
subprocess with result injection eliminates the "run tests manually" step.
"""

import json
import os
import subprocess
import sys
import tempfile
import hashlib
import threading
import time
from typing import Optional

STATE_DIR = "/tmp/agent007-sdd"
LOCK_FILE = os.path.join(STATE_DIR, "test-runner.lock")
VITEST_WORKER_FLAGS = "--pool=forks --poolOptions.forks.maxForks=2"
RESULT_FILE = os.path.join(STATE_DIR, "last-test-result.json")
TTL_SECONDS = 600  # 10 minutes

EXEMPT_PATTERNS = [
    ".claude/", ".git/", "node_modules/", "dist/", ".worktrees/",
    "__pycache__/", ".pytest_cache/", "coverage/", ".nyc_output/",
    "docs/", "README", "CHANGELOG", "LICENSE", ".md"
]

SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".py", ".go", ".rs"}

def is_source_file(path: str) -> bool:
    if not path:
        return False
    if any(pat in path for pat in EXEMPT_PATTERNS):
        return False
    _, ext = os.path.splitext(path)
    return ext in SOURCE_EXTENSIONS

def _uses_vitest(scripts: dict) -> bool:
    """Check if the test script invokes vitest."""
    test_val = scripts.get("test", "")
    return "vitest" in test_val

def detect_test_command(cwd: str) -> Optional[str]:
    """Detect the test command for the current project."""
    # Check package.json for test script
    pkg_json = os.path.join(cwd, "package.json")
    if os.path.exists(pkg_json):
        try:
            with open(pkg_json) as f:
                pkg = json.load(f)
            scripts = pkg.get("scripts", {})
            if "test" in scripts:
                # Determine package manager
                if os.path.exists(os.path.join(cwd, "bun.lockb")):
                    if _uses_vitest(scripts):
                        return f"bun test {VITEST_WORKER_FLAGS} --timeout 30000 2>&1 | head -100"
                    return "bun test --timeout 30000 2>&1 | head -100"
                elif os.path.exists(os.path.join(cwd, "pnpm-lock.yaml")):
                    if _uses_vitest(scripts):
                        return f"pnpm test -- {VITEST_WORKER_FLAGS} --passWithNoTests 2>&1 | head -100"
                    return "pnpm test --passWithNoTests 2>&1 | head -100"
                else:
                    if _uses_vitest(scripts):
                        return f"npm test -- {VITEST_WORKER_FLAGS} --passWithNoTests 2>&1 | head -100"
                    return "npm test -- --passWithNoTests 2>&1 | head -100"
        except (json.JSONDecodeError, OSError):
            pass

    # Python
    if os.path.exists(os.path.join(cwd, "pyproject.toml")) or \
       os.path.exists(os.path.join(cwd, "pytest.ini")) or \
       os.path.exists(os.path.join(cwd, "setup.cfg")):
        return "python -m pytest --tb=short -q 2>&1 | head -100"

    # Go
    if os.path.exists(os.path.join(cwd, "go.mod")):
        return "go test ./... 2>&1 | head -100"

    # Rust
    if os.path.exists(os.path.join(cwd, "Cargo.toml")):
        return "cargo test 2>&1 | head -100"

    return None

def acquire_lock() -> bool:
    """Atomic lock using O_CREAT|O_EXCL — no race window between check and create."""
    os.makedirs(STATE_DIR, exist_ok=True)
    try:
        fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        return True
    except FileExistsError:
        # Lock exists — check if owning process is still alive
        try:
            with open(LOCK_FILE) as f:
                pid = int(f.read().strip())
            os.kill(pid, 0)  # Signal 0 = check liveness, raises OSError if dead
            return False  # Process alive — skip this run
        except (ValueError, OSError):
            # Stale lock (process dead) — remove and acquire
            try:
                os.unlink(LOCK_FILE)
            except OSError:
                pass
            return acquire_lock()

def run_tests_background(test_cmd: str, cwd: str):
    """Fork test process, ~10ms blocking."""
    os.makedirs(STATE_DIR, exist_ok=True)

    # Write worker script to tmp file
    worker_script = f"""
import subprocess, json, os, time

result_file = {repr(RESULT_FILE)}
lock_file = {repr(LOCK_FILE)}

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
        os.remove(lock_file)
    except OSError:
        pass
"""

    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', prefix='agent007-test-', delete=False) as tf:
            tf.write(worker_script)
            script_file = tf.name

        proc = subprocess.Popen(
            [sys.executable, script_file],
            start_new_session=True,  # Detach from parent
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Update lock with child PID — parent exits soon, child holds the lock
        try:
            with open(LOCK_FILE, 'w') as f:
                f.write(str(proc.pid))
        except OSError:
            pass

        # Cleanup temp script after child has had time to read it
        def _cleanup_script(path: str) -> None:
            time.sleep(1.0)
            try:
                os.unlink(path)
            except OSError:
                pass

        threading.Thread(target=_cleanup_script, args=(script_file,), daemon=True).start()

    except OSError:
        pass  # Best effort — never block Claude

def read_last_result() -> Optional[dict]:
    """Read the most recent test result if fresh."""
    if not os.path.exists(RESULT_FILE):
        return None
    try:
        with open(RESULT_FILE) as f:
            result = json.load(f)
        # Expire after TTL
        if time.time() - result.get("timestamp", 0) > TTL_SECONDS:
            return None
        return result
    except (json.JSONDecodeError, OSError):
        return None

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    # Only act on Edit/Write tool calls
    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    # Get the file that was modified
    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Skip non-source files
    if not is_source_file(file_path):
        sys.exit(0)

    cwd = os.getcwd()
    test_cmd = detect_test_command(cwd)

    if not test_cmd:
        sys.exit(0)

    # Start background test run (atomic lock — no race window)
    if acquire_lock():
        run_tests_background(test_cmd, cwd)

    # Check if previous run result is ready to report
    last_result = read_last_result()
    if last_result and not last_result.get("passed", True):
        # Inject failing test context into Claude's next message
        output = {
            "hookSpecificOutput": {
                "additionalContext": (
                    f"⚠️ TESTS FAILING (from last run after previous edit):\n"
                    f"Command: {last_result.get('command', 'unknown')}\n"
                    f"Output:\n{last_result.get('output', '')[:2000]}\n\n"
                    f"Fix the failing tests before claiming completion."
                )
            }
        }
        print(json.dumps(output))

    sys.exit(0)

if __name__ == "__main__":
    main()
