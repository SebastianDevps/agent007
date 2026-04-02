#!/usr/bin/env python3
"""
rtk-analytics.py — Stop hook
Runs `rtk gain` and `rtk discover` at end of session if RTK is available.
Cross-platform replacement for inline bash -c commands in settings.json.
"""

import os
import platform
import shutil
import subprocess
import sys
from typing import Optional


def find_rtk() -> Optional[str]:
    rtk = shutil.which("rtk")
    if rtk:
        return rtk

    hook_dir   = os.path.dirname(os.path.abspath(__file__))
    plugin_dir = os.path.dirname(hook_dir)
    ext        = ".exe" if platform.system() == "Windows" else ""
    local      = os.path.join(plugin_dir, "bin", f"rtk{ext}")
    if os.path.isfile(local) and os.access(local, os.X_OK):
        return local

    return None


def main() -> None:
    rtk = find_rtk()
    if not rtk:
        sys.exit(0)

    for subcmd in ("gain", "discover"):
        subprocess.run([rtk, subcmd], capture_output=False, check=False)

    sys.exit(0)


if __name__ == "__main__":
    main()
