#!/usr/bin/env bash
# CACHE_TTL=30s
# exceptions.sh — render active contract exception count as `EX:N`.
#
# Primary source: .claude/harness/_exceptions.json (SP-5, may not exist yet).
# Fallback: count `# CONTRACT EXCEPTION` banners across .claude/harness/**/*.py
# via rg. Returns empty if count is 0 or files are missing.

set -u
cat >/dev/null 2>&1 || true

ROOT="${ROOT:-$PWD}"
# shellcheck source=/dev/null
. "$(dirname "$0")/../_cache.sh"

compute_exceptions() {
  local file="$ROOT/.claude/harness/_exceptions.json"
  local count=0
  if [ -r "$file" ]; then
    count=$(python3 -c "
import json
try:
    d = json.load(open('$file'))
    items = d.get('exceptions') if isinstance(d, dict) else d
    print(len(items) if isinstance(items, list) else 0)
except Exception:
    print(0)
" 2>/dev/null || echo 0)
  else
    count=$(rg -c "CONTRACT EXCEPTION" "$ROOT/.claude/harness" 2>/dev/null \
            | awk -F: '{ s += $2 } END { print s+0 }')
  fi
  [ -z "$count" ] && count=0
  if [ "$count" -gt 0 ] 2>/dev/null; then
    printf "EX:%d" "$count"
  fi
}

cache_get_or_compute "exceptions" 30 'compute_exceptions'
