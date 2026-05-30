#!/usr/bin/env python3
"""
transcript-policy.py — SubagentStart hook

Sanitizes context injected into subagents based on their target model tier.
Inspired by OpenClaw's provider-aware transcript sanitization.

Problem: When a subagent uses haiku (fast/cheap), complex thinking instructions
and heavy skill content waste tokens and confuse the model. Opus can handle
full context; haiku needs focused, simplified prompts.

Policy per model tier:
  haiku:  Strip extended thinking instructions, simplify skill injections,
          add "be concise" directive, cap skill content injection
  sonnet: Standard — no changes (default behavior)
  opus:   Add extended thinking guidance, allow full context

Output format: JSON with optional systemPromptAddition
  { "systemPromptAddition": "..." }  ← injected into subagent's system prompt
  {}                                 ← no modification

This hook does NOT block — it only adds/removes context.
It runs alongside subagent-context.py (which does skill injection).

Performance budget: < 30ms
"""

import json
import os
import sys

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print("{}")
    sys.exit(0)

# Model tier detection
HAIKU_MODELS = {"claude-haiku-4-5-20251001", "claude-haiku"}
OPUS_MODELS = {"claude-opus-4-6", "claude-opus"}
SONNET_MODELS = {"claude-sonnet-4-6", "claude-sonnet"}

HAIKU_DIRECTIVE = """
## Context Policy: Haiku Mode
You are running as a focused, efficient subagent. Apply these constraints:
- Be concise in reasoning — skip extended self-reflection
- Focus on the single task defined below — do not expand scope
- Prefer direct action over analysis: read the relevant files, make the change, verify
- Output only what is necessary — avoid verbose explanations
- If uncertain about a detail: make a reasonable assumption and note it briefly
""".strip()

OPUS_DIRECTIVE = """
## Context Policy: Opus Mode
You have full reasoning capacity available. Apply it where it matters:
- Use extended analysis for architecture decisions and root-cause investigation
- Consider cross-file implications before making changes
- Validate assumptions explicitly before acting on them
- Document non-obvious decisions in your output for the orchestrator
""".strip()


def detect_model_tier(data):
    """
    Detect target model from SubagentStart payload.
    Falls back to CLAUDE_MODEL env var, then to 'sonnet' default.
    """
    # Try payload fields
    model = (
        data.get("model") or
        data.get("subagentModel") or
        data.get("agent_model") or
        os.environ.get("CLAUDE_MODEL", "")
    ).lower()

    for haiku in HAIKU_MODELS:
        if haiku in model:
            return "haiku"
    for opus in OPUS_MODELS:
        if opus in model:
            return "opus"
    return "sonnet"  # default


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        print("{}")
        sys.exit(0)

    tier = detect_model_tier(data)

    if tier == "haiku":
        print(json.dumps({"systemPromptAddition": HAIKU_DIRECTIVE}))
    elif tier == "opus":
        print(json.dumps({"systemPromptAddition": OPUS_DIRECTIVE}))
    else:
        # sonnet — no modification
        print("{}")


if __name__ == "__main__":
    main()
