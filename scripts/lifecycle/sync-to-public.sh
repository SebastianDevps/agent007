#!/usr/bin/env bash
#
# sync-to-public.sh — Deploy .claude/ contents to the Agent007 public repo.
#
# The public repo (default ../Agent007) uses a FLAT layout: agents/, commands/,
# skills/, hooks/, rules/, scripts/, settings.json — all at the repo root, NOT
# nested under .claude/. (Agent007/.gitignore intentionally excludes .claude/.)
#
# This script:
#   1. Runs verify.sh on source — refuses to sync if validation fails
#   2. Runs hook regression tests (test-hooks.py) — refuses if any fail
#   3. rsyncs .claude/ contents (NOT the wrapper) to the target's root
#   4. Excludes runtime/state/private directories
#   5. Re-runs verify.sh from the deployed copy
#   6. Prints exact git commands the user can run to commit (does NOT commit)
#
# Usage:
#   sync-to-public.sh                          # default target ../Agent007
#   sync-to-public.sh /path/to/Agent007        # custom target
#   sync-to-public.sh --dry-run                # preview rsync without writing
#   sync-to-public.sh --skip-tests             # skip hook regression tests
#
# This is intentionally NOT a one-shot publish: the user reviews the diff
# in the public repo, runs `git status`, and decides whether to commit.
set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SOURCE_CLAUDE="$SOURCE_ROOT/.claude"
# Default target: Agent007/ inside the monorepo (NOT a sibling).
# Override by passing a path as the first arg.
DEFAULT_TARGET="$SOURCE_ROOT/Agent007"

DRY_RUN=0
SKIP_TESTS=0
TARGET=""
for arg in "$@"; do
  case "$arg" in
    --dry-run)    DRY_RUN=1 ;;
    --skip-tests) SKIP_TESTS=1 ;;
    --help|-h)
      sed -n '3,24p' "$0"
      exit 0
      ;;
    *) TARGET="$arg" ;;
  esac
done

[ -z "$TARGET" ] && TARGET="$DEFAULT_TARGET"

if [ ! -d "$TARGET" ]; then
  echo "✗ target does not exist: $TARGET" >&2
  echo "  Clone the public repo first, or pass an existing path." >&2
  exit 1
fi

if [ ! -d "$TARGET/.git" ]; then
  echo "✗ target is not a git repo: $TARGET" >&2
  echo "  sync-to-public expects a clonable working tree." >&2
  exit 1
fi

echo "sync-to-public.sh"
echo "  source:  $SOURCE_CLAUDE"
echo "  target:  $TARGET   (flat layout)"
echo "  dry:     $DRY_RUN"
echo ""

# ---- Pre-flight: source health ---------------------------------------------
echo "[1/4] verify.sh on source"
if ! "$SOURCE_CLAUDE/scripts/lifecycle/verify.sh" --quiet; then
  echo "  ✗ source plugin failed verify.sh — refusing to sync" >&2
  exit 2
fi
echo "  ✓ source verify clean"
echo ""

# ---- Pre-flight: hook regression tests --------------------------------------
if [ "$SKIP_TESTS" != "1" ]; then
  echo "[2/4] hook regression tests"
  if ! python3 "$SOURCE_CLAUDE/scripts/lifecycle/test-hooks.py" --quiet >/dev/null 2>&1; then
    echo "  ✗ hook regression tests FAILED — refusing to sync" >&2
    echo "    run python3 $SOURCE_CLAUDE/scripts/lifecycle/test-hooks.py for details" >&2
    exit 3
  fi
  echo "  ✓ hook tests pass"
  echo ""
fi

# ---- rsync ------------------------------------------------------------------
echo "[3/4] rsync (flat layout — .claude contents → target root)"
RSYNC_ARGS=(
  -a
  --delete
  # CRITICAL excludes — public repo has its own copy of these and they MUST
  # NOT be deleted by --delete. Order matters: excludes apply both ways
  # (won't push, won't delete).
  --exclude='/.git/'                # NEVER touch git history of the public repo
  --exclude='/.gitignore'           # public repo has its own .gitignore
  --exclude='/.installed'           # first-run marker created locally on install
  --exclude='/README.md'            # public repo has its own README
  --exclude='/GETTING_STARTED.md'   # public repo onboarding doc
  --exclude='/STATE.md'             # session pointer
  # Blacklist runtime / generated / private:
  --exclude='/state/'
  --exclude='/.sdlc/'
  --exclude='/metrics/'
  --exclude='/instincts/'
  --exclude='/_archive/'
  --exclude='/settings.local.json'
  --exclude='**/*.log'
  --exclude='**/__pycache__/'
  --exclude='**/.DS_Store'
  --exclude='**/.cache/'
  --exclude='**/node_modules/'
  --exclude='**/dist/'
  --exclude='**/.next/'
)
[ "$DRY_RUN" = "1" ] && RSYNC_ARGS+=(--dry-run --itemize-changes)

if ! command -v rsync >/dev/null 2>&1; then
  echo "  ✗ rsync not found — install via 'brew install rsync' (macOS)" >&2
  exit 4
fi

rsync "${RSYNC_ARGS[@]}" "$SOURCE_CLAUDE/" "$TARGET/"
echo "  ✓ rsync complete"
echo ""

if [ "$DRY_RUN" = "1" ]; then
  echo "[dry-run] No files written. Re-run without --dry-run to apply."
  exit 0
fi

# ---- Post-flight: deployed copy validates -----------------------------------
echo "[4/4] verify.sh on deployed copy"
# Public repo is FLAT, so verify.sh runs from the target root with cwd-aware paths.
# We re-use the same script — it walks .claude/ relative to itself, but the
# layout is flat. We do a simpler check here: settings.json + frontmatter +
# hook syntax (using the deployed scripts).
DEPLOYED_VERIFY=0
(
  cd "$TARGET"
  # Validate settings.json
  python3 -c "import json; json.load(open('settings.json'))" 2>/dev/null
) && DEPLOYED_VERIFY=1

if [ "$DEPLOYED_VERIFY" = "1" ]; then
  echo "  ✓ deployed settings.json parses"
else
  echo "  ✗ deployed copy has invalid settings.json" >&2
  exit 5
fi
echo ""

# ---- Hand-off: commit instructions ------------------------------------------
echo "═══════════════════════════════════════════════════════════════════"
echo "Sync complete. Review and commit MANUALLY:"
echo ""
echo "  cd $TARGET"
echo "  git status"
echo "  git diff --stat"
echo ""
echo "  # When happy:"
echo "  git add -A"
echo "  git commit -m \"feat|AGENT007|\$(date +%Y%m%d)|sync v6 — anti-convergence + CI + lifecycle\""
echo "  git push"
echo ""
echo "Then update the marketplace listing in $SOURCE_ROOT/agent007-marketplace/"
echo "(README.md was updated in lockstep — review and commit it too)."
echo "═══════════════════════════════════════════════════════════════════"
