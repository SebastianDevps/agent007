#!/usr/bin/env python3
"""
Tests for constraint-reinforcement.py — UserPromptSubmit constraint injection hook

Run: python3 -m pytest .claude/hooks/tests/test_constraint_reinforcement.py -v
  or: python3 .claude/hooks/tests/test_constraint_reinforcement.py
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "constraint-reinforcement.py")


def load_hook():
    spec = importlib.util.spec_from_file_location("constraint_reinforcement", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_hook(stdin_data: str):
    """Run the hook as subprocess, return (returncode, parsed_output_or_empty_dict)."""
    result = subprocess.run(
        [sys.executable, HOOK_PATH],
        input=stdin_data.encode("utf-8"),
        capture_output=True,
        timeout=10,
    )
    raw = result.stdout.decode("utf-8").strip()
    output = json.loads(raw) if raw else {}
    return result.returncode, output


def make_transcript(num_user_turns: int, tmp_dir: str) -> str:
    """Create a JSONL transcript with the given number of user turns."""
    path = os.path.join(tmp_dir, "transcript.jsonl")
    with open(path, "w") as f:
        for i in range(num_user_turns):
            f.write(json.dumps({"message": {"role": "user", "content": f"turn {i}"}}) + "\n")
            f.write(json.dumps({"message": {"role": "assistant", "content": f"reply {i}"}}) + "\n")
    return path


class TestCountTurns(unittest.TestCase):
    """Unit tests for count_turns_from_transcript — imported directly."""

    def setUp(self):
        self.mod = load_hook()
        self.tmp = tempfile.mkdtemp()

    def test_counts_user_turns_correctly(self):
        path = make_transcript(10, self.tmp)
        self.assertEqual(self.mod.count_turns_from_transcript(path), 10)

    def test_returns_zero_for_nonexistent_file(self):
        self.assertEqual(self.mod.count_turns_from_transcript("/nonexistent/path.jsonl"), 0)

    def test_returns_zero_for_empty_string_path(self):
        self.assertEqual(self.mod.count_turns_from_transcript(""), 0)

    def test_returns_zero_for_empty_file(self):
        path = os.path.join(self.tmp, "empty.jsonl")
        open(path, "w").close()
        self.assertEqual(self.mod.count_turns_from_transcript(path), 0)

    def test_skips_malformed_lines_gracefully(self):
        path = os.path.join(self.tmp, "mixed.jsonl")
        with open(path, "w") as f:
            f.write('{"message": {"role": "user", "content": "hi"}}\n')
            f.write("NOT VALID JSON\n")
            f.write('{"message": {"role": "user", "content": "bye"}}\n')
        self.assertEqual(self.mod.count_turns_from_transcript(path), 2)

    def test_only_counts_user_role(self):
        path = os.path.join(self.tmp, "roles.jsonl")
        with open(path, "w") as f:
            f.write('{"message": {"role": "user", "content": "u1"}}\n')
            f.write('{"message": {"role": "assistant", "content": "a1"}}\n')
            f.write('{"message": {"role": "system", "content": "s1"}}\n')
        self.assertEqual(self.mod.count_turns_from_transcript(path), 1)

    def test_turn_threshold_constant_is_50(self):
        self.assertEqual(self.mod.TURN_THRESHOLD, 50)

    def test_constraints_constant_is_non_empty(self):
        self.assertTrue(len(self.mod.CONSTRAINTS.strip()) > 100)


class TestConstraintReinforcement(unittest.TestCase):
    """Integration tests running the hook as a subprocess."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_below_threshold_exits_silently(self):
        """< 50 turns → exit 0, no stdout."""
        path = make_transcript(10, self.tmp)
        rc, output = run_hook(json.dumps({"transcript_path": path}))
        self.assertEqual(rc, 0)
        self.assertEqual(output, {})

    def test_at_threshold_injects_constraints(self):
        """Exactly 50 turns → injects additionalContext."""
        path = make_transcript(50, self.tmp)
        rc, output = run_hook(json.dumps({"transcript_path": path}))
        self.assertEqual(rc, 0)
        self.assertIn("additionalContext", output)

    def test_above_threshold_injects_constraints(self):
        """100 turns → injects additionalContext."""
        path = make_transcript(100, self.tmp)
        rc, output = run_hook(json.dumps({"transcript_path": path}))
        self.assertIn("additionalContext", output)

    def test_injected_context_contains_banned_phrases(self):
        path = make_transcript(60, self.tmp)
        _, output = run_hook(json.dumps({"transcript_path": path}))
        context = output.get("additionalContext", "")
        self.assertIn("should work", context)
        self.assertIn("probably", context)

    def test_injected_context_contains_verification_gates(self):
        path = make_transcript(60, self.tmp)
        _, output = run_hook(json.dumps({"transcript_path": path}))
        context = output.get("additionalContext", "")
        self.assertIn("verification-before-completion", context)

    def test_injected_context_contains_sdd_iron_law(self):
        path = make_transcript(60, self.tmp)
        _, output = run_hook(json.dumps({"transcript_path": path}))
        context = output.get("additionalContext", "")
        self.assertIn("SDD Iron Law", context)

    def test_injected_context_contains_turn_count(self):
        path = make_transcript(55, self.tmp)
        _, output = run_hook(json.dumps({"transcript_path": path}))
        context = output.get("additionalContext", "")
        self.assertIn("55", context)

    def test_missing_transcript_path_exits_silently(self):
        """No transcript_path → 0 turns → below threshold → silent."""
        rc, output = run_hook(json.dumps({"other_key": "value"}))
        self.assertEqual(rc, 0)
        self.assertEqual(output, {})

    def test_malformed_json_exits_silently(self):
        """Malformed JSON → exit 0, no output (never blocks)."""
        rc, output = run_hook("not valid json")
        self.assertEqual(rc, 0)
        self.assertEqual(output, {})

    def test_output_is_valid_json_when_injecting(self):
        """Output when injecting must be valid JSON."""
        path = make_transcript(60, self.tmp)
        rc, output = run_hook(json.dumps({"transcript_path": path}))
        self.assertIsInstance(output, dict)


if __name__ == "__main__":
    unittest.main()
