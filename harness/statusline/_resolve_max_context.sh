#!/usr/bin/env bash
# _resolve_max_context.sh — shared helper to derive the max context window
# from a Claude Code statusline JSON payload. Mirrors the logic in
# segments/model.sh so segments report consistent denominators.
#
# Usage:
#   source _resolve_max_context.sh
#   TOTAL=$(resolve_max_context "$JSON")   # echoes integer (0 = unknown)

resolve_max_context() {
  local json="$1"
  local mid disp needle low_disp total=0

  if command -v jq >/dev/null 2>&1; then
    mid=$(printf '%s' "$json"  | jq -r '.model.id // ""' 2>/dev/null)
    disp=$(printf '%s' "$json" | jq -r '.model.display_name // .model.name // ""' 2>/dev/null)
  else
    mid=$(printf '%s' "$json"  | python3 -c 'import json,sys;d=json.load(sys.stdin);m=d.get("model") or {};print(m.get("id","") if isinstance(m,dict) else "")' 2>/dev/null)
    disp=$(printf '%s' "$json" | python3 -c 'import json,sys;d=json.load(sys.stdin);m=d.get("model") or {};print(m.get("display_name") or m.get("name") or "" if isinstance(m,dict) else "")' 2>/dev/null)
  fi

  needle=$(printf '%s %s' "$mid" "$disp" | tr '[:upper:]' '[:lower:]')
  low_disp=$(printf '%s' "$disp" | tr '[:upper:]' '[:lower:]')

  if [[ "$low_disp" =~ ([0-9]+)[[:space:]]*m([^a-z]|$) ]] || [[ "$needle" =~ \[([0-9]+)m\] ]] || [[ "$low_disp" =~ \(([0-9]+)m ]]; then
    total=$(( ${BASH_REMATCH[1]} * 1000000 ))
  elif [[ "$low_disp" =~ ([0-9]+)[[:space:]]*k ]]; then
    total=$(( ${BASH_REMATCH[1]} * 1000 ))
  elif [[ "$low_disp" =~ ([0-9]{6,}) ]]; then
    total=${BASH_REMATCH[1]}
  fi
  if [ "$total" -eq 0 ]; then
    case "$needle" in
      *opus-4-7*\[1m\]*|*1m*) total=1000000 ;;
      *opus-4-7*|*sonnet-4-6*|*sonnet-4-5*|*haiku-4-5*) total=200000 ;;
    esac
  fi
  printf '%d' "$total"
}
