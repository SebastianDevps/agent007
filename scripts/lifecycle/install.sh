#!/usr/bin/env bash
#
# install.sh — Deploy this plugin into a target project's .claude/
#
# This repo is itself the plugin source. install.sh copies (or symlinks) the
# plugin into another project. The default target is the user's other repo
# (Agent007 / public distribution); override with the first positional arg.
#
# Behaviors:
#   - --link  → symlink target/.claude → this repo's .claude (faster iteration)
#   - --copy  → rsync target/.claude (default — safer for tagged releases)
#   - Refuses to write if target/.claude exists and is not empty (use --force).
#   - Always runs verify.sh BEFORE writing anything.
#
# Usage:
#   install.sh                          # copy → ../Agent007/.claude (default)
#   install.sh /path/to/project          # copy → /path/to/project/.claude
#   install.sh --link ~/work/myproj     # symlink mode
#   install.sh --force /path/to/project # overwrite existing .claude
set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SOURCE_CLAUDE="$SOURCE_ROOT/.claude"
DEFAULT_TARGET="$(cd "$SOURCE_ROOT/.." && pwd)/Agent007"

MODE="copy"
FORCE=0
TARGET=""
for arg in "$@"; do
  case "$arg" in
    --link)  MODE="link" ;;
    --copy)  MODE="copy" ;;
    --force) FORCE=1 ;;
    --help|-h)
      sed -n '3,21p' "$0"
      exit 0
      ;;
    *) TARGET="$arg" ;;
  esac
done

[ -z "$TARGET" ] && TARGET="$DEFAULT_TARGET"
TARGET_CLAUDE="$TARGET/.claude"

echo "install.sh"
echo "  source:  $SOURCE_CLAUDE"
echo "  target:  $TARGET_CLAUDE"
echo "  mode:    $MODE"
echo ""

# Pre-flight verify the source is healthy
echo "[1/3] Running verify.sh on source…"
if ! "$SOURCE_ROOT/.claude/scripts/lifecycle/verify.sh" --quiet; then
  echo "  ✗ verify.sh failed — refusing to install a broken plugin" >&2
  exit 1
fi
echo "  ✓ source plugin valid"
echo ""

# Refuse to clobber existing non-empty .claude unless --force
if [ -d "$TARGET_CLAUDE" ] && [ "$(ls -A "$TARGET_CLAUDE" 2>/dev/null)" ] && [ "$FORCE" != "1" ]; then
  echo "  ✗ Target $TARGET_CLAUDE exists and is not empty." >&2
  echo "    Re-run with --force to overwrite, or remove it manually." >&2
  exit 2
fi

mkdir -p "$TARGET"

echo "[2/3] Deploying plugin ($MODE mode)…"
case "$MODE" in
  link)
    rm -rf "$TARGET_CLAUDE"
    ln -s "$SOURCE_CLAUDE" "$TARGET_CLAUDE"
    echo "  ✓ symlinked"
    ;;
  copy)
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --delete \
        --exclude='state/' \
        --exclude='metrics/' \
        --exclude='_archive/' \
        --exclude='*.log' \
        "$SOURCE_CLAUDE/" "$TARGET_CLAUDE/"
    else
      rm -rf "$TARGET_CLAUDE"
      cp -R "$SOURCE_CLAUDE" "$TARGET_CLAUDE"
    fi
    echo "  ✓ copied"
    ;;
esac
echo ""

echo "[3/3] Verifying deployed copy…"
if ! "$TARGET_CLAUDE/scripts/lifecycle/verify.sh" --quiet; then
  echo "  ✗ deployed copy failed verify — manual cleanup required" >&2
  exit 3
fi
echo "  ✓ deployed copy passes verification"
echo ""
echo "Done. Plugin installed at $TARGET_CLAUDE"
