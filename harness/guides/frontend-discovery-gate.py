#!/usr/bin/env python3
"""
frontend-discovery-gate.py — PreToolUse hook for Edit / Write on visual files

Enforces the `discovery-before-code` protocol on visual surfaces. If the agent
tries to write a `.tsx` / `.jsx` / `.css` / `.html` / `.svelte` / `.vue` /
`.astro` file without a recent discovery output on disk, BLOCK with instructions.

Why:
    Without this gate, the agent can skip the discovery step (referent fetch,
    style choice, states design, token declaration). The skill itself doesn't
    enforce — the LLM may forget. A hook does.

Behavior:
    - Reads .claude/state/discovery-output.json
    - If file is missing or older than `valid_for_minutes` (default 30) → BLOCK
    - On block, message tells the agent exactly how to clear the gate:
        Skill('discovery-before-code')
    - Files matching the visual file pattern AND located under test/fixtures
      paths are allowed (tests, mocks, generated stubs).

Allowlist (gate is skipped):
    - Files under */test/*, */tests/*, */__tests__/*, */fixtures/*, */mocks/*
    - Files matching *.test.* / *.spec.* / *.stories.*
    - Files in node_modules/ / dist/ / .next/ / build/

Bypass:
    - Set FRONTEND_DISCOVERY_BYPASS=1 in env (escape hatch for emergencies)
    - PROFILE=minimal (matches plugin convention)

Performance: < 30ms (single state file read + path check).
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal" or os.environ.get("FRONTEND_DISCOVERY_BYPASS") in {"1", "true", "yes"}:
    print(json.dumps({"continue": True}))
    sys.exit(0)


VISUAL_EXTS = {".tsx", ".jsx", ".css", ".scss", ".html", ".svelte", ".vue", ".astro"}

ALLOWLIST_FRAGMENTS = (
    "/test/", "/tests/", "/__tests__/", "/fixtures/", "/mocks/",
    "/node_modules/", "/dist/", "/.next/", "/build/", "/.cache/",
    "/.storybook/",
)

ALLOWLIST_FILENAME_PATTERNS = (
    ".test.", ".spec.", ".stories.",
)

DEFAULT_TTL_MINUTES = 30


def parse_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def project_root() -> Path:
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


def is_visual(path: Path) -> bool:
    return path.suffix.lower() in VISUAL_EXTS


def is_allowlisted(path: Path) -> bool:
    norm = "/" + str(path).replace(os.sep, "/").lstrip("/")
    if any(frag in norm for frag in ALLOWLIST_FRAGMENTS):
        return True
    name = path.name
    if any(pat in name for pat in ALLOWLIST_FILENAME_PATTERNS):
        return True
    return False


def discovery_state_path(root: Path) -> Path:
    return root / ".claude" / "state" / "discovery-output.json"


def load_discovery(root: Path):
    p = discovery_state_path(root)
    if not p.exists():
        return None, None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, None
    ts_raw = data.get("timestamp")
    if not ts_raw:
        return data, None
    try:
        ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return data, None
    return data, ts


def block(reason: str) -> None:
    print(json.dumps({
        "decision": "block",
        "reason": f"[frontend-discovery-gate] {reason}",
    }))
    sys.exit(0)


def allow() -> None:
    print(json.dumps({"continue": True}))
    sys.exit(0)


def main() -> None:
    payload = parse_payload()
    tool = payload.get("tool_name") or payload.get("toolName") or ""
    if tool not in {"Edit", "Write"}:
        allow()

    inp = (
        payload.get("tool_input")
        or payload.get("toolInput")
        or payload.get("input")
        or {}
    )
    raw_path = inp.get("file_path") or inp.get("path") or ""
    if not raw_path:
        allow()

    target = Path(raw_path)
    if not is_visual(target):
        allow()
    if is_allowlisted(target):
        allow()

    root = project_root()
    data, ts = load_discovery(root)

    if data is None:
        block(
            "Visual write blocked — no discovery output on disk.\n"
            f"Target: {raw_path}\n\n"
            "Run Skill('discovery-before-code') first. The skill writes\n"
            ".claude/state/discovery-output.json with referent + style + states + tokens.\n"
            "Without it, this gate prevents you from converging to a generic AI design.\n\n"
            "Emergency bypass: set FRONTEND_DISCOVERY_BYPASS=1 (NOT recommended)."
        )

    if ts is None:
        block(
            "Discovery output exists but its timestamp is missing or invalid.\n"
            "Re-run Skill('discovery-before-code') to refresh."
        )

    ttl_minutes = int(data.get("valid_for_minutes", DEFAULT_TTL_MINUTES))
    age_minutes = (time.time() - ts) / 60
    if age_minutes > ttl_minutes:
        block(
            f"Discovery output is stale: {age_minutes:.1f} min old (TTL: {ttl_minutes} min).\n"
            "Either re-run Skill('discovery-before-code') or update the JSON's timestamp\n"
            "if you confirm the discovery is still valid."
        )

    allow()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Fail-open: a buggy gate must not block all frontend writes
        print(json.dumps({"continue": True}))
        sys.exit(0)
