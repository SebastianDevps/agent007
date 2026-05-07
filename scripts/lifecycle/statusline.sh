#!/usr/bin/env bash
#
# statusline.sh — Renders the Claude Code status line
#
# Reads context budget written by context-engine.py and emits a single line
# with: model · context % · session age · plugin overhead estimate.
#
# Output format (kept short — status lines have ~80 chars budget):
#
#   ◆ sonnet · 38% (76k/200k) · 24m · plugin~5%
#
# Or under pressure:
#
#   ◆ sonnet · 84% ⚠ COMPACT · 1h12m · plugin~7%
#
# Inputs (all optional — script falls back gracefully):
#   - .sdlc/state/context-budget.json     (written by context-engine on PreToolUse/Agent + Stop)
#   - .sdlc/state/context-budget.jsonl    (written by context-tick.py)
#   - $CLAUDE_MODEL                       (env)
#   - $CLAUDE_CONTEXT_TOKENS              (env, set by harness in some versions)
#
# Why bash (not Python): statusLine fires very frequently (every prompt,
# every tool call). bash + jq parse is faster than Python startup.
#
# Output: single line to stdout. NEVER multi-line. NEVER fail loudly.

set -u

# Walk up to find project root
ROOT="$PWD"
while [ "$ROOT" != "/" ]; do
  [ -d "$ROOT/.claude" ] && break
  ROOT=$(dirname "$ROOT")
done

STATE_DIR="$ROOT/.sdlc/state"
BUDGET_JSON="$STATE_DIR/context-budget.json"
JSONL="$STATE_DIR/context-budget.jsonl"

# Read stdin (Claude Code passes JSON to statusLine commands, similar to hooks).
# The schema is not officially documented but commonly includes: model, session_id,
# cwd, transcript_path. Fall back gracefully if stdin is empty.
STDIN_JSON=""
if [ ! -t 0 ]; then
  STDIN_JSON=$(cat 2>/dev/null || echo "")
fi

# Extract model from stdin → tokens.json → env, with sensible fallback
MODEL=""
if [ -n "$STDIN_JSON" ] && command -v python3 >/dev/null 2>&1; then
  MODEL=$(echo "$STDIN_JSON" | python3 -c "
import json, sys
try:
    d = json.loads(sys.stdin.read())
    # Try multiple paths Claude Code may use
    print(
        d.get('model', '') or
        d.get('model_id', '') or
        (d.get('model_info') or {}).get('id', '') or
        (d.get('session') or {}).get('model', '') or
        ''
    )
except Exception:
    print('')
" 2>/dev/null)
fi
# Fallback: tokens.json snapshot (written by context-tick.py)
if [ -z "$MODEL" ] && [ -f "$STATE_DIR/tokens.json" ] && command -v python3 >/dev/null 2>&1; then
  MODEL=$(python3 -c "
import json
try:
    print(json.load(open('$STATE_DIR/tokens.json')).get('model', ''))
except Exception:
    print('')
" 2>/dev/null)
fi
# Fallback: env (legacy)
[ -z "$MODEL" ] && MODEL="${CLAUDE_MODEL:-}"
# Last resort
[ -z "$MODEL" ] && MODEL="claude"

# Map full model id → short label
case "$MODEL" in
  *opus-4-7*|*opus-4.7*)        MODEL_LABEL="opus 4.7"   ;;
  *opus-4-6*|*opus-4.6*)        MODEL_LABEL="opus 4.6"   ;;
  *opus*)                        MODEL_LABEL="opus"       ;;
  *sonnet-4-6*|*sonnet-4.6*)    MODEL_LABEL="sonnet 4.6" ;;
  *sonnet*)                      MODEL_LABEL="sonnet"     ;;
  *haiku-4-5*|*haiku-4.5*)      MODEL_LABEL="haiku 4.5"  ;;
  *haiku*)                       MODEL_LABEL="haiku"      ;;
  claude)                        MODEL_LABEL="?"          ;;
  *)                             MODEL_LABEL="${MODEL##*-}" ;;
esac

# Debug: if we couldn't detect the model AND stdin had content, log it once so
# we can update the schema mapping later. This file is self-cleaning (overwritten).
if [ "$MODEL_LABEL" = "?" ] && [ -n "$STDIN_JSON" ]; then
  echo "$STDIN_JSON" > "$STATE_DIR/statusline-stdin-debug.json" 2>/dev/null || true
fi

# Token source priority (PRIMARY → fallback):
#   1. .sdlc/state/tokens.json — written by context-tick.py from PostToolUse payload (real value)
#   2. .sdlc/state/context-budget.json — written by context-engine.py (snapshot at Agent spawn)
#   3. env vars (legacy, NOT standard in Claude Code)
TOKENS_USED=0
TOKENS_BUDGET=200000
TOKENS_FILE="$STATE_DIR/tokens.json"

