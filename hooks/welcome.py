#!/usr/bin/env python3
"""
SessionStart Hook — First-Run Banner
Shows AGENT007 banner on first session in this project, then stays silent.
Marker: .claude/.installed (created after first display).
"""

import json
import os
import sys

BANNER = r"""
   _  ___ ___ _  _ _____  ___  ___  _____
  /_\/ __| __| \| |_   _|/ _ \/ _ \|__  /
 / _ \ (_ | _|| .` | | | | (_) \_, / / /
/_/ \_\___|___|_|\_| |_|  \___/ /_/ /_/
"""

AUTHOR   = "  autor: Sebastian Guerra"
VERSION  = "  v4.1 · 41 skills · 5 agents · 16 commands"
SEP      = "  " + "─" * 44


def main():
    try:
        sys.stdin.read()  # consume Claude's event JSON from stdin
    except Exception:
        pass

    cwd    = os.getcwd()
    marker = os.path.join(cwd, ".claude", ".installed")

    if not os.path.exists(marker):
        # Print to stderr → visible in the user's terminal, not injected into Claude
        sys.stderr.write(BANNER + "\n")
        sys.stderr.write(AUTHOR  + "\n")
        sys.stderr.write(VERSION + "\n")
        sys.stderr.write(SEP     + "\n\n")
        sys.stderr.flush()

        try:
            with open(marker, "w") as f:
                f.write("installed\n")
        except OSError:
            pass  # non-critical — banner won't repeat on next session but that's fine

    # Always emit valid JSON — empty object = no additionalContext noise in Claude
    print(json.dumps({}))
    sys.exit(0)


if __name__ == "__main__":
    main()
