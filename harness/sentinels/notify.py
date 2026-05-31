#!/usr/bin/env python3
# CONTRACT EXCEPTION (v7-F1): Notification event has no canonical v7 bucket — target: SP-4
"""
notify.py — Notification hook (cross-platform)
Sends a desktop notification when Claude needs attention. The title includes the
PROJECT FOLDER that triggered it, so you know which one to look at.

  macOS   → osascript (native)
  Linux   → notify-send
  Windows → PowerShell balloon (Windows.Forms)
"""

import json
import os
import platform
import subprocess
import sys

DEFAULT_MESSAGE = "Claude necesita tu atención"


def _read_payload() -> dict:
    """The Notification hook receives JSON on stdin (cwd, message, ...)."""
    try:
        return json.loads(sys.stdin.read() or "{}")
    except Exception:
        return {}


def _project_folder(payload: dict) -> str:
    # Hooks run in the project's cwd; the payload's cwd is the canonical source.
    path = payload.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    return os.path.basename(path.rstrip("/\\")) or path


def _notify_macos(title: str, message: str) -> None:
    t = title.replace("\\", "\\\\").replace('"', '\\"')
    m = message.replace("\\", "\\\\").replace('"', '\\"')
    script = f'display notification "{m}" with title "{t}" sound name "Glass"'
    subprocess.run(["osascript", "-e", script], capture_output=True)


def _notify_linux(title: str, message: str) -> None:
    subprocess.run(
        ["notify-send", title, message, "--icon=dialog-information"],
        capture_output=True,
    )


def _notify_windows(title: str, message: str) -> None:
    t = title.replace("'", "''")
    m = message.replace("'", "''")
    ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.Visible = $true
$notify.ShowBalloonTip(5000, '{t}', '{m}', [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Milliseconds 5500
$notify.Dispose()
"""
    subprocess.run(
        ["powershell", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps_script],
        capture_output=True,
    )


def main() -> None:
    payload = _read_payload()
    title = _project_folder(payload)
    message = payload.get("message") or DEFAULT_MESSAGE
    system = platform.system()
    try:
        if system == "Darwin":
            _notify_macos(title, message)
        elif system == "Linux":
            _notify_linux(title, message)
        elif system == "Windows":
            _notify_windows(title, message)
    except Exception:
        pass  # Notifications are best-effort — never block Claude

    sys.exit(0)


if __name__ == "__main__":
    main()
