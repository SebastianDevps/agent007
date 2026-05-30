#!/usr/bin/env bash
# statusline.sh — v7 segment-based statusline entry point.
#
# Reads Claude Code's statusline JSON payload from stdin, walks the
# segments-config.toml order, and runs each enabled segment with the payload
# piped to its stdin. Segment outputs are concatenated with " · " — empty or
# failing segments are silently skipped so the line never breaks.
#
# Contract (per segment script in segments/):
#   - reads JSON payload on stdin
#   - prints a single short string or nothing
#   - exits 0 always
#   - completes within timeouts.default_ms

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEGMENTS_DIR="$SCRIPT_DIR/segments"
CONFIG="$SCRIPT_DIR/segments-config.toml"

# Read stdin once — replay to each segment via process substitution.
STDIN_JSON=""
if [ ! -t 0 ]; then
  STDIN_JSON=$(cat 2>/dev/null || echo "")
fi
export STDIN_JSON

# Parse config: order = [...] (one item per line, quoted). default_ms.
ORDER=()
TIMEOUT_MS=200
if [ -r "$CONFIG" ]; then
  in_order=0
  while IFS= read -r line; do
    case "$line" in
      "order = ["*|"order=["*) in_order=1; continue ;;
      "]"*) in_order=0; continue ;;
      "default_ms"*"="*)
        val="${line#*=}"
        val="${val// /}"
        [ -n "$val" ] && TIMEOUT_MS="$val"
        ;;
    esac
    if [ "$in_order" = "1" ]; then
      name=$(printf '%s' "$line" | sd '^[^"]*"' '' | sd '".*$' '')
      [ -n "$name" ] && ORDER+=("$name")
    fi
  done < "$CONFIG"
fi

# Fallback order if config missing.
if [ "${#ORDER[@]}" -eq 0 ]; then
  ORDER=(model plugin-context harness-mode exceptions sensor-pulse sdd-active)
fi

# Convert ms → seconds (use `timeout` from coreutils if present, else gtimeout).
TIMEOUT_SEC=$(awk -v ms="$TIMEOUT_MS" 'BEGIN { printf "%.2f", ms/1000 }')
TIMEOUT_BIN=""
if command -v timeout >/dev/null 2>&1; then
  TIMEOUT_BIN="timeout"
elif command -v gtimeout >/dev/null 2>&1; then
  TIMEOUT_BIN="gtimeout"
fi

run_segment() {
  local name="$1"
  local script="$SEGMENTS_DIR/${name}.sh"
  [ -x "$script" ] || [ -r "$script" ] || return 0
  local out=""
  if [ -n "$TIMEOUT_BIN" ]; then
    out=$(printf '%s' "$STDIN_JSON" | "$TIMEOUT_BIN" "$TIMEOUT_SEC" bash "$script" 2>/dev/null || true)
  else
    out=$(printf '%s' "$STDIN_JSON" | bash "$script" 2>/dev/null || true)
  fi
  printf '%s' "$out"
}

PARTS=()
for seg in "${ORDER[@]}"; do
  rendered=$(run_segment "$seg")
  if [ -n "$rendered" ]; then
    PARTS+=("$rendered")
  fi
done

SEP=" · "
LINE=""
for i in "${!PARTS[@]}"; do
  if [ "$i" -eq 0 ]; then
    LINE="${PARTS[$i]}"
  else
    LINE="${LINE}${SEP}${PARTS[$i]}"
  fi
done

printf '%s' "$LINE"
