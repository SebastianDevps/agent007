#!/usr/bin/env python3
"""
notify.py — Notification hook (cross-platform)
Sends a desktop notification when Claude needs attention.

  macOS   → osascript (native)
  Linux   → notify-send
  Windows → PowerShell toast via BurntToast or fallback balloon
"""

import platform
import subprocess
import sys

TITLE   = "Agent007"
MESSAGE = "Claude necesita tu atención"


def _notify_macos() -> None:
    script = (
        f'display notification "{MESSAGE}" '
        f'with title "{TITLE}" '
        f'sound name "Glass"'
    )
    subprocess.run(["osascript", "-e", script], capture_output=True)


def _notify_linux() -> None:
    subprocess.run(
        ["notify-send", TITLE, MESSAGE, "--icon=dialog-information"],
        capture_output=True,
    )


def _notify_windows() -> None:
    # PowerShell toast using Windows.UI.Notifications (works Win 10+)
    ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.Visible = $true
$notify.ShowBalloonTip(5000, '{TITLE}', '{MESSAGE}', [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Milliseconds 5500
$notify.Dispose()
"""
    subprocess.run(
        ["powershell", "-NonInteractive", "-WindowStyle", "Hidden", "-Command", ps_script],
        capture_output=True,
    )


def main() -> None:
    system = platform.system()
    try:
        if system == "Darwin":
            _notify_macos()
        elif system == "Linux":
            _notify_linux()
        elif system == "Windows":
            _notify_windows()
    except Exception:
        pass  # Notifications are best-effort — never block Claude

    sys.exit(0)


if __name__ == "__main__":
    main()
