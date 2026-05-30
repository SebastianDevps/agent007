# _platform.sh — sourced by bash scripts in .claude/harness/
# Cross-platform path + tool helpers for Mac / Linux / WSL / Git-Bash.
# Usage: source .claude/harness/_platform.sh

# Detect OS (mac | linux | wsl | windows-bash | unknown)
detect_os() {
  case "$(uname -s 2>/dev/null)" in
    Darwin*) echo "mac" ;;
    Linux*)
      if grep -qi microsoft /proc/version 2>/dev/null; then
        echo "wsl"
      else
        echo "linux"
      fi
      ;;
    MINGW*|MSYS*|CYGWIN*) echo "windows-bash" ;;
    *) echo "unknown" ;;
  esac
}

# Home dir — bash always has $HOME (even on Git-Bash via USERPROFILE mapping)
claude_home() {
  echo "$HOME/.claude"
}

claude_projects_dir() {
  echo "$HOME/.claude/projects"
}

# Temp dir — first existing of $TMPDIR, $TEMP, /tmp
claude_temp_dir() {
  for d in "$TMPDIR" "$TEMP" "/tmp"; do
    [ -n "$d" ] && [ -d "$d" ] && echo "$d" && return 0
  done
  echo "/tmp"
}

# Tool availability check
has_tool() {
  command -v "$1" >/dev/null 2>&1
}

# Resolve python interpreter — python3 preferred, python fallback
claude_python() {
  if has_tool python3; then echo "python3"
  elif has_tool python; then echo "python"
  else echo ""
  fi
}

# Walk up from $1 (or $PWD) until finding .claude/harness
find_hook_root() {
  local start="${1:-$PWD}"
  local p="$start"
  while [ "$p" != "/" ] && [ -n "$p" ]; do
    if [ -d "$p/.claude/harness" ]; then
      echo "$p"
      return 0
    fi
    p="$(dirname "$p")"
  done
  return 1
}

# Safe jq — falls back to a Python json.tool pretty-print when jq absent
safe_jq() {
  if has_tool jq; then
    jq "$@"
  else
    local py
    py="$(claude_python)"
    [ -z "$py" ] && return 1
    "$py" -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))"
  fi
}
