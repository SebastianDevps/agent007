#!/usr/bin/env python3
"""
config-guard.py — PreToolUse hook (matcher: Edit|Write)

Blocks edits to linter/formatter configuration files.
Philosophy: fix the code, not the linter.

Protected files:
  .eslintrc*           ESLint
  .prettierrc*         Prettier
  tsconfig.json        TypeScript compiler
  tsconfig.*.json      TypeScript project references
  jest.config.*        Jest test runner
  vitest.config.*      Vitest test runner
  .ruff.toml           Ruff Python linter (standalone)
  ruff.toml            Ruff Python linter
  pyproject.toml       Python project (only matched by filename — project-wide)
  biome.json           Biome formatter/linter
  biome.jsonc          Biome formatter/linter
  .stylelintrc*        Stylelint CSS linter

NOT protected (explicitly allowed):
  package.json         npm project manifest
  .env.example         environment template
  docker-compose.yml   container orchestration
  any other config     project-specific files not in the linter list

Input  (stdin): Claude Code PreToolUse JSON
Output (stdout):
  Blocked  → {"decision": "block", "reason": "Config protection: ..."}
  Passthru → original stdin JSON unchanged

Performance: < 10ms (pure Python, no imports beyond stdlib)
Idempotent: running 2× on the same input produces the same output
Logging:   blocked file path is printed to stderr
"""

import fnmatch
import json
import os
import sys

# ---------------------------------------------------------------------------
# Protected file patterns (basename matching only)
# ---------------------------------------------------------------------------

# Exact filenames
_EXACT = frozenset({
    ".eslintrc",
    ".prettierrc",
    "tsconfig.json",
    ".ruff.toml",
    "ruff.toml",
    "pyproject.toml",
    "biome.json",
    "biome.jsonc",
    ".stylelintrc",
})

# Glob patterns matched against the basename
_GLOBS = (
    ".eslintrc.*",       # .eslintrc.js  .eslintrc.json  .eslintrc.yml  .eslintrc.cjs
    ".prettierrc.*",     # .prettierrc.js  .prettierrc.json  .prettierrc.yaml
    "tsconfig.*.json",   # tsconfig.app.json  tsconfig.base.json …
    "jest.config.*",     # jest.config.js  jest.config.ts  jest.config.json  jest.config.cjs
    "vitest.config.*",   # vitest.config.js  vitest.config.ts  vitest.config.mts
    ".stylelintrc.*",    # .stylelintrc.js  .stylelintrc.json  .stylelintrc.yaml
)


def _is_protected(file_path: str) -> bool:
    """Return True if the file basename matches any protected pattern."""
    basename = os.path.basename(file_path)

    if basename in _EXACT:
        return True

    for pattern in _GLOBS:
        if fnmatch.fnmatch(basename, pattern):
            return True

    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    raw = sys.stdin.read()

    # Parse JSON — on failure passthrough (never block on parse error)
    try:
        data = json.loads(raw) if raw.strip() else {}
    except (json.JSONDecodeError, ValueError):
        sys.stdout.write(raw)
        sys.exit(0)

    # Extract file path from tool_input
    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    file_path  = (
        tool_input.get("file_path")
        or tool_input.get("path")
        or ""
    )

    if not file_path or not _is_protected(file_path):
        # Not a protected file — passthrough stdin unchanged
        sys.stdout.write(raw)
        sys.exit(0)

    # Protected file — block and log
    basename = os.path.basename(file_path)
    sys.stderr.write(f"config-guard: blocked edit to {file_path}\n")
    sys.stderr.flush()

    block_response = {
        "decision": "block",
        "reason": (
            f"Config protection: fix the code, not the linter. "
            f"File '{basename}' is protected. "
            f"If you need to change this config, ask the user explicitly."
        ),
    }
    sys.stdout.write(json.dumps(block_response))
    sys.exit(0)


if __name__ == "__main__":
    main()
