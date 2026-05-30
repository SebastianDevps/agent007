#!/usr/bin/env bash
#
# verify.sh — Plugin self-validation
#
# Five checks that mirror the CI pipeline. Run locally before commit, or as
# part of install.sh / uninstall.sh sanity gates. Exit non-zero on any failure.
#
#   1. settings-json-valid          → .claude/settings.json parses as JSON
#   2. skill-frontmatter-lint       → every SKILL.md / invokable .md has
#                                      `name`, `description` keys
#   3. hook-syntax-check            → every .py in .claude/harness/ compiles
#   4. line-cap-check               → SKILL.md (eager-loaded) ≤ 200 lines.
#                                      references/ are exempt (lazy)
#   5. references-resolvable        → every `references:` entry in a SKILL.md
#                                      points to a file that exists
#
# Usage:
#   .claude/scripts/lifecycle/verify.sh           # run all checks
#   .claude/scripts/lifecycle/verify.sh --quiet   # only output failures
#   .claude/scripts/lifecycle/verify.sh --check N # run only check N (1..5)

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CLAUDE_DIR="$ROOT/.claude"

QUIET=0
ONLY=""
WITH_TESTS=0
for arg in "$@"; do
  case "$arg" in
    --quiet) QUIET=1 ;;
    --with-tests) WITH_TESTS=1 ;;
    --check=*) ONLY="${arg#--check=}" ;;
    --check) shift; ONLY="${1:-}" ;;
  esac
done
export WITH_TESTS

PASS=0
FAIL=0
WARN=0

say()   { [ "$QUIET" = "1" ] || echo "$@"; }
ok()    { say "  ✓ $1"; PASS=$((PASS+1)); }
fail()  { echo "  ✗ $1" >&2;             FAIL=$((FAIL+1)); }
warn()  { say "  ! $1";                  WARN=$((WARN+1)); }

run_check() {
  local n="$1" label="$2" fn="$3"
  if [ -n "$ONLY" ] && [ "$ONLY" != "$n" ]; then return; fi
  say ""
  say "[$n/5] $label"
  "$fn"
}

# ---------------------------------------------------------------------------
# 1. settings.json valid
# ---------------------------------------------------------------------------
check_settings() {
  local f="$CLAUDE_DIR/settings.json"
  if [ ! -f "$f" ]; then
    fail "settings.json not found"
    return
  fi
  if python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/dev/null; then
    ok "settings.json parses"
  else
    fail "settings.json INVALID JSON"
  fi
}

# ---------------------------------------------------------------------------
# 2. SKILL frontmatter lint
# ---------------------------------------------------------------------------
check_frontmatter() {
  local found=0 broken=0
  while IFS= read -r f; do
    found=$((found+1))
    # Need closing --- and required keys name/description before it
    if ! awk '
      BEGIN{count=0}
      /^---[[:space:]]*$/{count++; if(count==2)exit}
      count==1 && /^name:[[:space:]]*[^[:space:]]/ {has_name=1}
      count==1 && /^description:[[:space:]]*[^[:space:]]/ {has_desc=1}
      END{exit (count>=2 && has_name && has_desc) ? 0 : 1}
    ' "$f"; then
      fail "frontmatter missing/incomplete: ${f#$ROOT/}"
      broken=$((broken+1))
    fi
  done < <(find "$CLAUDE_DIR/skills" -type f \( -name 'SKILL.md' -o -path '*/workflow-utils/*.md' -o -path '*/quality-gates/*.md' \) ! -path '*/references/*' ! -name 'INDEX.md')

  if [ $broken -eq 0 ] && [ $found -gt 0 ]; then
    ok "$found SKILL.md frontmatter checks passed"
  fi
}

# ---------------------------------------------------------------------------
# 3. Hook syntax
# ---------------------------------------------------------------------------
check_hooks() {
  local broken=0 total=0
  while IFS= read -r f; do
    total=$((total+1))
    if ! python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$f" 2>/dev/null; then
      fail "syntax error: ${f#$ROOT/}"
      broken=$((broken+1))
    fi
  done < <(find "$CLAUDE_DIR/hooks" -type f -name '*.py')

  if [ $broken -eq 0 ] && [ $total -gt 0 ]; then
    ok "$total hook .py files compile"
  fi
}

