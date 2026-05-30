#!/usr/bin/env bash
# CACHE_TTL=10s
# sdd-active.sh — render active SDD change + phase as `SDD: <change>(<phase>)`.
#
# Reads .sdlc/state/session.md. Empty when no active SDD change is found.

set -u
cat >/dev/null 2>&1 || true

ROOT="${ROOT:-$PWD}"
# shellcheck source=/dev/null
. "$(dirname "$0")/../_cache.sh"

compute_sdd() {
  local f="$ROOT/.sdlc/state/session.md"
  [ -r "$f" ] || { echo ""; return; }
  python3 - "$f" <<'PY' 2>/dev/null
import re, sys
try:
    txt = open(sys.argv[1]).read()
except Exception:
    print("", end=""); raise SystemExit

# Match "Tarea Activa" / "Active Task" sections.
m = re.search(r"##\s*(?:Tarea Activa|Active Task)\s*\n(.*?)(?=\n##|\Z)", txt, re.S)
if not m:
    print("", end=""); raise SystemExit
body = m.group(1).strip()
if not body or body.lower() in {"ninguna", "none", "(ninguna)", "(none)"}:
    print("", end=""); raise SystemExit

# Try to extract change + phase. Look for sdd/<change>/<phase> first.
sdd = re.search(r"sdd/([\w\-.]+)/(\w+)", body)
if sdd:
    print(f"SDD: {sdd.group(1)}({sdd.group(2)})", end=""); raise SystemExit

# Fallback: first line, truncated.
line = body.splitlines()[0].strip().lstrip("-* ").strip()
if len(line) > 30:
    line = line[:27] + "..."
print(f"SDD: {line}", end="")
PY
}

cache_get_or_compute "sdd-active" 10 'compute_sdd'
