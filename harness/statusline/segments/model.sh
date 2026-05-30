#!/usr/bin/env bash
# model.sh — render `◆ <label> · <pct>% (<used>/<total>)` from Claude Code payload.
# Dynamic context window: parse display_name first, then fallback table by model.id.
# Used tokens: try payload fields, else derive from transcript_path usage block.
# Bash + jq (degrades to python3 if jq missing).

set -u
JSON=$(cat 2>/dev/null || echo "")
[ -z "$JSON" ] && exit 0

if command -v jq >/dev/null 2>&1; then
  MID=$(printf '%s' "$JSON" | jq -r '.model.id // ""' 2>/dev/null)
  DISP=$(printf '%s' "$JSON" | jq -r '.model.display_name // .model.name // ""' 2>/dev/null)
  USED=$(printf '%s' "$JSON" | jq -r '.model_context_tokens // .context_tokens // .transcript_tokens // 0' 2>/dev/null)
  TPATH=$(printf '%s' "$JSON" | jq -r '.transcript_path // ""' 2>/dev/null)
else
  MID=$(printf '%s' "$JSON" | python3 -c 'import json,sys;d=json.load(sys.stdin);m=d.get("model") or {};print(m.get("id","") if isinstance(m,dict) else m)' 2>/dev/null)
  DISP=$(printf '%s' "$JSON" | python3 -c 'import json,sys;d=json.load(sys.stdin);m=d.get("model") or {};print(m.get("display_name") or m.get("name") or "" if isinstance(m,dict) else "")' 2>/dev/null)
  USED=$(printf '%s' "$JSON" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(int(d.get("model_context_tokens") or d.get("context_tokens") or d.get("transcript_tokens") or 0))' 2>/dev/null)
  TPATH=$(printf '%s' "$JSON" | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d.get("transcript_path") or "")' 2>/dev/null)
fi

# Fallback: derive USED from transcript's last assistant usage block.
if [ "${USED:-0}" -eq 0 ] && [ -n "$TPATH" ] && [ -r "$TPATH" ]; then
  USED=$(python3 - "$TPATH" <<'PY' 2>/dev/null
import json, sys
path = sys.argv[1]
total = 0
try:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
except OSError:
    print(0); sys.exit(0)
for raw in reversed(lines[-400:]):
    try:
        e = json.loads(raw)
    except Exception:
        continue
    if e.get('type') != 'assistant':
        continue
    u = (e.get('message') or {}).get('usage') or {}
    if not u:
        continue
    total = int(u.get('input_tokens') or 0) + \
            int(u.get('cache_read_input_tokens') or 0) + \
            int(u.get('cache_creation_input_tokens') or 0) + \
            int(u.get('output_tokens') or 0)
    break
print(total)
PY
)
  USED=${USED:-0}
fi

NEEDLE=$(printf '%s %s' "$MID" "$DISP" | tr '[:upper:]' '[:lower:]')

# Label resolution
case "$NEEDLE" in
  *opus-4-7*|*"opus 4.7"*|*opus-4.7*) LABEL="opus 4.7" ;;
  *opus-4-6*|*"opus 4.6"*)            LABEL="opus 4.6" ;;
  *opus*)                              LABEL="opus" ;;
  *sonnet-4-6*|*"sonnet 4.6"*)        LABEL="sonnet 4.6" ;;
  *sonnet-4-5*|*"sonnet 4.5"*)        LABEL="sonnet 4.5" ;;
  *sonnet*)                            LABEL="sonnet" ;;
  *haiku-4-5*|*"haiku 4.5"*)          LABEL="haiku 4.5" ;;
  *haiku*)                             LABEL="haiku" ;;
  *)                                   LABEL=$(printf '%s' "${DISP:-${MID:-claude}}" | awk '{print $1}') ;;
esac

# Total: parse display_name regex → fallback table → empty.
TOTAL=0
LOW_DISP=$(printf '%s' "$DISP" | tr '[:upper:]' '[:lower:]')
if [[ "$LOW_DISP" =~ ([0-9]+)[[:space:]]*m([^a-z]|$) ]] || [[ "$NEEDLE" =~ \[([0-9]+)m\] ]] || [[ "$LOW_DISP" =~ \(([0-9]+)m ]]; then
  TOTAL=$(( ${BASH_REMATCH[1]} * 1000000 ))
elif [[ "$LOW_DISP" =~ ([0-9]+)[[:space:]]*k ]]; then
  TOTAL=$(( ${BASH_REMATCH[1]} * 1000 ))
elif [[ "$LOW_DISP" =~ ([0-9]{6,}) ]]; then
  TOTAL=${BASH_REMATCH[1]}
fi
if [ "$TOTAL" -eq 0 ]; then
  case "$NEEDLE" in
    *opus-4-7*\[1m\]*|*1m*) TOTAL=1000000 ;;
    *opus-4-7*|*sonnet-4-6*|*sonnet-4-5*|*haiku-4-5*) TOTAL=200000 ;;
  esac
fi

[[ "$NEEDLE" == *1m* || "$NEEDLE" == *"(1m"* ]] && [[ "$LABEL" != *"(1M)"* ]] && LABEL="$LABEL (1M)"

fmt() { local n=$1
  if [ "$n" -ge 1000000 ]; then local v=$(( n / 1000000 )); local r=$(( (n % 1000000) / 100000 ))
    if [ "$r" -eq 0 ]; then printf '%dM' "$v"; else printf '%d.%dM' "$v" "$r"; fi
  elif [ "$n" -ge 1000 ]; then printf '%dk' $(( n / 1000 ))
  else printf '%d' "$n"; fi
}

# Always render model label. Append usage only when data permits.
OUT="◆ $LABEL"
if [ "${USED:-0}" -gt 0 ]; then
  if [ "$TOTAL" -gt 0 ]; then
    PCT=$(( USED * 100 / TOTAL ))
    OUT="$OUT · ${PCT}% ($(fmt "$USED")/$(fmt "$TOTAL"))"
  else
    OUT="$OUT · $(fmt "$USED")"
  fi
fi
printf '%s' "$OUT"
