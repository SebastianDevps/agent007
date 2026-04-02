#!/usr/bin/env python3
"""
tool-loop-detection.py — PostToolUse hook (all tools)

Detects when the same tool call is repeated without progress.
Inspired by OpenClaw's SHA-256 loop detection with 4 escalation patterns.

Patterns detected:
  Generic Repeat:   same (tool + params + outcome) × 10 → warning, × 30 → circuit breaker
  Ping-Pong:        alternating between 2 identical call patterns → detected at 6 alternations

State file: .sdlc/state/loop-state.json
  { "window": [ {hash, tool, timestamp}, ... ], "circuit_broken": false }

Exit codes:
  0 = allow (continue: true)
  0 = warning injected via stdout message
  2 = circuit breaker triggered (block with escalation message)

Performance budget: < 30ms
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)

# Tools that are always safe to repeat — skip fingerprinting
BENIGN_TOOLS = {"Read", "Glob", "Grep", "WebFetch", "WebSearch", "TaskList", "TaskGet"}

WINDOW_SIZE = 30
WARNING_THRESHOLD = 10
CIRCUIT_BREAKER_THRESHOLD = 30
PING_PONG_THRESHOLD = 6  # 3 full alternations


def find_project_root() -> Path:
    current = Path(os.getcwd())
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    return Path(os.getcwd())


def load_state(state_path: Path) -> dict:
    try:
        if state_path.exists():
            return json.loads(state_path.read_text())
    except Exception:
        pass
    return {"window": [], "circuit_broken": False}


def save_state(state_path: Path, state: dict) -> None:
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def build_fingerprint(tool_name: str, tool_input: dict, tool_response: dict) -> str:
    params_str = json.dumps(tool_input, sort_keys=True)[:500]
    # Use first 200 chars of response to capture outcome without over-matching
    outcome_str = json.dumps(tool_response, sort_keys=True)[:200] if tool_response else ""
    raw = f"{tool_name}:{params_str}:{outcome_str}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def detect_ping_pong(window: list) -> bool:
    """Detect alternation between exactly 2 different hashes."""
    if len(window) < PING_PONG_THRESHOLD:
        return False
    recent = [e["hash"] for e in window[-PING_PONG_THRESHOLD:]]
    unique = set(recent)
    if len(unique) != 2:
        return False
    # Check true alternation: A B A B A B
    return all(recent[i] != recent[i + 1] for i in range(len(recent) - 1))


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({"continue": True}))
        sys.exit(0)

    tool_name = data.get("tool_name") or data.get("toolName") or ""
    tool_input = data.get("tool_input") or data.get("toolInput") or {}
    tool_response = data.get("tool_response") or data.get("toolResponse") or {}

    if tool_name in BENIGN_TOOLS or not tool_name:
        print(json.dumps({"continue": True}))
        sys.exit(0)

    project_root = find_project_root()
    state_path = project_root / ".sdlc" / "state" / "loop-state.json"
    state = load_state(state_path)

    # Already circuit-broken this session — escalate immediately
    if state.get("circuit_broken"):
        msg = (
            "[tool-loop-detection] ⚡ CIRCUIT BREAKER ACTIVE\n"
            "A loop was detected and circuit broken this session.\n"
            "Review what's repeating and break the cycle before continuing."
        )
        print(msg, file=sys.stderr)
        sys.exit(2)

    fingerprint = build_fingerprint(tool_name, tool_input, tool_response)

    # Append to window
    window = state.get("window", [])
    window.append({"hash": fingerprint, "tool": tool_name, "ts": int(time.time())})
    if len(window) > WINDOW_SIZE:
        window = window[-WINDOW_SIZE:]
    state["window"] = window

    # Count consecutive repetitions of this fingerprint at the end of the window
    same_count = sum(1 for e in window if e["hash"] == fingerprint)

    # Ping-pong detection
    if detect_ping_pong(window):
        state["circuit_broken"] = True
        save_state(state_path, state)
        msg = (
            f"[tool-loop-detection] 🔁 PING-PONG LOOP DETECTED\n"
            f"Alternating between 2 identical call patterns {PING_PONG_THRESHOLD}× in a row.\n"
            f"Tool: {tool_name}\n"
            f"This indicates a task stuck in a cycle. Change approach before continuing."
        )
        print(msg, file=sys.stderr)
        sys.exit(2)

    # Circuit breaker
    if same_count >= CIRCUIT_BREAKER_THRESHOLD:
        state["circuit_broken"] = True
        save_state(state_path, state)
        msg = (
            f"[tool-loop-detection] ⚡ CIRCUIT BREAKER TRIGGERED\n"
            f"Tool '{tool_name}' called {same_count}× with identical params+outcome.\n"
            f"This session has been circuit-broken. Diagnose the root cause:\n"
            f"  1. What is this tool trying to accomplish?\n"
            f"  2. Why is the outcome not changing?\n"
            f"  3. Try a different approach or escalate to the user."
        )
        print(msg, file=sys.stderr)
        sys.exit(2)

    save_state(state_path, state)

    # Warning (non-blocking)
    if same_count >= WARNING_THRESHOLD:
        warning = {
            "continue": True,
            "suppressOutput": False,
        }
        print(
            f"[tool-loop-detection] ⚠️  WARNING: '{tool_name}' called {same_count}× "
            f"with identical params+outcome. If this is intentional, continue. "
            f"If stuck, change approach. Circuit breaker triggers at {CIRCUIT_BREAKER_THRESHOLD}×."
        )
    else:
        print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