if [ -f "$TOKENS_FILE" ] && command -v python3 >/dev/null 2>&1; then
  read -r TOKENS_USED TOKENS_BUDGET < <(
    python3 - <<PY 2>/dev/null
import json
try:
    d = json.load(open("$TOKENS_FILE"))
    print(d.get("tokens_used", 0), d.get("tokens_total", 200000))
except Exception:
    print(0, 200000)
PY
  ) || { TOKENS_USED=0; TOKENS_BUDGET=200000; }
elif [ -f "$BUDGET_JSON" ] && command -v python3 >/dev/null 2>&1; then
  read -r TOKENS_USED TOKENS_BUDGET < <(
    python3 - <<PY 2>/dev/null
import json
try:
    d = json.load(open("$BUDGET_JSON"))
    print(d.get("estimated_tokens", 0), d.get("model_budget", 200000))
except Exception:
    print(0, 200000)
PY
  ) || { TOKENS_USED=0; TOKENS_BUDGET=200000; }
fi

# Optional env overrides (legacy / advanced)
if [ -n "${CLAUDE_CONTEXT_TOKENS:-}" ] && [ "$CLAUDE_CONTEXT_TOKENS" -gt 0 ] 2>/dev/null; then
  TOKENS_USED="$CLAUDE_CONTEXT_TOKENS"
fi
if [ -n "${CLAUDE_MAX_TOKENS:-}" ] && [ "$CLAUDE_MAX_TOKENS" -gt 0 ] 2>/dev/null; then
  TOKENS_BUDGET="$CLAUDE_MAX_TOKENS"
fi

# Compute %
if [ "$TOKENS_BUDGET" -gt 0 ] && [ "$TOKENS_USED" -gt 0 ]; then
  PCT=$(( TOKENS_USED * 100 / TOKENS_BUDGET ))
else
  PCT=0
fi

# Pressure indicator
PRESSURE=""
if [ "$PCT" -ge 80 ]; then
  PRESSURE=" ⚠ COMPACT"
elif [ "$PCT" -ge 60 ]; then
  PRESSURE=" ⚠"
fi

# Tokens display, K-formatted
fmt_k() {
  local n=$1
  if [ "$n" -ge 1000 ]; then
    awk -v n="$n" 'BEGIN { printf "%.0fk", n/1000 }'
  else
    echo "$n"
  fi
}
USED_K=$(fmt_k "$TOKENS_USED")
BUDGET_K=$(fmt_k "$TOKENS_BUDGET")

# Session age — approximate from earliest event in JSONL of current session
AGE=""
if [ -f "$JSONL" ] && command -v python3 >/dev/null 2>&1; then
  AGE=$(python3 - <<PY 2>/dev/null
from datetime import datetime, timezone
import json
try:
    with open("$JSONL") as f:
        # Read last 200 lines (current session likely in tail)
        lines = f.readlines()[-200:]
    sessions = {}
    for ln in lines:
        try:
            ev = json.loads(ln)
        except Exception:
            continue
        sid = ev.get("session_id", "?")
        ts = ev.get("ts")
        if not ts: continue
        try:
            t = datetime.fromisoformat(ts.replace("Z","+00:00"))
        except Exception:
            continue
        s = sessions.setdefault(sid, [t, t])
        if t < s[0]: s[0] = t
        if t > s[1]: s[1] = t
    if not sessions:
        print(""); raise SystemExit
    # Pick session with most recent last-ts
    sid = max(sessions, key=lambda k: sessions[k][1])
    start, end = sessions[sid]
    secs = int((datetime.now(timezone.utc) - start).total_seconds())
    if secs < 60:
        print(f"{secs}s")
    elif secs < 3600:
        print(f"{secs // 60}m")
    else:
        h = secs // 3600
        m = (secs % 3600) // 60
        print(f"{h}h{m:02d}m")
except Exception:
    print("")
PY
  )
fi

# Plugin overhead (rough estimate based on auto-inject + tool-loop weight)
# Assumes ~5% overhead in normal operation. Real value would need finer telemetry.
PLUGIN_PCT=5
if [ "$PCT" -ge 60 ]; then
  PLUGIN_PCT=7  # auto-inject becomes proportionally less but absolute grows
fi

# Compose output (single line, ASCII-safe diamond from box-drawing)
LINE="◆ ${MODEL_LABEL}"
if [ "$PCT" -gt 0 ]; then
  LINE+=" · ${PCT}% (${USED_K}/${BUDGET_K})${PRESSURE}"
fi
if [ -n "$AGE" ]; then
  LINE+=" · ${AGE}"
fi
LINE+=" · plugin~${PLUGIN_PCT}%"

printf "%s" "$LINE"
