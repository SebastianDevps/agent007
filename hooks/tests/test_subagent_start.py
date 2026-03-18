#!/usr/bin/env python3
"""
Tests for subagent-start.py — Skill Registry Injection Hook

Run: python3 -m pytest .claude/hooks/tests/test_subagent_start.py -v
  or: python3 .claude/hooks/tests/test_subagent_start.py
"""

import importlib.util
import json
import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "subagent-start.py")


def load_hook():
    spec = importlib.util.spec_from_file_location("subagent_start", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSubagentStart(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()

    def _run_main(self, stdin_data: str) -> dict:
        """Helper: run main() with given stdin, capture stdout, return parsed JSON."""
        with patch("sys.stdin", StringIO(stdin_data)), \
             patch("sys.stdout", new_callable=StringIO) as mock_out, \
             patch("sys.exit"):
            try:
                self.mod.main()
            except SystemExit:
                pass
            output = mock_out.getvalue().strip()
        return json.loads(output) if output else {}

    def test_valid_json_input_returns_hook_specific_output(self):
        """Valid JSON input → output has hookSpecificOutput.additionalContext."""
        result = self._run_main('{"hook_event_name": "SubagentStart"}')
        self.assertIn("hookSpecificOutput", result)
        self.assertIn("additionalContext", result["hookSpecificOutput"])

    def test_invalid_json_input_still_injects_registry(self):
        """Malformed JSON → still outputs the skill registry (hook is non-blocking)."""
        result = self._run_main("not-valid-json")
        self.assertIn("hookSpecificOutput", result)
        self.assertIn("additionalContext", result["hookSpecificOutput"])

    def test_empty_input_still_injects_registry(self):
        """Empty stdin → still outputs the skill registry."""
        result = self._run_main("")
        self.assertIn("hookSpecificOutput", result)

    def test_registry_contains_verification_before_completion(self):
        """Registry must mention verification-before-completion (critical constraint)."""
        result = self._run_main("{}")
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("verification-before-completion", context)

    def test_registry_contains_systematic_debugging(self):
        """Registry must mention systematic-debugging (bug workflow)."""
        result = self._run_main("{}")
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("systematic-debugging", context)

    def test_registry_contains_banned_phrases_section(self):
        """Registry must include banned phrases guidance."""
        result = self._run_main("{}")
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Banned Phrases", context)
        self.assertIn("should work", context)

    def test_registry_contains_sop_pipeline_skills(self):
        """Registry must mention the SOP pipeline skills."""
        result = self._run_main("{}")
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("sop-discovery", context)
        self.assertIn("sop-code-assist", context)
        self.assertIn("sop-reviewer", context)

    def test_output_is_valid_json(self):
        """Output must always be valid JSON."""
        for stdin in ['{}', 'invalid', '', '{"key": "value"}']:
            result = self._run_main(stdin)
            self.assertIsInstance(result, dict, f"Output not a dict for stdin: {stdin!r}")

    def test_skill_registry_constant_is_non_empty(self):
        """SKILL_REGISTRY constant must be non-empty."""
        self.assertTrue(len(self.mod.SKILL_REGISTRY.strip()) > 100)

    def test_registry_contains_deep_research(self):
        """Registry must mention deep-research for research tasks."""
        result = self._run_main("{}")
        context = result["hookSpecificOutput"]["additionalContext"]
        self.assertIn("deep-research", context)


if __name__ == "__main__":
    unittest.main()
