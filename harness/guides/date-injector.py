#!/usr/bin/env python3
"""
date-injector.py — UserPromptSubmit Hook: Dynamic Date Injection

Why this exists (Ola 27, P1 cache fix):
The prompt cache invalidates on ANY byte change in the cached
prefix — including a swapped date string. The legacy approach was to embed
`Today's date is YYYY-MM-DD` in a static file (e.g. CLAUDE.md or an
auto-loaded MEMORY index). That file becomes a cache-killer the moment the
date rotates at midnight, invalidating the user-global / project prefix
across EVERY call for EVERY project.

This hook moves the date into the per-turn dynamic tail via
`hookSpecificOutput.additionalContext`. The harness places UserPromptSubmit
context AFTER the cacheable system prefix, so the rotating byte never
touches the cached portion.

Output contract (per harness schema, Ola 7+8 hookSpecificOutput):
    {
      "hookSpecificOutput": {
        "hookEventName": "UserPromptSubmit",
        "additionalContext": "Today's date is YYYY-MM-DD\n..."
      }
    }

Failure mode: always exit 0. Never block the user prompt. If date resolution
fails for any reason, emit empty additionalContext and move on.
"""

import json
import sys
from datetime import datetime


def build_additional_context() -> str:
    """Compose the dynamic-tail context block.

    Currently contains today's date. Extend here if future dynamic content
    (rotating MEMORY index, user email, etc.) needs to move out of static
    files into the per-turn tail.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    return f"Today's date is {today}"


def main() -> None:
    try:
        sys.stdin.read()  # consume hook payload (not used)
    except Exception:
        pass

    try:
        additional_context = build_additional_context()
    except Exception:
        additional_context = ""

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context,
        }
    }

    try:
        print(json.dumps(output))
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
