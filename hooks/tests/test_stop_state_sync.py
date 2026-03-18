#!/usr/bin/env python3
"""
Tests for stop-state-sync.py — Stop Hook

Run: python3 -m pytest .claude/hooks/tests/test_stop_state_sync.py -v
"""

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch


HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "stop-state-sync.py")


def load_hook():
    spec = importlib.util.spec_from_file_location("stop_state_sync", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestLoadSessionState(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()
        self.tmpdir = tempfile.mkdtemp()

    def test_returns_none_when_file_missing(self):
        """load_session_state returns None when file does not exist."""
        with patch.object(self.mod, "SESSION_STATE_FILE", "/nonexistent/path/.session-state.json"):
            result = self.mod.load_session_state()
        self.assertIsNone(result)

    def test_returns_dict_when_valid_json(self):
        """load_session_state returns parsed dict for valid JSON."""
        state = {"previousSkill": "brainstorming", "taskHistory": [], "activeContext": {}}
        f = os.path.join(self.tmpdir, ".session-state.json")
        with open(f, "w") as fh:
            json.dump(state, fh)

        with patch.object(self.mod, "SESSION_STATE_FILE", f):
            result = self.mod.load_session_state()

        self.assertIsNotNone(result)
        self.assertEqual(result["previousSkill"], "brainstorming")

    def test_returns_none_on_invalid_json(self):
        """load_session_state returns None when file contains invalid JSON."""
        f = os.path.join(self.tmpdir, ".session-state.json")
        with open(f, "w") as fh:
            fh.write("not-valid-json")

        with patch.object(self.mod, "SESSION_STATE_FILE", f):
            result = self.mod.load_session_state()

        self.assertIsNone(result)


class TestIsRalphActive(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()

    def test_returns_false_for_none_state(self):
        self.assertFalse(self.mod.is_ralph_active(None))

    def test_returns_false_for_empty_state(self):
        self.assertFalse(self.mod.is_ralph_active({}))

    def test_detects_ralph_in_previous_skill(self):
        state = {"previousSkill": "ralph-loop", "taskHistory": []}
        self.assertTrue(self.mod.is_ralph_active(state))

    def test_detects_ralph_in_recent_task_history(self):
        state = {
            "previousSkill": "sop-discovery",
            "taskHistory": [
                {"skill": "brainstorming"},
                {"skill": "ralph-loop-wrapper"},
            ]
        }
        self.assertTrue(self.mod.is_ralph_active(state))

    def test_returns_false_when_no_ralph_references(self):
        state = {
            "previousSkill": "sop-discovery",
            "taskHistory": [{"skill": "brainstorming"}, {"skill": "writing-plans"}]
        }
        self.assertFalse(self.mod.is_ralph_active(state))


class TestBuildSummaryBullets(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()

    def test_includes_previous_skill_bullet(self):
        state = {"previousSkill": "sop-discovery", "taskHistory": [], "activeContext": {}}
        bullets = self.mod.build_summary_bullets(state)
        self.assertTrue(any("sop-discovery" in b for b in bullets))

    def test_includes_recent_skills_bullet(self):
        state = {
            "previousSkill": None,
            "taskHistory": [
                {"skill": "brainstorming"},
                {"skill": "writing-plans"},
                {"skill": "sop-code-assist"},
            ],
            "activeContext": {}
        }
        bullets = self.mod.build_summary_bullets(state)
        self.assertTrue(any("brainstorming" in b or "writing-plans" in b for b in bullets))

    def test_fallback_bullet_when_no_data(self):
        state = {"previousSkill": None, "taskHistory": [], "activeContext": {}}
        bullets = self.mod.build_summary_bullets(state)
        self.assertGreater(len(bullets), 0)
        self.assertTrue(any("finalizada" in b or "sin actividad" in b for b in bullets))


class TestUpdateStateMd(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()
        self.tmpdir = tempfile.mkdtemp()

    def test_replaces_existing_section(self):
        """update_state_md replaces content under 'Resumen de Última Sesión'."""
        state_md = (
            "# Agent007 Session State\n\n"
            "## Posición Actual\n- Branch: main\n\n"
            "## Resumen de Última Sesión\n"
            "- Old bullet 1\n"
            "- Old bullet 2\n"
        )
        f = os.path.join(self.tmpdir, "STATE.md")
        with open(f, "w") as fh:
            fh.write(state_md)

        with patch.object(self.mod, "STATE_MD_FILE", f):
            self.mod.update_state_md(["New bullet A", "New bullet B"])

        with open(f) as fh:
            result = fh.read()

        self.assertIn("New bullet A", result)
        self.assertIn("New bullet B", result)
        self.assertNotIn("Old bullet 1", result)

    def test_appends_section_when_missing(self):
        """update_state_md appends section when it doesn't exist in file."""
        state_md = "# Agent007 Session State\n\n## Posición Actual\n- Branch: main\n"
        f = os.path.join(self.tmpdir, "STATE.md")
        with open(f, "w") as fh:
            fh.write(state_md)

        with patch.object(self.mod, "STATE_MD_FILE", f):
            self.mod.update_state_md(["New bullet"])

        with open(f) as fh:
            result = fh.read()

        self.assertIn("Resumen de Última Sesión", result)
        self.assertIn("New bullet", result)

    def test_does_nothing_when_file_missing(self):
        """update_state_md silently does nothing when STATE.md is missing."""
        with patch.object(self.mod, "STATE_MD_FILE", "/nonexistent/STATE.md"):
            try:
                self.mod.update_state_md(["bullet"])
            except Exception:
                self.fail("update_state_md raised an exception for missing file")


class TestMainOutput(unittest.TestCase):

    def setUp(self):
        self.mod = load_hook()

    def test_main_always_prints_empty_json(self):
        """main() always outputs {} regardless of state."""
        with patch.object(self.mod, "SESSION_STATE_FILE", "/nonexistent/.session-state.json"):
            with patch.object(self.mod, "STATE_MD_FILE", "/nonexistent/STATE.md"):
                with patch("sys.stdout", new_callable=StringIO) as mock_out:
                    self.mod.main()
                    output = mock_out.getvalue().strip()

        self.assertEqual(output, "{}")

    def test_main_skips_state_md_when_ralph_active(self):
        """main() does not modify STATE.md when ralph is active."""
        state = {"previousSkill": "ralph-loop", "taskHistory": [], "activeContext": {}}

        with tempfile.TemporaryDirectory() as tmpdir:
            session_file = os.path.join(tmpdir, ".session-state.json")
            state_md_file = os.path.join(tmpdir, "STATE.md")
            with open(session_file, "w") as f:
                json.dump(state, f)
            original_content = "## Resumen de Última Sesión\n- original bullet\n"
            with open(state_md_file, "w") as f:
                f.write(original_content)

            with patch.object(self.mod, "SESSION_STATE_FILE", session_file):
                with patch.object(self.mod, "STATE_MD_FILE", state_md_file):
                    with patch("sys.stdout", new_callable=StringIO):
                        self.mod.main()

            with open(state_md_file) as f:
                result = f.read()

        self.assertIn("original bullet", result)

    def test_main_does_not_raise_on_any_error(self):
        """main() never raises exceptions — always exits cleanly."""
        with patch.object(self.mod, "load_session_state", side_effect=RuntimeError("boom")):
            try:
                with patch("sys.stdout", new_callable=StringIO):
                    self.mod.main()
            except Exception:
                self.fail("main() raised an exception")


if __name__ == "__main__":
    unittest.main()
