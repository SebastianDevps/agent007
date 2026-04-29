#!/usr/bin/env python3
"""
context-engine.py — PreToolUse(Agent) + Stop hook

Inspired by OpenClaw's ContextEngine interface (ingest/assemble/compact).
Proactively manages context before subagent spawns instead of reacting after overflow.

PreToolUse(Agent):
  assemble() → estimate tokens of current context
  if > 80% budget → log compact recommendation before spawn
  prepareSubagentSpawn() → write minimal context plan to context-budget.json
  dispose on Stop if spawn never completed

Stop:
  dispose() → clean up partial context-budget.json if spawn failed

State file: .sdlc/state/context-budget.json
  {
    "status": "idle" | "spawn_pending" | "spawn_complete",
    "estimated_tokens": N,
    "model_budget": N,
    "percent_used": N,
    "spawn_id": "...",
    "timestamp": "..."
  }

Model context windows:
  claude-opus-4-6:        200000
  claude-sonnet-4-6:      200000
  claude-haiku-4-5-20251001: 200000

Token estimation: chars / 4 (rough but reliable without tiktoken)

Exit codes:
  0 = allow (with optional stdout message)
  0 = always (Stop handler never blocks)

Performance budget: < 40ms
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)

MODEL_WINDOWS = {
    "claude-opus-4-6": 200_000,
    "claude-sonnet-4-6": 200_000,
    "claude-haiku-4-5-20251001": 200_000,
}
DEFAULT_WINDOW = 200_000
BLOCK_THRESHOLD = 0.80     # ≥80% → block spawn (hard gate)
WARN_THRESHOLD  = 0.60     # 60-79% → advisory only
CHARS_PER_TOKEN = 4        # rough estimate


def find_project_root():
    current = Path(os.getcwd())
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    return Path(os.getcwd())


def estimate_tokens_from_env():
    """Try to read token count from environment or context-tick state file."""
    current_tokens = int(os.environ.get("CLAUDE_CONTEXT_TOKENS", "0"))
    if current_tokens > 0:
        return current_tokens

    # Fallback: read from context-tick state if available
    try:
        project_root = find_project_root()
        tick_path = project_root / ".claude" / "state" / "context-tick.json"
        if tick_path.exists():
            state = json.loads(tick_path.read_text())
            return state.get("tokens_used", 0)
    except Exception:
        pass
    return 0


def get_model_budget():
    model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
    max_tokens = int(os.environ.get("CLAUDE_MAX_TOKENS", "0"))
    if max_tokens > 0:
        return max_tokens
    return MODEL_WINDOWS.get(model, DEFAULT_WINDOW)


def load_budget_state(state_path):
    try:
        if state_path.exists():
            return json.loads(state_path.read_text())
    except Exception:
        pass
    return {"status": "idle"}


def save_budget_state(state_path, state):
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def handle_pre_tool_use(data, project_root):
    """assemble() + prepareSubagentSpawn()"""
    state_path = project_root / ".sdlc" / "state" / "context-budget.json"

    estimated_tokens = estimate_tokens_from_env()
    model_budget = get_model_budget()
    percent = (estimated_tokens / model_budget * 100) if model_budget > 0 else 0

    spawn_id = f"spawn-{int(time.time())}"
    timestamp = datetime.now(timezone.utc).isoformat()

    budget_state = {
        "status": "spawn_pending",
        "estimated_tokens": estimated_tokens,
        "model_budget": model_budget,
        "percent_used": round(percent, 1),
        "spawn_id": spawn_id,
        "timestamp": timestamp,
    }
    save_budget_state(state_path, budget_state)

    if estimated_tokens > 0 and percent >= BLOCK_THRESHOLD * 100:
        # Hard block — context too high for a safe spawn
        response = {
            "decision": "block",
            "reason": (
                f"[context-engine] 🔴 SPAWN BLOCKED — Context at {percent:.0f}% "
                f"({estimated_tokens:,}/{model_budget:,} tokens).\n"
                f"Run /compact before spawning a subagent to prevent context rot.\n"
                f"Spawn ID: {spawn_id}"
            ),
        }
    elif estimated_tokens > 0 and percent >= WARN_THRESHOLD * 100:
        # Advisory — warn but allow
        response = {
            "continue": True,
            "hookSpecificOutput": {
                "additionalContext": (
                    f"[context-engine] ⚠️ Context at {percent:.0f}% before Agent spawn "
                    f"({estimated_tokens:,}/{model_budget:,} tokens). "
                    f"Consider /compact soon. Spawn ID: {spawn_id}"
                )
            },
        }
    else:
        response = {"continue": True}

    print(json.dumps(response))


def handle_stop(project_root):
    """dispose() — clean up pending spawn state if stop fires before completion."""
    state_path = project_root / ".sdlc" / "state" / "context-budget.json"
    budget_state = load_budget_state(state_path)

    if budget_state.get("status") == "spawn_pending":
        # Stop fired before spawn completed — mark as disposed
        budget_state["status"] = "idle"
        budget_state["disposed_at"] = datetime.now(timezone.utc).isoformat()
        budget_state["note"] = "Session ended with pending spawn — context budget cleared"
        save_budget_state(state_path, budget_state)

    print("{}")


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({"continue": True}))
        sys.exit(0)

    project_root = find_project_root()

    # Distinguish between PreToolUse and Stop invocations
    # PreToolUse payload has "tool_name"; Stop payload typically doesn't
    tool_name = data.get("tool_name") or data.get("toolName") or ""

    if tool_name == "Agent":
        handle_pre_tool_use(data, project_root)
    else:
        # Invoked from Stop hook
        handle_stop(project_root)


if __name__ == "__main__":
    main()
