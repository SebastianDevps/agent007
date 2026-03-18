#!/usr/bin/env python3
"""
Tests for sdd-test-guard.py — Anti-Reward-Hacking Assertion Guard

Run: python3 -m pytest .claude/hooks/tests/test_sdd_test_guard.py -v
  or: python3 .claude/hooks/tests/test_sdd_test_guard.py
"""

import json
import os
import sys
import tempfile
import time
import unittest

# Allow importing from parent hooks directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import importlib.util

HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "sdd-test-guard.py")

def load_hook():
    spec = importlib.util.spec_from_file_location("sdd_test_guard", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestIsTestFile(unittest.TestCase):
    def setUp(self):
        self.mod = load_hook()

    def test_jest_spec_files(self):
        self.assertTrue(self.mod.is_test_file("src/users/users.service.spec.ts"))
        self.assertTrue(self.mod.is_test_file("src/auth/auth.controller.spec.tsx"))

    def test_jest_test_files(self):
        self.assertTrue(self.mod.is_test_file("src/utils/helpers.test.js"))
        self.assertTrue(self.mod.is_test_file("src/api/endpoint.test.ts"))

    def test_go_test_files(self):
        self.assertTrue(self.mod.is_test_file("pkg/service/user_test.go"))
        self.assertTrue(self.mod.is_test_file("internal/db/connection_test.go"))

    def test_python_test_files(self):
        self.assertTrue(self.mod.is_test_file("tests/test_users.py"))
        self.assertTrue(self.mod.is_test_file("src/users_test.py"))

    def test_non_test_files(self):
        self.assertFalse(self.mod.is_test_file("src/users/users.service.ts"))
        self.assertFalse(self.mod.is_test_file("main.go"))
        self.assertFalse(self.mod.is_test_file("README.md"))
        self.assertFalse(self.mod.is_test_file(""))


class TestCountAssertions(unittest.TestCase):
    def setUp(self):
        self.mod = load_hook()

    def test_jest_expect_calls(self):
        content = """
        expect(result).toBe(42);
        expect(user.name).toEqual('John');
        expect(fn).toHaveBeenCalledWith('arg');
        """
        # Patterns match both expect() and chained .toBe()/.toEqual()/.toHaveBeenCalledWith()
        count = self.mod.count_assertions(content)
        self.assertGreaterEqual(count, 3)  # At minimum 3 assertions

    def test_python_assertions(self):
        content = """
        assert result == 42
        assertEqual(a, b)
        assertTrue(condition)
        assertFalse(other)
        """
        self.assertEqual(self.mod.count_assertions(content), 4)

    def test_empty_content(self):
        self.assertEqual(self.mod.count_assertions(""), 0)

    def test_no_assertions(self):
        content = "function doSomething() { return 42; }"
        self.assertEqual(self.mod.count_assertions(content), 0)

    def test_mixed_languages(self):
        content = """
        expect(a).toBe(1);
        assert b == 2
        assertEqual(c, 3)
        """
        count = self.mod.count_assertions(content)
        self.assertGreaterEqual(count, 3)


class TestReadTestState(unittest.TestCase):
    def setUp(self):
        self.mod = load_hook()
        self.tmp = tempfile.mkdtemp()
        self.result_file = os.path.join(self.tmp, "last-test-result.json")

    def _patch_result_file(self):
        """Temporarily redirect RESULT_FILE to tmp."""
        self.mod.RESULT_FILE = self.result_file

    def test_returns_none_when_no_file(self):
        self.mod.RESULT_FILE = os.path.join(self.tmp, "nonexistent.json")
        self.assertIsNone(self.mod.read_test_state())

    def test_returns_state_when_fresh(self):
        self._patch_result_file()
        state = {"passed": False, "output": "FAIL", "timestamp": time.time()}
        with open(self.result_file, "w") as f:
            json.dump(state, f)
        result = self.mod.read_test_state()
        self.assertIsNotNone(result)
        self.assertFalse(result["passed"])

    def test_returns_none_when_expired(self):
        self._patch_result_file()
        state = {"passed": False, "output": "FAIL", "timestamp": time.time() - 700}
        with open(self.result_file, "w") as f:
            json.dump(state, f)
        self.assertIsNone(self.mod.read_test_state())

    def test_returns_none_on_corrupt_json(self):
        self._patch_result_file()
        with open(self.result_file, "w") as f:
            f.write("not json {{{")
        self.assertIsNone(self.mod.read_test_state())


class TestDecisionMatrix(unittest.TestCase):
    """
    Tests for the core decision logic:
      Tests passing + any edit          → ALLOW (exit 0)
      Tests failing + assertions same+  → ALLOW (exit 0)
      Tests failing + assertions fewer  → DENY (exit 2)
      No test state                     → ALLOW (exit 0)
    """

    def setUp(self):
        self.mod = load_hook()
        self.tmp = tempfile.mkdtemp()

    def _write_test_state(self, passed: bool):
        result_file = os.path.join(self.tmp, "last-test-result.json")
        state = {
            "passed": passed,
            "output": "Tests: 3 failed" if not passed else "Tests: 3 passed",
            "timestamp": time.time(),
        }
        with open(result_file, "w") as f:
            json.dump(state, f)
        self.mod.RESULT_FILE = result_file
        return result_file

    def test_no_test_state_allows_any_edit(self):
        self.mod.RESULT_FILE = os.path.join(self.tmp, "nonexistent.json")
        # count_assertions on '' == 0 >= 0, but no state means allow
        state = self.mod.read_test_state()
        self.assertIsNone(state)

    def test_tests_passing_allows_assertion_reduction(self):
        self._write_test_state(passed=True)
        state = self.mod.read_test_state()
        self.assertTrue(state["passed"])
        # When passing, assertion count doesn't matter — always allow

    def test_tests_failing_more_assertions_allows(self):
        self._write_test_state(passed=False)
        current = "expect(a).toBe(1);\nexpect(b).toBe(2);"
        new = "expect(a).toBe(1);\nexpect(b).toBe(2);\nexpect(c).toBe(3);"
        current_count = self.mod.count_assertions(current)
        new_count = self.mod.count_assertions(new)
        self.assertGreater(new_count, current_count)  # Assertions increased

    def test_tests_failing_fewer_assertions_is_reward_hacking(self):
        self._write_test_state(passed=False)
        current = "expect(a).toBe(1);\nexpect(b).toBe(2);\nexpect(c).toBe(3);"
        new = "expect(a).toBe(1);"  # Reduced from 3 to 1
        current_count = self.mod.count_assertions(current)
        new_count = self.mod.count_assertions(new)
        self.assertLess(new_count, current_count)  # Would trigger block


if __name__ == "__main__":
    unittest.main(verbosity=2)
