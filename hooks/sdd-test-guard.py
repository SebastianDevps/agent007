#!/usr/bin/env python3
"""
PreToolUse Hook — Assertion Count Guard (Anti-Reward-Hacking)
Blocks edits that reduce assertion count while tests are failing.

Ported from ai-framework (Dario-Arcos).

The insight: if tests are FAILING and a proposed edit REDUCES assertions,
it's almost certainly reward hacking (weakening tests to make them pass)
rather than legitimate code improvement. Block the edit.

Decision matrix:
  Tests passing + any edit          → ALLOW
  Tests failing + assertions same+  → ALLOW (fixing code)
  Tests failing + assertions fewer  → DENY (reward hacking)
  No test state                     → ALLOW
"""

import json
import os
import re
import sys
import time
from typing import Optional

STATE_DIR = "/tmp/agent007-sdd"
RESULT_FILE = os.path.join(STATE_DIR, "last-test-result.json")
TTL_SECONDS = 600  # 10 minutes

# Language-agnostic assertion patterns
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

def is_test_file(path: str) -> bool:
    return bool(TEST_FILE_RE.search(path))

def count_assertions(content: str) -> int:
    return len(ASSERTION_RE.findall(content))

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

def read_current_file_content(file_path: str) -> str:
    """Read current content of a file before the proposed edit."""
    try:
        with open(file_path) as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""

def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # Allow on parse error

    # Only guard Edit and Write operations
    tool_name = input_data.get("tool_name", "")
    if tool_name not in ("Edit", "Write"):
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    # Only guard test files
    if not is_test_file(file_path):
        sys.exit(0)

    # Check current test state
    test_state = read_test_state()
    if not test_state:
        sys.exit(0)  # No state = allow

    tests_passing = test_state.get("passed", True)
    if tests_passing:
        sys.exit(0)  # Tests passing = allow any edit

    # Tests are FAILING. Count assertions before and after proposed edit.
    current_content = read_current_file_content(file_path)
    current_assertions = count_assertions(current_content)

    # Get proposed new content
    if tool_name == "Write":
        new_content = tool_input.get("content", "")
    elif tool_name == "Edit":
        # Apply the edit mentally to count assertions
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")
        new_content = current_content.replace(old_string, new_string, 1)
    else:
        new_content = current_content

    new_assertions = count_assertions(new_content)

    if new_assertions < current_assertions:
        # BLOCK: reward hacking detected
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
        sys.exit(2)  # Block the tool call

    # Allow: assertions same or increased
    sys.exit(0)

if __name__ == "__main__":
    main()
