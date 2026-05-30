#!/usr/bin/env bash
# CACHE_TTL=15s
# sensor-pulse.sh — summarize reference-only audit log activity in the last hour.
#
# Reads .sdlc/state/reference-only-audit.jsonl (tail 100 lines), filters by
# ts >= now - 1h, counts status=pass and status=fail. Output: `✓12 ✗1`
# (omits the `✗N` portion if there are no failures). Empty if log missing.

set -u
cat >/dev/null 2>&1 || true

ROOT="${ROOT:-$PWD}"
# shellcheck source=/dev/null
. "$(dirname "$0")/../_cache.sh"

compute_pulse() {
  local log="$ROOT/.sdlc/state/reference-only-audit.jsonl"
  [ -r "$log" ] || { echo ""; return; }
  python3 - "$log" <<'PY' 2>/dev/null
import json, sys
from datetime import datetime, timezone, timedelta

log = sys.argv[1]
cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
passes = fails = 0
try:
    with open(log) as f:
        lines = f.readlines()[-100:]
    for ln in lines:
        try:
            ev = json.loads(ln)
        except Exception:
            continue
        ts = ev.get("ts")
        if ts:
            try:
                t = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if t < cutoff:
                    continue
            except Exception:
                pass
        status = ev.get("status", "")
        if status == "pass":
            passes += 1
        elif status == "fail":
            fails += 1
except Exception:
    pass

if passes == 0 and fails == 0:
    print("", end="")
elif fails == 0:
    print(f"✓{passes}", end="")
else:
    print(f"✓{passes} ✗{fails}", end="")
PY
}

cache_get_or_compute "sensor-pulse" 15 'compute_pulse'
