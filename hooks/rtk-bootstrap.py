#!/usr/bin/env python3
"""
rtk-bootstrap.py — SessionStart hook
Auto-installs RTK if not found in PATH or .claude/bin/.

Strategy by platform:
  macOS   → brew install rtk  |  curl install.sh fallback
  Linux   → curl install.sh   |  cargo fallback
  Windows → download pre-built binary to .claude/bin/  |  cargo fallback
  All     → silent pass if already installed
"""

import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import urllib.request
import zipfile
import tarfile
import tempfile

HOOK_DIR   = os.path.dirname(os.path.abspath(__file__))
PLUGIN_DIR = os.path.dirname(HOOK_DIR)
BIN_DIR    = os.path.join(PLUGIN_DIR, "bin")

RELEASES_BASE = "https://github.com/rtk-ai/rtk/releases/latest/download/"

PLATFORM_BINARY = {
    ("Darwin",  "arm64"):   "rtk-aarch64-apple-darwin.tar.gz",
    ("Darwin",  "x86_64"):  "rtk-x86_64-apple-darwin.tar.gz",
    ("Linux",   "aarch64"): "rtk-aarch64-unknown-linux-gnu.tar.gz",
    ("Linux",   "x86_64"):  "rtk-x86_64-unknown-linux-musl.tar.gz",
    ("Windows", "AMD64"):   "rtk-x86_64-pc-windows-msvc.zip",
}


def _emit(message: str) -> None:
    """Write a JSON output message that Claude Code will display."""
    print(json.dumps({"type": "text", "text": f"[rtk-bootstrap] {message}"}))


def _local_bin_path() -> str:
    ext = ".exe" if platform.system() == "Windows" else ""
    return os.path.join(BIN_DIR, f"rtk{ext}")


def is_installed() -> bool:
    if shutil.which("rtk"):
        return True
    local = _local_bin_path()
    return os.path.isfile(local) and os.access(local, os.X_OK)


def _run(cmd: list, check: bool = False) -> int:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode
    except FileNotFoundError:
        return 127


def _try_brew() -> bool:
    if shutil.which("brew") is None:
        return False
    _emit("Installing via Homebrew...")
    return _run(["brew", "install", "rtk"]) == 0


def _try_curl() -> bool:
    if shutil.which("curl") is None:
        return False
    _emit("Installing via curl script...")
    code = _run(
        ["sh", "-c",
         "curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh"],
    )
    return code == 0


def _try_binary_download() -> bool:
    """Download pre-built binary to .claude/bin/ (Windows primary, fallback others)."""
    system  = platform.system()
    machine = platform.machine()

    # Normalize ARM labels
    if machine in ("arm64", "ARM64"):
        machine = "aarch64"

    key = (system, machine)
    filename = PLATFORM_BINARY.get(key)
    if not filename:
        _emit(f"No pre-built binary for {system}/{machine}.")
        return False

    url = RELEASES_BASE + filename
    _emit(f"Downloading binary from GitHub releases ({filename})...")

    try:
        os.makedirs(BIN_DIR, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            archive_path = os.path.join(tmp, filename)
            urllib.request.urlretrieve(url, archive_path)

            # Extract
            if filename.endswith(".zip"):
                with zipfile.ZipFile(archive_path) as zf:
                    zf.extractall(tmp)
            else:
                with tarfile.open(archive_path) as tf:
                    tf.extractall(tmp)

            # Find the binary
            ext = ".exe" if system == "Windows" else ""
            for root, _, files in os.walk(tmp):
                for fname in files:
                    if fname in (f"rtk{ext}", "rtk"):
                        src = os.path.join(root, fname)
                        dst = _local_bin_path()
                        shutil.copy2(src, dst)
                        if system != "Windows":
                            os.chmod(dst, os.stat(dst).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
                        _emit(f"Binary installed to {dst}")
                        return True

        _emit("Binary not found inside archive.")
        return False

    except Exception as exc:
        _emit(f"Binary download failed: {exc}")
        return False


def _try_cargo() -> bool:
    if shutil.which("cargo") is None:
        return False
    _emit("Installing via cargo (this may take a few minutes)...")
    return _run(["cargo", "install", "--git", "https://github.com/rtk-ai/rtk"]) == 0


def install() -> bool:
    system = platform.system()

    if system == "Darwin":
        return _try_brew() or _try_curl() or _try_binary_download() or _try_cargo()
    elif system == "Linux":
        return _try_curl() or _try_binary_download() or _try_cargo()
    elif system == "Windows":
        return _try_binary_download() or _try_cargo()
    else:
        return _try_cargo()


def main() -> None:
    if is_installed():
        # Already installed — silent pass
        sys.exit(0)

    _emit("RTK not found. Installing for token compression...")
    success = install()

    if success:
        _emit("RTK installed. Token compression active from next command.")
    else:
        _emit("RTK install failed. Continuing without token compression. Install manually: brew install rtk")

    sys.exit(0)


if __name__ == "__main__":
    main()
