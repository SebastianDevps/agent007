#!/usr/bin/env bash
# rtk-rewrite.sh — PreToolUse hook (matcher: Bash)
#
# Rewrites eligible shell commands to run under RTK when available.
# Example: "git status" → "rtk git status"
#
# Rules:
#   REWRITE  if: RTK installed AND command starts with an approved binary
#   SKIP     if: RTK not installed (silent passthrough)
#   SKIP     if: command already starts with "rtk"
#   SKIP     if: command contains pipes (|) or redirects (>, <)
#   SKIP     if: command ends with / invokes a script (.sh, .py, .js)
#   SKIP     if: command contains deploy / publish / release
#
# Input  (stdin): Claude Code PreToolUse JSON
# Output (stdout): {"continue":true} — passthrough
#                  {"tool_input":{"command":"rtk ..."}} — rewritten
#
# Performance: < 10ms (no node, no python, pure bash + optional jq)
# Idempotent: running 2× on same input produces same output

set -euo pipefail

# ── Passthrough helper ────────────────────────────────────────────────────────
passthrough() { printf '{"continue":true}'; exit 0; }

# ── Read stdin (full, one shot) ───────────────────────────────────────────────
INPUT=$(cat)

# ── RTK availability check ───────────────────────────────────────────────────
# Use 'command -v' rather than 'which' — faster, no subprocess on most shells
if ! command -v rtk >/dev/null 2>&1; then
  passthrough
fi

# ── Extract command from JSON ─────────────────────────────────────────────────
if command -v jq >/dev/null 2>&1; then
  CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)
else
  # sed/grep fallback — handles simple single-line "command" fields
  # Matches: "command": "..." or "command" : "..."
  CMD=$(printf '%s' "$INPUT" \
    | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' \
    | head -1 \
    | sed 's/.*"command"[[:space:]]*:[[:space:]]*"\(.*\)"/\1/')
fi

# No command found — passthrough
[ -z "$CMD" ] && passthrough

# ── Guard: already prefixed ───────────────────────────────────────────────────
case "$CMD" in
  rtk\ *) passthrough ;;
esac

# ── Guard: pipes or redirects (shell complexity — skip) ──────────────────────
case "$CMD" in
  *\|*|*\>*|*\<*) passthrough ;;
esac

# ── Guard: script invocation (.sh / .py / .js) ───────────────────────────────
case "$CMD" in
  *.sh*|*.py*|*.js*) passthrough ;;
esac

# ── Guard: deploy / publish / release context ────────────────────────────────
case "$CMD" in
  *deploy*|*publish*|*release*) passthrough ;;
esac

# ── Guard: only rewrite approved leading binaries ────────────────────────────
LEAD="${CMD%% *}"   # everything before first space (or the whole string)

case "$LEAD" in
  git|npm|pnpm|cargo|pytest|vitest|docker|kubectl|bun|npx|\
  eslint|tsc|jest|playwright|go|rspec|curl) ;;
  *) passthrough ;;
esac

# ── Ultra-compact mode for high-noise commands ────────────────────────────────
# These commands produce extremely verbose output — use -u for icon-compressed output
case "$CMD" in
  "git log"*|"docker ps"*|"docker logs"*|"kubectl"*|"npm list"*|"pnpm list"*)
    NEW_CMD="rtk -u $CMD" ;;
  *)
    NEW_CMD="rtk $CMD" ;;
esac

if command -v jq >/dev/null 2>&1; then
  printf '%s' "$INPUT" \
    | jq --arg cmd "$NEW_CMD" '{"tool_input": (.tool_input + {"command": $cmd})}'
else
  # Fallback: manually build the output JSON.
  # Escape backslashes and double-quotes in the new command.
  SAFE_CMD=$(printf '%s' "$NEW_CMD" | sed 's/\\/\\\\/g; s/"/\\"/g')
  printf '{"tool_input":{"command":"%s"}}' "$SAFE_CMD"
fi
