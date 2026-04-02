#!/usr/bin/env python3
"""
provider-rotation.py — PreToolUse(Agent) hook

Model failover with cooldown. Inspired by OpenClaw's auth-profile rotation.

When a preferred model tier is in cooldown (recent failure), recommends
the next available model in the failover chain before spawning a subagent.

Failover chain: claude-opus-4-6 → claude-sonnet-4-6 → claude-haiku-4-5-20251001

State file: .sdlc/state/provider-state.json
  {
    "models": {
      "claude-opus-4-6":         { "failures": 0, "cooldown_until": null },
      "claude-sonnet-4-6":       { "failures": 0, "cooldown_until": null },
      "claude-haiku-4-5-20251001": { "failures": 0, "cooldown_until": null }
    }
  }

CLI usage (from hooks or manual):
  python3 provider-rotation.py --mark-failure claude-opus-4-6
  python3 provider-rotation.py --mark-success claude-sonnet-4-6
  python3 provider-rotation.py --status

Hook behavior (PreToolUse/Agent):
  - Reads current model from CLAUDE_MODEL env var
  - Checks if model is in cooldown
  - If in cooldown: outputs recommended alternative model
  - Always exit 0 (non-blocking — recommendation only)

Cooldown schedule (exponential):
  failure 1: 5 minutes
  failure 2: 15 minutes
  failure 3+: 60 minutes

Exit codes:
  0 = allow (with optional recommendation)
"""

import json
import math
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)

FAILOVER_CHAIN = [
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
]

COOLDOWN_MINUTES = {1: 5, 2: 15}
COOLDOWN_DEFAULT = 60  # minutes for 3+ failures


def find_project_root():
    current = Path(os.getcwd())
    while current != current.parent:
        if (current / ".claude").is_dir():
            return current
        current = current.parent
    return Path(os.getcwd())


def load_state(state_path):
    try:
        if state_path.exists():
            return json.loads(state_path.read_text())
    except Exception:
        pass
    return {"models": {m: {"failures": 0, "cooldown_until": None} for m in FAILOVER_CHAIN}}


def save_state(state_path, state):
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, indent=2))
    except Exception:
        pass


def is_in_cooldown(model_state):
    if not model_state.get("cooldown_until"):
        return False
    cooldown_until = datetime.fromisoformat(model_state["cooldown_until"])
    return datetime.now(timezone.utc) < cooldown_until


def cooldown_duration_minutes(failure_count):
    return COOLDOWN_MINUTES.get(failure_count, COOLDOWN_DEFAULT)


def get_recommended_model(state, preferred_model):
    """
    Return (recommended_model, reason) where recommended may differ from preferred
    if preferred is in cooldown.
    """
    models = state.get("models", {})
    start_idx = FAILOVER_CHAIN.index(preferred_model) if preferred_model in FAILOVER_CHAIN else 0

    for model in FAILOVER_CHAIN[start_idx:]:
        model_state = models.get(model, {"failures": 0, "cooldown_until": None})
        if not is_in_cooldown(model_state):
            if model == preferred_model:
                return model, None  # No change needed
            else:
                return model, f"{preferred_model} is in cooldown — using {model} instead"

    # All models in cooldown — use haiku anyway (best effort)
    return FAILOVER_CHAIN[-1], "All models in cooldown — using haiku (best effort)"


def handle_cli():
    args = sys.argv[1:]
    project_root = find_project_root()
    state_path = project_root / ".sdlc" / "state" / "provider-state.json"
    state = load_state(state_path)

    if "--mark-failure" in args:
        idx = args.index("--mark-failure")
        model = args[idx + 1] if idx + 1 < len(args) else ""
        if model not in FAILOVER_CHAIN:
            print(f"Unknown model: {model}. Valid: {FAILOVER_CHAIN}")
            sys.exit(1)
        models = state.setdefault("models", {})
        model_state = models.setdefault(model, {"failures": 0, "cooldown_until": None})
        model_state["failures"] = model_state.get("failures", 0) + 1
        failures = model_state["failures"]
        duration = cooldown_duration_minutes(failures)
        cooldown_until = datetime.now(timezone.utc) + timedelta(minutes=duration)
        model_state["cooldown_until"] = cooldown_until.isoformat()
        save_state(state_path, state)
        print(f"Marked {model} as failed ({failures}x). Cooldown: {duration} minutes.")
        sys.exit(0)

    if "--mark-success" in args:
        idx = args.index("--mark-success")
        model = args[idx + 1] if idx + 1 < len(args) else ""
        if model not in FAILOVER_CHAIN:
            print(f"Unknown model: {model}. Valid: {FAILOVER_CHAIN}")
            sys.exit(1)
        models = state.setdefault("models", {})
        models[model] = {"failures": 0, "cooldown_until": None}
        save_state(state_path, state)
        print(f"Cleared cooldown for {model}.")
        sys.exit(0)

    if "--status" in args:
        models = state.get("models", {})
        now = datetime.now(timezone.utc)
        print("Provider State:")
        for model in FAILOVER_CHAIN:
            ms = models.get(model, {"failures": 0, "cooldown_until": None})
            in_cooldown = is_in_cooldown(ms)
            status = "COOLDOWN" if in_cooldown else "OK"
            failures = ms.get("failures", 0)
            cooldown_str = ""
            if in_cooldown and ms.get("cooldown_until"):
                until = datetime.fromisoformat(ms["cooldown_until"])
                remaining = int((until - now).total_seconds() / 60)
                cooldown_str = f" ({remaining}m remaining)"
            print(f"  {model}: {status} (failures={failures}){cooldown_str}")
        sys.exit(0)


def handle_hook():
    """PreToolUse/Agent hook mode."""
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({"continue": True}))
        sys.exit(0)

    tool_name = data.get("tool_name") or data.get("toolName") or ""
    if tool_name != "Agent":
        print(json.dumps({"continue": True}))
        sys.exit(0)

    project_root = find_project_root()
    state_path = project_root / ".sdlc" / "state" / "provider-state.json"
    state = load_state(state_path)

    current_model = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
    recommended, reason = get_recommended_model(state, current_model)

    if reason:
        print(
            f"[provider-rotation] ⚠️  {reason}\n"
            f"  Preferred: {current_model}\n"
            f"  Recommended: {recommended}\n"
            f"  Update the agent's model field or set CLAUDE_MODEL={recommended}"
        )

    print(json.dumps({"continue": True}))


def main():
    # CLI mode: direct invocation with flags
    if len(sys.argv) > 1 and sys.argv[1].startswith("--"):
        handle_cli()
    else:
        handle_hook()


if __name__ == "__main__":
    main()
