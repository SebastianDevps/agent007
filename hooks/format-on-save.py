#!/usr/bin/env python3
"""
PostToolUse Hook — Format on Save (cross-platform replacement for format-on-save.sh)
Runs Prettier on edited files when the project has a Prettier config.

Behavior is functionally identical to format-on-save.sh:
  - Same file extensions
  - Same Prettier config detection (including package.json key)
  - Same silent exit-0 contract (never blocks Claude)
  - Cross-platform: macOS / Linux / Windows (no bash dependency)
"""

import json
import os
import shutil
import subprocess
import sys

PRETTIER_EXTENSIONS = {
    "ts", "tsx", "js", "jsx", "mjs", "cjs",
    "json", "css", "scss", "sass", "html", "md",
}

PRETTIER_CONFIGS = [
    ".prettierrc",
    ".prettierrc.json",
    ".prettierrc.yml",
    ".prettierrc.yaml",
    ".prettierrc.js",
    ".prettierrc.cjs",
    "prettier.config.js",
    "prettier.config.ts",
    "prettier.config.cjs",
    "prettier.config.mjs",
]


def has_prettier_config(cwd: str) -> bool:
    for config in PRETTIER_CONFIGS:
        if os.path.exists(os.path.join(cwd, config)):
            return True
    pkg = os.path.join(cwd, "package.json")
    if os.path.exists(pkg):
        try:
            with open(pkg) as f:
                if "prettier" in json.load(f):
                    return True
        except (json.JSONDecodeError, OSError):
            pass
    return False


def main():
    try:
        data      = json.loads(sys.stdin.read())
        file_path = data.get("tool_input", {}).get("file_path", "")
    except (json.JSONDecodeError, ValueError, KeyError):
        sys.exit(0)

    if not file_path or not os.path.isfile(file_path):
        sys.exit(0)

    ext = os.path.splitext(file_path)[1].lstrip(".")
    if ext not in PRETTIER_EXTENSIONS:
        sys.exit(0)

    if not has_prettier_config(os.getcwd()):
        sys.exit(0)

    # Resolve npx cross-platform (npx on Unix, npx.cmd on Windows)
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        sys.exit(0)

    try:
        subprocess.run(
            [npx, "prettier", "--write", "--log-level=warn", file_path],
            capture_output=True,
            timeout=30,
        )
    except (subprocess.TimeoutExpired, OSError):
        pass  # silent — never block Claude

    sys.exit(0)


if __name__ == "__main__":
    main()
