#!/usr/bin/env python3
"""
conversation-tick.py — PostToolUse hook (matcher: *)

Adds ~1200 tokens to the context budget baseTokens after every tool call,
modelling the accumulation of conversation history in the orchestrator context.

If the budget exceeds 30% or 40%, the node script prints a warning to stdout
which this hook relays back to Claude as a hook system message.

Input  (stdin): Claude Code PostToolUse JSON (consumed but ignored)
Output (stdout): JSON hook response — silent when safe, warning message when over threshold

Performance budget: < 50ms
"""

import json
import os
import subprocess
import sys

# Profile awareness: skip in minimal mode (saves ~45ms per tool call)
if os.environ.get("CLAUDE_HOOK_PROFILE", "standard") == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)


def _find_project_root() -> str:
    current = os.getcwd()
    while current != os.path.dirname(current):
        if os.path.isdir(os.path.join(current, ".claude")):
            return current
        current = os.path.dirname(current)
    return os.getcwd()


def main() -> None:
    try:
        sys.stdin.read()  # consume input — not needed for tick
    except Exception:
        pass

    project_root = _find_project_root()

    # Context budget is tracked by context-engine.py (PreToolUse hook).
    # Read the state file it writes instead of invoking a script.
    warning_text = ""
    try:
        import json
        budget_path = os.path.join(project_root, ".sdlc", "state", "context-budget.json")
        if os.path.exists(budget_path):
            with open(budget_path) as f:
                budget = json.load(f)
            pct = budget.get("percent", 0)
            if pct >= 85:
                warning_text = f"⛔ Context at {pct}% — must /compact before continuing"
            elif pct >= 70:
                warning_text = f"⚠️  Context at {pct}% — consider /compact soon"
    except Exception:
        pass  # never block Claude on tracker failure

    if warning_text:
        # Relay warning so Claude sees it as a system-level context signal
        print(json.dumps({"continue": True, "reason": warning_text}))
    else:
        print(json.dumps({"continue": True}))

    sys.exit(0)


if __name__ == "__main__":
    main()
