#!/usr/bin/env python3
"""
Agent007 — orchestrator-gate hook (UserPromptSubmit)

Passes all messages through to Claude (suppress: false).

Architecture decision (2026-04-02):
  Routing decisions belong in the skill/command layer (post-LLM), not in hooks.
  Hooks are for deterministic enforcement and observability only.
  The TypeScript orchestrator (.claude/orchestrator/) is available as an explicit
  tool that Claude can invoke via Bash when needed — not as a hidden interceptor.

  Reference: industry standard from Anthropic, OpenAI Agents SDK, LangGraph —
  all use post-LLM routing. Pre-LLM message suppression creates opaque failures
  and eliminates Claude's audit trail.
"""

import json
import sys


def main() -> None:
    try:
        sys.stdin.read()  # consume stdin — required by hook protocol
    except Exception:
        pass
    print(json.dumps({"suppress": False}))


if __name__ == "__main__":
    main()
