#!/usr/bin/env bash
# install.sh — Agent007 manual installer (git clone distribution)
# Usage: bash install.sh [target-directory]
#   target-directory defaults to current directory

set -euo pipefail

RESET='\033[0m'
BOLD='\033[1m'
GOLD='\033[38;5;220m'
DIM='\033[2m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'

# ── Banner ──────────────────────────────────────────────────────────────────────
echo ""
printf "${GOLD}${BOLD}"
cat << 'BANNER'
   _  ___ ___ _  _ _____  ___  ___  _____
  /_\/ __| __| \| |_   _|/ _ \/ _ \|__  /
 / _ \ (_ | _|| .` | | | | (_) \_, / / /
/_/ \_\___|___|_|\_| |_|  \___/ /_/ /_/
BANNER
printf "${RESET}"
printf "  ${DIM}autor: Sebastian Guerra${RESET}\n"
printf "  ${DIM}v4.1 · 41 skills · 5 agents · 16 commands${RESET}\n"
echo ""

# ── Resolve paths ───────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR/.claude"
TARGET_DIR="${1:-$(pwd)}"

if [ ! -d "$TARGET_DIR" ]; then
  printf "${RED}❌  Target directory not found: $TARGET_DIR${RESET}\n"
  exit 1
fi

if [ ! -d "$SOURCE_DIR" ]; then
  printf "${RED}❌  .claude/ not found in $SCRIPT_DIR — run this from the Agent007 repo root${RESET}\n"
  exit 1
fi

DEST="$TARGET_DIR/.claude"

# ── Idempotency check ────────────────────────────────────────────────────────────
if [ -d "$DEST" ]; then
  printf "${YELLOW}⚠️   .claude/ already exists in $TARGET_DIR${RESET}\n"
  printf "    Overwrite? Existing Agent007 config will be replaced. [y/N] "
  read -r CONFIRM
  case "$CONFIRM" in
    [yY][eE][sS]|[yY]) ;;
    *)
      printf "${DIM}Aborted — existing config preserved.${RESET}\n"
      exit 0
      ;;
  esac
fi

# ── Copy ─────────────────────────────────────────────────────────────────────────
printf "📦 Installing to ${BOLD}$TARGET_DIR/.claude/${RESET} ...\n"
cp -r "$SOURCE_DIR/" "$DEST/"

# Make hooks executable
find "$DEST/hooks" -type f \( -name "*.sh" -o -name "*.js" -o -name "*.py" \) \
  -exec chmod +x {} \; 2>/dev/null || true

echo ""
printf "${GREEN}${BOLD}✅  Agent007 installed.${RESET}\n"
echo ""
echo "  Open your project in Claude Code and run:"
printf "    ${BOLD}/dev \"your task\"${RESET}      → master command\n"
printf "    ${BOLD}/consult \"question\"${RESET}  → expert consultation\n"
printf "    ${BOLD}/ralph-loop \"task\"${RESET}   → autonomous loop\n"
echo ""
