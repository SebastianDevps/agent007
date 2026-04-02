#!/usr/bin/env bash
# monitor-session.sh — Monitor de sesión autónoma en tiempo real
#
# Muestra el progreso de una sesión /dev corriendo en paralelo.
# Lee PROGRESS.md del proyecto objetivo + ralph-state.json del plugin.
#
# Usage:
#   bash .claude/scripts/monitor-session.sh ~/Projects/airpods-landing
#   bash .claude/scripts/monitor-session.sh ~/Projects/airpods-landing --interval 30

TARGET_DIR="${1:-$HOME/Projects/airpods-landing}"
INTERVAL="${2:-30}"
[[ "$2" == "--interval" ]] && INTERVAL="${3:-30}"

PROGRESS_FILE="$TARGET_DIR/PROGRESS.md"
RALPH_STATE="$HOME/Projects/PluginClaude/.claude/ralph-state.json"
RALPH_COMPLETE="$HOME/Projects/PluginClaude/.claude/ralph-complete.txt"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; GRAY='\033[0;90m'; NC='\033[0m'

clear_screen() { printf '\033[2J\033[H'; }

render() {
  clear_screen
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BOLD}  Agent007 — Session Monitor${NC}"
  echo -e "${GRAY}  $(date '+%Y-%m-%d %H:%M:%S') | target: $TARGET_DIR${NC}"
  echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo ""

  # ── Ralph Loop Status ──────────────────────────────────────────────────────
  echo -e "${BOLD}Ralph Loop${NC}"
  if [[ -f "$RALPH_COMPLETE" ]]; then
    echo -e "  ${GREEN}✅ COMPLETE${NC}"
  elif [[ -f "$RALPH_STATE" ]]; then
    local active iter max_iter task status
    active=$(python3 -c "import json; d=json.load(open('$RALPH_STATE')); print(d.get('active', False))" 2>/dev/null || echo "false")
    iter=$(python3 -c "import json; d=json.load(open('$RALPH_STATE')); print(d.get('currentIteration', 0))" 2>/dev/null || echo "0")
    max_iter=$(python3 -c "import json; d=json.load(open('$RALPH_STATE')); print(d.get('maxIterations', 20))" 2>/dev/null || echo "20")
    task=$(python3 -c "import json; d=json.load(open('$RALPH_STATE')); print(d.get('task', 'unknown')[:60])" 2>/dev/null || echo "unknown")

    if [[ "$active" == "True" ]]; then
      local pct=$(( iter * 100 / max_iter ))
      local filled=$(( iter * 20 / max_iter ))
      local bar=""
      for ((i=0; i<filled; i++)); do bar+="█"; done
      for ((i=filled; i<20; i++)); do bar+="░"; done
      echo -e "  ${YELLOW}🔄 RUNNING${NC}  [${bar}] iter ${iter}/${max_iter} (${pct}%)"
      echo -e "  ${GRAY}Task: $task${NC}"
    else
      echo -e "  ${GRAY}Inactive${NC}"
    fi
  else
    echo -e "  ${GRAY}Not started yet — waiting for session to begin${NC}"
  fi

  echo ""

  # ── Project Status ─────────────────────────────────────────────────────────
  echo -e "${BOLD}Project: $(basename $TARGET_DIR)${NC}"
  if [[ ! -d "$TARGET_DIR" ]]; then
    echo -e "  ${GRAY}Directory not created yet${NC}"
  else
    # Package.json exists?
    if [[ -f "$TARGET_DIR/package.json" ]]; then
      local name version
      name=$(python3 -c "import json; d=json.load(open('$TARGET_DIR/package.json')); print(d.get('name','?'))" 2>/dev/null || echo "?")
      echo -e "  ${GREEN}✅ package.json${NC}  ($name)"
    else
      echo -e "  ${YELLOW}⏳ Initializing...${NC}"
    fi

    # Count source files
    local src_count=0
    [[ -d "$TARGET_DIR/src" ]] && src_count=$(find "$TARGET_DIR/src" -name "*.tsx" -o -name "*.ts" 2>/dev/null | wc -l | tr -d ' ')
    [[ $src_count -gt 0 ]] && echo -e "  ${GREEN}✅ Source files: $src_count .tsx/.ts${NC}" || echo -e "  ${GRAY}   Source files: none yet${NC}"

    # GSAP usage
    local gsap_count=0
    [[ -d "$TARGET_DIR/src" ]] && gsap_count=$(grep -rl "gsap" "$TARGET_DIR/src" 2>/dev/null | wc -l | tr -d ' ')
    [[ $gsap_count -gt 0 ]] && echo -e "  ${GREEN}✅ GSAP in $gsap_count files${NC}" || echo -e "  ${GRAY}   GSAP: not yet${NC}"

    # Build status (check .next directory)
    [[ -d "$TARGET_DIR/.next" ]] && echo -e "  ${GREEN}✅ Build output (.next exists)${NC}" || echo -e "  ${GRAY}   Build: not run yet${NC}"
  fi

  echo ""

  # ── Progress Log ───────────────────────────────────────────────────────────
  echo -e "${BOLD}Progress Log${NC}"
  if [[ -f "$PROGRESS_FILE" ]]; then
    local lines
    lines=$(tail -15 "$PROGRESS_FILE")
    while IFS= read -r line; do
      if [[ "$line" == *"COMPLETE"* ]]; then
        echo -e "  ${GREEN}$line${NC}"
      elif [[ "$line" == *"FAIL"* ]]; then
        echo -e "  ${RED}$line${NC}"
      elif [[ "$line" == *"##"* ]]; then
        echo -e "  ${BLUE}$line${NC}"
      else
        echo -e "  ${GRAY}$line${NC}"
      fi
    done <<< "$lines"
  else
    echo -e "  ${GRAY}Waiting for first task to complete...${NC}"
  fi

  echo ""
  echo -e "${GRAY}Refreshing every ${INTERVAL}s — Ctrl+C to stop${NC}"
}

# ── Run ───────────────────────────────────────────────────────────────────────
echo -e "${BOLD}Starting monitor for: $TARGET_DIR${NC}"
echo -e "${GRAY}Ctrl+C to stop${NC}"
sleep 1

while true; do
  render
  sleep "$INTERVAL"
done
