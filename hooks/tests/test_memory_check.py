#!/usr/bin/env python3
"""
Tests for memory-check.py — Manifest Staleness Detector

Run: python3 -m pytest .claude/hooks/tests/test_memory_check.py -v
  or: python3 .claude/hooks/tests/test_memory_check.py
"""

import hashlib
import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import importlib.util

HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "memory-check.py")

def load_hook():
    spec = importlib.util.spec_from_file_location("memory_check", HOOK_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestMd5File(unittest.TestCase):
    def setUp(self):
        self.mod = load_hook()
        self.tmp = tempfile.mkdtemp()

    def test_md5_of_known_content(self):
        f = os.path.join(self.tmp, "test.txt")
        with open(f, "w") as fh:
            fh.write("hello")
        expected = hashlib.md5(b"hello").hexdigest()
        self.assertEqual(self.mod.md5_file(f), expected)

    def test_md5_of_nonexistent_file_returns_empty(self):
        result = self.mod.md5_file("/nonexistent/file.txt")
        self.assertEqual(result, "")

    def test_different_content_different_hash(self):
        f1 = os.path.join(self.tmp, "a.txt")
        f2 = os.path.join(self.tmp, "b.txt")
        with open(f1, "w") as fh:
            fh.write("hello")
        with open(f2, "w") as fh:
            fh.write("world")
        self.assertNotEqual(self.mod.md5_file(f1), self.mod.md5_file(f2))

    def test_same_content_same_hash(self):
        f1 = os.path.join(self.tmp, "a.txt")
        f2 = os.path.join(self.tmp, "b.txt")
        content = "same content"
        for f in [f1, f2]:
            with open(f, "w") as fh:
                fh.write(content)
        self.assertEqual(self.mod.md5_file(f1), self.mod.md5_file(f2))


class TestPhase1Stat(unittest.TestCase):
    def setUp(self):
        self.mod = load_hook()
        self.tmp = tempfile.mkdtemp()

    def test_detects_existing_manifests(self):
        # Create package.json
        pkg = os.path.join(self.tmp, "package.json")
        with open(pkg, "w") as f:
            f.write('{"name": "test"}')

        result = self.mod.phase1_stat(self.tmp)
        self.assertIn("package.json", result)
        self.assertIsInstance(result["package.json"], float)

    def test_ignores_missing_manifests(self):
        result = self.mod.phase1_stat(self.tmp)
        self.assertNotIn("package.json", result)
        self.assertNotIn("go.mod", result)

    def test_detects_multiple_manifests(self):
        for name in ["package.json", "tsconfig.json", "docker-compose.yml"]:
            path = os.path.join(self.tmp, name)
            with open(path, "w") as f:
                f.write("{}")

        result = self.mod.phase1_stat(self.tmp)
        self.assertIn("package.json", result)
        self.assertIn("tsconfig.json", result)
        self.assertIn("docker-compose.yml", result)


class TestStateStorage(unittest.TestCase):
    def setUp(self):
        self.mod = load_hook()
        self.tmp = tempfile.mkdtemp()
        self.mod.STATE_DIR = self.tmp
        self.mod.MANIFEST_STATE_FILE = os.path.join(self.tmp, "manifest-hashes.json")

    def test_load_state_returns_empty_when_no_file(self):
        result = self.mod.load_state()
        self.assertEqual(result, {})

    def test_save_and_load_roundtrip(self):
        state = {"mtimes": {"package.json": 1234.5}, "hashes": {"package.json": "abc"}}
        self.mod.save_state(state)
        loaded = self.mod.load_state()
        self.assertEqual(loaded["mtimes"]["package.json"], 1234.5)
        self.assertEqual(loaded["hashes"]["package.json"], "abc")

    def test_load_state_returns_empty_on_corrupt_json(self):
        with open(self.mod.MANIFEST_STATE_FILE, "w") as f:
            f.write("not valid json {{{")
        result = self.mod.load_state()
        self.assertEqual(result, {})


class TestChangeDetection(unittest.TestCase):
    """
    Integration tests for the two-phase change detection logic.
    Phase 1: mtime comparison → candidates
    Phase 2: MD5 comparison → actually changed
    """

    def setUp(self):
        self.mod = load_hook()
        self.tmp = tempfile.mkdtemp()
        self.mod.STATE_DIR = self.tmp
        self.mod.MANIFEST_STATE_FILE = os.path.join(self.tmp, "manifest-hashes.json")

    def test_first_run_detects_all_manifests_as_changed(self):
        pkg = os.path.join(self.tmp, "package.json")
        with open(pkg, "w") as f:
            f.write('{"name": "test"}')

        # No saved state → everything is "new" → actually changed
        saved_state = self.mod.load_state()
        current_mtimes = self.mod.phase1_stat(self.tmp)

        saved_mtimes = saved_state.get("mtimes", {})
        changed = [m for m, t in current_mtimes.items() if saved_mtimes.get(m, 0) != t]
        self.assertIn("package.json", changed)

    def test_unchanged_file_not_reported(self):
        pkg = os.path.join(self.tmp, "package.json")
        content = '{"name": "test"}'
        with open(pkg, "w") as f:
            f.write(content)

        # Save initial state
        hash_val = self.mod.md5_file(pkg)
        stat = os.stat(pkg)
        self.mod.save_state({
            "mtimes": {"package.json": stat.st_mtime},
            "hashes": {"package.json": hash_val},
            "last_check": time.time()
        })

        # File not modified — mtime unchanged → no candidates
        saved_state = self.mod.load_state()
        current_mtimes = self.mod.phase1_stat(self.tmp)
        saved_mtimes = saved_state.get("mtimes", {})
        changed = [m for m, t in current_mtimes.items() if saved_mtimes.get(m, 0) != t]
        self.assertNotIn("package.json", changed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
