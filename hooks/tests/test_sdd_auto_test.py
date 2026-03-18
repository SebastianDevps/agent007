#!/usr/bin/env python3
"""
Tests for sdd-auto-test.py — Background Test Runner

Run: python3 -m pytest .claude/hooks/tests/test_sdd_auto_test.py -v
  or: python3 .claude/hooks/tests/test_sdd_auto_test.py
"""

import importlib.util
import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "sdd-auto-test.py")


def load_hook():
    spec = importlib.util.spec_from_file_location("sdd_auto_test", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestIsSourceFile(unittest.TestCase):
    def setUp(self):
        self.mod = load_hook()

    def test_typescript_source(self):
        self.assertTrue(self.mod.is_source_file("src/users/users.service.ts"))
        self.assertTrue(self.mod.is_source_file("src/main.tsx"))

    def test_javascript_source(self):
        self.assertTrue(self.mod.is_source_file("lib/helpers.js"))
        self.assertTrue(self.mod.is_source_file("index.jsx"))

    def test_python_source(self):
        self.assertTrue(self.mod.is_source_file("app/main.py"))

    def test_go_source(self):
        self.assertTrue(self.mod.is_source_file("cmd/server/main.go"))

    def test_rust_source(self):
        self.assertTrue(self.mod.is_source_file("src/main.rs"))

    def test_exempt_claude_dir(self):
        self.assertFalse(self.mod.is_source_file(".claude/hooks/sdd-auto-test.py"))

    def test_exempt_node_modules(self):
        self.assertFalse(self.mod.is_source_file("node_modules/lodash/index.js"))

    def test_exempt_dist(self):
        self.assertFalse(self.mod.is_source_file("dist/bundle.js"))

    def test_exempt_docs(self):
        self.assertFalse(self.mod.is_source_file("docs/guide.md"))

    def test_exempt_markdown(self):
        self.assertFalse(self.mod.is_source_file("README.md"))

    def test_empty_path(self):
        self.assertFalse(self.mod.is_source_file(""))


class TestDetectTestCommand(unittest.TestCase):
    def setUp(self):
        self.mod = load_hook()
        self.tmp = tempfile.mkdtemp()

    def test_npm_test_detected(self):
        pkg = {"name": "test", "scripts": {"test": "jest"}}
        with open(os.path.join(self.tmp, "package.json"), "w") as f:
            json.dump(pkg, f)
        cmd = self.mod.detect_test_command(self.tmp)
        self.assertIsNotNone(cmd)
        self.assertIn("npm test", cmd)

    def test_pnpm_detected_by_lockfile(self):
        pkg = {"name": "test", "scripts": {"test": "jest"}}
        with open(os.path.join(self.tmp, "package.json"), "w") as f:
            json.dump(pkg, f)
        # Create pnpm lockfile
        with open(os.path.join(self.tmp, "pnpm-lock.yaml"), "w") as f:
            f.write("lockfileVersion: '6.0'")
        cmd = self.mod.detect_test_command(self.tmp)
        self.assertIn("pnpm test", cmd)

    def test_python_pytest_detected(self):
        with open(os.path.join(self.tmp, "pyproject.toml"), "w") as f:
            f.write("[tool.pytest.ini_options]")
        cmd = self.mod.detect_test_command(self.tmp)
        self.assertIsNotNone(cmd)
        self.assertIn("pytest", cmd)

    def test_go_detected(self):
        with open(os.path.join(self.tmp, "go.mod"), "w") as f:
            f.write("module example.com/project\ngo 1.21")
        cmd = self.mod.detect_test_command(self.tmp)
        self.assertIsNotNone(cmd)
        self.assertIn("go test", cmd)

    def test_rust_detected(self):
        with open(os.path.join(self.tmp, "Cargo.toml"), "w") as f:
            f.write("[package]\nname = \"test\"")
        cmd = self.mod.detect_test_command(self.tmp)
        self.assertIsNotNone(cmd)
        self.assertIn("cargo test", cmd)

    def test_no_project_returns_none(self):
        empty_dir = tempfile.mkdtemp()
        cmd = self.mod.detect_test_command(empty_dir)
        self.assertIsNone(cmd)

    def test_package_json_without_test_script(self):
        pkg = {"name": "test", "scripts": {"build": "tsc"}}
        with open(os.path.join(self.tmp, "package.json"), "w") as f:
            json.dump(pkg, f)
        cmd = self.mod.detect_test_command(self.tmp)
        self.assertIsNone(cmd)


class TestReadLastResult(unittest.TestCase):
    def setUp(self):
        self.mod = load_hook()
        self.tmp = tempfile.mkdtemp()
        self.mod.STATE_DIR = self.tmp
        self.mod.RESULT_FILE = os.path.join(self.tmp, "last-test-result.json")

    def test_returns_none_when_no_file(self):
        self.assertIsNone(self.mod.read_last_result())

    def test_returns_result_when_fresh(self):
        result = {
            "passed": False,
            "output": "FAIL: 3 tests failed",
            "returncode": 1,
            "timestamp": time.time(),
        }
        with open(self.mod.RESULT_FILE, "w") as f:
            json.dump(result, f)
        loaded = self.mod.read_last_result()
        self.assertIsNotNone(loaded)
        self.assertFalse(loaded["passed"])

    def test_returns_none_when_expired(self):
        result = {
            "passed": False,
            "timestamp": time.time() - 700,  # > TTL
        }
        with open(self.mod.RESULT_FILE, "w") as f:
            json.dump(result, f)
        self.assertIsNone(self.mod.read_last_result())

    def test_returns_none_on_corrupt_json(self):
        with open(self.mod.RESULT_FILE, "w") as f:
            f.write("{ corrupted json }")
        self.assertIsNone(self.mod.read_last_result())


if __name__ == "__main__":
    unittest.main(verbosity=2)
