#!/usr/bin/env bash
# CACHE_TTL=2s
# plugin-context.sh — estimate plugin context overhead as a percentage of total.
#
# Heuristic: count chars in `.claude/**.{md,sh,py}` (excluding .bak / archives),
# divide by 4 to approximate tokens, then divide by the resolved model context
# window (shared with model.sh via _resolve_max_context.sh).
# Output: `plugin~5%` — empty if computation fails or returns 0.

set -u

JSON=$(cat 2>/dev/null || echo "")
ROOT="${ROOT:-$PWD}"

# shellcheck source=/dev/null
. "$(dirname "$0")/../_cache.sh"
# shellcheck source=/dev/null
. "$(dirname "$0")/../_resolve_max_context.sh"

TOTAL=$(resolve_max_context "$JSON")
[ -z "$TOTAL" ] || [ "$TOTAL" -eq 0 ] && TOTAL=200000

compute_plugin_pct() {
  local dir="$ROOT/.claude"
  [ -d "$dir" ] || { echo ""; return; }
  # fd: only .md .sh .py, excludes archive/bak by glob.
  local chars
  chars=$(fd -t f -e md -e sh -e py \
             --exclude '*.bak' \
             --exclude '_archive' \
             --exclude 'node_modules' \
             . "$dir" -X wc -c 2>/dev/null \
           | awk '{ s += $1 } END { print s+0 }')
  [ -z "$chars" ] || [ "$chars" -eq 0 ] && { echo ""; return; }
  local tokens=$(( chars / 4 ))
  local pct=$(( tokens * 100 / TOTAL ))
  [ "$pct" -le 0 ] && pct=1
  if [ "$pct" -gt 100 ]; then
    local multiplier=$(( pct / 100 ))
    printf "plugin>%d×ctx ⚠" "$multiplier"
  else
    printf "plugin~%d%%" "$pct"
  fi
}

# Cache key includes the budget so 1M vs 200k don't collide.
cache_get_or_compute "plugin-context-${TOTAL}" 2 'compute_plugin_pct'
