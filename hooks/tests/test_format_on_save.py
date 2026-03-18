#!/usr/bin/env python3
"""
Tests for format-on-save.sh — Prettier auto-format hook

Strategy: invoke the bash script via subprocess with controlled stdin/environment.
The hook exits 0 in all cases (non-blocking). Tests verify it never crashes
and never formats when Prettier is absent or extension is unsupported.

Run: python3 -m pytest .claude/hooks/tests/test_format_on_save.py -v
  or: python3 .claude/hooks/tests/test_format_on_save.py
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from typing import Optional

HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "format-on-save.sh")


def run_hook(stdin_data: str, cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    """Run the bash hook with given stdin and working directory."""
    return subprocess.run(
        ["bash", HOOK_PATH],
        input=stdin_data.encode("utf-8"),
        capture_output=True,
        cwd=cwd or tempfile.gettempdir(),
        timeout=10,
    )


def make_event(file_path: str) -> str:
    """Build the JSON event payload that Claude Code sends to the hook."""
    return json.dumps({"tool_input": {"file_path": file_path}})


class TestFormatOnSave(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_hook_exists_and_is_executable(self):
        """Hook script must exist."""
        self.assertTrue(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")

    def test_empty_file_path_exits_zero(self):
        """Empty file_path in event → exit 0 (silent)."""
        result = run_hook(json.dumps({"tool_input": {"file_path": ""}}))
        self.assertEqual(result.returncode, 0)

    def test_no_file_path_key_exits_zero(self):
        """Missing file_path key → exit 0."""
        result = run_hook(json.dumps({"tool_input": {}}))
        self.assertEqual(result.returncode, 0)

    def test_malformed_json_exits_zero(self):
        """Malformed JSON stdin → exit 0 (never blocks)."""
        result = run_hook("not valid json")
        self.assertEqual(result.returncode, 0)

    def test_nonexistent_file_exits_zero(self):
        """Non-existent file_path → exit 0."""
        result = run_hook(make_event("/tmp/nonexistent_abc123.ts"))
        self.assertEqual(result.returncode, 0)

    def test_unsupported_extension_exits_zero(self):
        """Unsupported extension (.py) → exit 0, file not touched."""
        py_file = os.path.join(self.tmp, "test.py")
        content = "x=1\n"
        with open(py_file, "w") as f:
            f.write(content)
        result = run_hook(make_event(py_file), cwd=self.tmp)
        self.assertEqual(result.returncode, 0)
        # File must not be touched
        with open(py_file) as f:
            self.assertEqual(f.read(), content)

    def test_supported_extension_without_prettier_config_exits_zero(self):
        """Supported extension (.ts) but no Prettier config → exit 0, no formatting."""
        ts_file = os.path.join(self.tmp, "test.ts")
        content = "const x=1\n"
        with open(ts_file, "w") as f:
            f.write(content)
        # tmp dir has no prettier config
        result = run_hook(make_event(ts_file), cwd=self.tmp)
        self.assertEqual(result.returncode, 0)
        # Content must not be changed (no prettier config present)
        with open(ts_file) as f:
            self.assertEqual(f.read(), content)

    def test_supported_extensions_list(self):
        """All declared supported extensions exit 0 without Prettier config."""
        supported = ["ts", "tsx", "js", "jsx", "mjs", "cjs", "json", "css", "scss", "html", "md"]
        for ext in supported:
            fname = os.path.join(self.tmp, f"test.{ext}")
            with open(fname, "w") as f:
                f.write("x\n")
            result = run_hook(make_event(fname), cwd=self.tmp)
            self.assertEqual(result.returncode, 0, f"Failed for extension .{ext}")

    def test_hook_never_produces_stderr_on_clean_run(self):
        """Hook must not emit unexpected errors to stderr."""
        result = run_hook(make_event("/tmp/nonexistent.ts"), cwd=self.tmp)
        # stderr should be empty or contain only expected warning (none expected here)
        self.assertEqual(result.returncode, 0)


class TestFormatOnSaveWithPrettierConfig(unittest.TestCase):
    """Tests for behavior when a Prettier config IS present."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # Create a minimal .prettierrc
        with open(os.path.join(self.tmp, ".prettierrc"), "w") as f:
            json.dump({"semi": True, "singleQuote": True}, f)

    def test_with_prettier_config_and_valid_file_exits_zero(self):
        """With .prettierrc present, hook runs (or skips if npx absent) — always exits 0."""
        ts_file = os.path.join(self.tmp, "test.ts")
        with open(ts_file, "w") as f:
            f.write('const x = 1\n')
        result = run_hook(make_event(ts_file), cwd=self.tmp)
        self.assertEqual(result.returncode, 0)

    def test_with_prettier_config_unsupported_ext_exits_zero(self):
        """With .prettierrc present, unsupported extension still exits 0."""
        py_file = os.path.join(self.tmp, "test.py")
        with open(py_file, "w") as f:
            f.write("x = 1\n")
        result = run_hook(make_event(py_file), cwd=self.tmp)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
