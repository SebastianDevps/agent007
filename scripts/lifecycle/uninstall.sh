#!/usr/bin/env bash
#
# uninstall.sh — Remove this plugin from a target project's .claude/
#
# Always preserves the user's project state (.sdlc/state/) and memory
# (~/.claude/projects/<encoded>/memory/). Only the plugin code is removed.
#
# Usage:
#   uninstall.sh                          # remove from default target
#   uninstall.sh /path/to/project         # remove from /path/to/project/.claude
#   uninstall.sh --dry-run /path          # show what would be removed
set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
DEFAULT_TARGET="$(cd "$SOURCE_ROOT/.." && pwd)/Agent007"

DRY_RUN=0
TARGET=""
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --help|-h)
      sed -n '3,12p' "$0"
      exit 0
      ;;
    *) TARGET="$arg" ;;
  esac
done

[ -z "$TARGET" ] && TARGET="$DEFAULT_TARGET"
TARGET_CLAUDE="$TARGET/.claude"

echo "uninstall.sh"
echo "  target:  $TARGET_CLAUDE"
echo "  dry-run: $DRY_RUN"
echo ""

if [ ! -e "$TARGET_CLAUDE" ]; then
  echo "  ✓ Nothing to do — $TARGET_CLAUDE does not exist."
  exit 0
fi

# Identify what gets preserved vs removed
PRESERVE=()
[ -d "$TARGET_CLAUDE/state" ] && PRESERVE+=("$TARGET_CLAUDE/state")
[ -d "$TARGET/.sdlc/state" ] && PRESERVE+=("$TARGET/.sdlc/state")
[ -f "$TARGET_CLAUDE/STATE.md" ] && PRESERVE+=("$TARGET_CLAUDE/STATE.md")

echo "Plugin will be removed:"
echo "  - $TARGET_CLAUDE"
echo ""
if [ ${#PRESERVE[@]} -gt 0 ]; then
  echo "These will be PRESERVED (project state, not plugin code):"
  for p in "${PRESERVE[@]}"; do
    echo "  - $p"
  done
  echo ""
fi

if [ "$DRY_RUN" = "1" ]; then
  echo "[dry-run] No changes made."
  exit 0
fi

# Move preserved items to a temp dir, remove .claude/, restore preserved items
TMP="$(mktemp -d)"
for p in "${PRESERVE[@]}"; do
  rel="${p#$TARGET_CLAUDE/}"
  if [ "$rel" != "$p" ]; then
    mkdir -p "$TMP/$(dirname "$rel")"
    mv "$p" "$TMP/$rel"
  fi
done

# Symlink? Just unlink it.
if [ -L "$TARGET_CLAUDE" ]; then
  rm "$TARGET_CLAUDE"
else
  rm -rf "$TARGET_CLAUDE"
fi

# Restore preserved items
if [ -d "$TMP" ] && [ "$(ls -A "$TMP" 2>/dev/null)" ]; then
  mkdir -p "$TARGET_CLAUDE"
  cp -R "$TMP/." "$TARGET_CLAUDE/"
fi
rm -rf "$TMP"

echo "✓ Plugin removed from $TARGET_CLAUDE"
[ ${#PRESERVE[@]} -gt 0 ] && echo "✓ Preserved state restored"
