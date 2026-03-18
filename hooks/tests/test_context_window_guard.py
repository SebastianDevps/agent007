#!/usr/bin/env python3
"""
Tests for context-window-guard.py — PostToolUse Context Window Monitor

Run: python3 -m pytest .claude/hooks/tests/test_context_window_guard.py -v
"""

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch


HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "context-window-guard.py")


def load_hook():
    spec = importlib.util.spec_from_file_location("context_window_guard", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestReadStdinPayload(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()

    def test_returns_none_for_empty_stdin(self):
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.read.return_value = ""
            result = self.mod.read_stdin_payload()
        self.assertIsNone(result)

    def test_returns_dict_for_valid_json(self):
        payload = {"context_window": {"remaining_percentage": 45.0}}
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.read.return_value = json.dumps(payload)
            result = self.mod.read_stdin_payload()
        self.assertEqual(result["context_window"]["remaining_percentage"], 45.0)

    def test_returns_none_for_invalid_json(self):
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.read.return_value = "not-json"
            result = self.mod.read_stdin_payload()
        self.assertIsNone(result)


class TestExtractRemainingPercentage(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()

    def test_extracts_from_context_window_dict(self):
        payload = {"context_window": {"remaining_percentage": 42.5}}
        result = self.mod.extract_remaining_percentage(payload)
        self.assertAlmostEqual(result, 42.5)

    def test_extracts_from_nested_hook_event_data(self):
        payload = {
            "hook_event_data": {
                "context_window": {"remaining_percentage": 20.0}
            }
        }
        result = self.mod.extract_remaining_percentage(payload)
        self.assertAlmostEqual(result, 20.0)

    def test_computes_from_tokens_remaining_and_total(self):
        payload = {"context_window": {"tokens_remaining": 25000, "tokens_total": 100000}}
        result = self.mod.extract_remaining_percentage(payload)
        self.assertAlmostEqual(result, 25.0)

    def test_returns_none_when_no_context_window_data(self):
        payload = {"tool_name": "Read", "some_other_key": "value"}
        result = self.mod.extract_remaining_percentage(payload)
        self.assertIsNone(result)

    def test_returns_none_for_none_payload(self):
        result = self.mod.extract_remaining_percentage(None)
        self.assertIsNone(result)


class TestDebounce(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()
        self.tmpdir = tempfile.mkdtemp()
        self.session_id = "test-session-123"

    def _debounce_path(self):
        return f"/tmp/agent007-ctx-{self.session_id}-warned.json"

    def tearDown(self):
        try:
            os.unlink(self._debounce_path())
        except FileNotFoundError:
            pass

    def test_should_warn_when_no_prior_state(self):
        # No debounce file — should warn
        self.assertTrue(self.mod.should_warn(self.session_id, is_critical=False))

    def test_critical_always_bypasses_debounce(self):
        # Even if we just warned, critical always fires
        self.mod.record_tool_use(self.session_id, warned=True)
        self.assertTrue(self.mod.should_warn(self.session_id, is_critical=True))

    def test_warning_suppressed_within_debounce_window(self):
        # Warn once, then check — should be suppressed for next 4 tool uses
        self.mod.record_tool_use(self.session_id, warned=True)
        self.assertFalse(self.mod.should_warn(self.session_id, is_critical=False))

    def test_warning_fires_after_debounce_window(self):
        # Warn once, then advance DEBOUNCE_TOOL_USES tool-uses without warning
        self.mod.record_tool_use(self.session_id, warned=True)
        for _ in range(self.mod.DEBOUNCE_TOOL_USES):
            self.mod.record_tool_use(self.session_id, warned=False)
        self.assertTrue(self.mod.should_warn(self.session_id, is_critical=False))


class TestOutputBuilders(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()

    def test_warning_output_contains_percentage(self):
        output = self.mod.build_warning_output(28.5)
        text = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("28.5", text)
        self.assertIn("⚠️", text)

    def test_critical_output_contains_percentage_and_actions(self):
        output = self.mod.build_critical_output(10.2)
        text = output["hookSpecificOutput"]["additionalContext"]
        self.assertIn("10.2", text)
        self.assertIn("🔴", text)
        self.assertIn("commit", text.lower())


class TestMainBehavior(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()
        self.session_id = "main-test-session"

    def tearDown(self):
        try:
            os.unlink(f"/tmp/agent007-ctx-{self.session_id}-warned.json")
        except FileNotFoundError:
            pass

    def test_main_exits_silently_when_no_context_data(self):
        """main() exits 0 without printing when payload has no context window."""
        payload = {"tool_name": "Read"}
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.read.return_value = json.dumps(payload)
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                with self.assertRaises(SystemExit) as cm:
                    self.mod.main()
        self.assertEqual(cm.exception.code, 0)
        self.assertEqual(mock_out.getvalue().strip(), "")

    def test_main_emits_warning_at_30_percent(self):
        """main() emits warning output when remaining_percentage = 29%."""
        payload = {
            "context_window": {"remaining_percentage": 29.0},
            "session_id": self.session_id
        }
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.read.return_value = json.dumps(payload)
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                with self.assertRaises(SystemExit):
                    self.mod.main()
        output = mock_out.getvalue().strip()
        self.assertTrue(output, "Expected warning output but got empty string")
        data = json.loads(output)
        self.assertIn("hookSpecificOutput", data)

    def test_main_emits_critical_at_15_percent(self):
        """main() emits critical output when remaining_percentage = 10%."""
        payload = {
            "context_window": {"remaining_percentage": 10.0},
            "session_id": self.session_id
        }
        with patch("sys.stdin") as mock_stdin:
            mock_stdin.read.return_value = json.dumps(payload)
            with patch("sys.stdout", new_callable=StringIO) as mock_out:
                with self.assertRaises(SystemExit):
                    self.mod.main()
        output = mock_out.getvalue().strip()
        data = json.loads(output)
        text = data["hookSpecificOutput"]["additionalContext"]
        self.assertIn("🔴", text)

    def test_main_does_not_raise_on_exception(self):
        """main() never raises exceptions — always exits cleanly."""
        with patch.object(self.mod, "read_stdin_payload", side_effect=RuntimeError("boom")):
            try:
                with self.assertRaises(SystemExit) as cm:
                    self.mod.main()
                self.assertEqual(cm.exception.code, 0)
            except Exception:
                self.fail("main() raised an unexpected exception")


if __name__ == "__main__":
    unittest.main()
