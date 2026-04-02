#!/usr/bin/env python3
"""
constraint-reinforcement.py — UserPromptSubmit hook
Re-injects core CLAUDE.md constraints when conversation depth exceeds threshold.

Why: LLMs drift from their instructions in long conversations. At ~50 turns the
model may forget enforcement rules (banned phrases, verification gates, SDD Iron Law).
This hook passively re-injects the critical constraints so they remain active.

Exit codes:
  0 — always (non-blocking; this hook only injects context, never blocks)
"""

import json
import sys
import os

TURN_THRESHOLD = 50


def count_turns_from_transcript(transcript_path: str) -> int:
    """Count user turns by reading the session transcript file."""
    if not transcript_path or not os.path.exists(transcript_path):
        return 0
    count = 0
    try:
        with open(transcript_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    msg = entry.get("message", {})
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        count += 1
                except Exception:
                    pass
    except Exception:
        pass
    return count

CONSTRAINTS = """
## Agent007 — Active Constraints (auto-reinforced)

### Banned Phrases — self-correct immediately
| Banned | Required instead |
|--------|-----------------|
| "should work" | "verified working — evidence: [cmd] → [output]" |
| "probably" / "likely" | "confirmed by testing" |
| "typically" / "usually" | "documented in [file/docs]" |
| "might" | "tested and confirmed" |
| "I assume" / "it seems" | "I verified by reading [file]" |

### Verification Gates (always active)
- Cannot claim "done" without invoking verification-before-completion skill
- Cannot claim "fixed" without reproducing the bug first
- Cannot assume user approval — get explicit "yes" / "proceed"
- Must read a file before editing it
- Must verify file locations with Glob/Grep before assuming paths

### SDD Iron Law
NO PRODUCTION CODE WITHOUT A DEFINED SCENARIO FIRST.
When building features: define observable scenarios → implement → verify convergence.
Never modify scenarios to pass code.

### Risk Escalation
auth / payment / encryption / migration / breaking-change → require explicit user confirmation
""".strip()


def main():
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        data = json.loads(raw)
    except Exception:
        # Any failure (encoding, JSON parse, IO) — exit silently, never block
        sys.exit(0)

    # Count turns from transcript file (UserPromptSubmit input has transcript_path, not messages)
    transcript_path = data.get("transcript_path", "")
    turn_count = count_turns_from_transcript(transcript_path)

    if turn_count < TURN_THRESHOLD:
        sys.exit(0)

    # UserPromptSubmit uses top-level additionalContext (not hookSpecificOutput)
    output = {
        "additionalContext": (
            f"[CONSTRAINT REINFORCEMENT — turn {turn_count}]\n\n"
            + CONSTRAINTS
        ),
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