# ---------------------------------------------------------------------------
# 4. Line cap on eager-loaded SKILL.md
# ---------------------------------------------------------------------------
check_line_caps() {
  local violations=0 checked=0 exempt_warned=0 max=200
  local exempt_file="$CLAUDE_DIR/scripts/lifecycle/.line-cap-exemptions"

  is_exempt() {
    [ -f "$exempt_file" ] || return 1
    local rel="${1#$ROOT/}"
    grep -v '^[[:space:]]*#' "$exempt_file" | grep -v '^[[:space:]]*$' | \
      awk -F'\t' -v p="$rel" '$1 == p {found=1} END {exit !found}'
  }

  evaluate() {
    local f="$1"
    checked=$((checked+1))
    local n
    n=$(wc -l < "$f" | tr -d ' ')
    if [ "$n" -le "$max" ]; then return; fi
    if is_exempt "$f"; then
      warn "exceeds $max lines ($n) [EXEMPT — see .line-cap-exemptions]: ${f#$ROOT/}"
      exempt_warned=$((exempt_warned+1))
    else
      fail "exceeds $max lines ($n): ${f#$ROOT/}"
      violations=$((violations+1))
    fi
  }

  while IFS= read -r f; do
    evaluate "$f"
  done < <(find "$CLAUDE_DIR/skills" -type f \( -name 'SKILL.md' -o -path '*/workflow-utils/*.md' -o -path '*/quality-gates/*.md' -o -path '*/orchestration/*.md' -o -path '*/core/*.md' \) ! -path '*/references/*' ! -name 'INDEX.md')

  for f in "$CLAUDE_DIR/CLAUDE.md" "$CLAUDE_DIR/CONTEXT.md"; do
    [ -f "$f" ] && evaluate "$f"
  done

  if [ $violations -eq 0 ]; then
    if [ $exempt_warned -gt 0 ]; then
      ok "$checked checked, $exempt_warned exempt (debt registered)"
    else
      ok "$checked eager-loaded files within $max-line cap"
    fi
  fi
}

# ---------------------------------------------------------------------------
# 5. references: resolvable
# ---------------------------------------------------------------------------
check_refs() {
  local broken=0 checked=0
  while IFS= read -r skill; do
    local dir
    dir="$(dirname "$skill")"
    # Extract `references:` block: lines after `references:` that start with `- `
    # until a non-list line.
    local refs
    refs=$(awk '
      /^references:[[:space:]]*$/ {in_block=1; next}
      in_block==1 && /^[[:space:]]*-[[:space:]]/ {
        sub(/^[[:space:]]*-[[:space:]]*/,"")
        # Strip surrounding quotes (single or double) so YAML-quoted refs resolve
        gsub(/^["\047]|["\047][[:space:]]*$/, "")
        print
        next
      }
      in_block==1 && !/^[[:space:]]/ {in_block=0}
    ' "$skill")
    [ -z "$refs" ] && continue
    while IFS= read -r ref; do
      [ -z "$ref" ] && continue
      checked=$((checked+1))
      if [ ! -f "$dir/$ref" ]; then
        fail "broken reference in ${skill#$ROOT/}: $ref"
        broken=$((broken+1))
      fi
    done <<< "$refs"
  done < <(find "$CLAUDE_DIR/skills" -type f -name 'SKILL.md' ! -path '*/references/*')

  if [ $broken -eq 0 ] && [ $checked -gt 0 ]; then
    ok "$checked reference paths resolve"
  elif [ $checked -eq 0 ]; then
    warn "no references: blocks found (skipped)"
  fi
}

# ---------------------------------------------------------------------------

say "verify.sh — plugin self-validation"
say "Root: $ROOT"

run_check 1 "settings.json valid"           check_settings
run_check 2 "SKILL frontmatter lint"        check_frontmatter
run_check 3 "Hook syntax check"             check_hooks
run_check 4 "Line cap on eager files"       check_line_caps
run_check 5 "References resolvable"         check_refs

# ---------------------------------------------------------------------------
# 6. Hook regression tests (optional — opt-in with --with-tests or check=6)
# ---------------------------------------------------------------------------
check_hook_tests() {
  local runner="$CLAUDE_DIR/scripts/lifecycle/test-hooks.py"
  if [ ! -f "$runner" ]; then
    warn "test-hooks.py not found — skipping"
    return
  fi
  if python3 "$runner" --quiet >/dev/null 2>&1; then
    local count
    count=$(python3 "$runner" --quiet 2>&1 | tail -1 | awk '{print $3}')
    ok "${count:-?} hook regression tests pass"
  else
    fail "hook regression tests FAILED — run python3 $runner for details"
  fi
}

if [ -n "$ONLY" ] && [ "$ONLY" = "6" ]; then
  say ""
  say "[6/6] Hook regression tests"
  check_hook_tests
elif [ -z "$ONLY" ] && [ "${WITH_TESTS:-0}" = "1" ]; then
  say ""
  say "[6/6] Hook regression tests"
  check_hook_tests
fi

say ""
if [ $FAIL -gt 0 ]; then
  echo "FAIL — $FAIL error(s), $WARN warning(s), $PASS passed" >&2
  exit 1
fi

say "OK — $PASS check(s) passed, $WARN warning(s)"
exit 0
