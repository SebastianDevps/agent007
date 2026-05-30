#!/usr/bin/env bash
# CACHE_TTL=10s
# harness-mode.sh — render the v7 reference-only mode (shadow / enforce).

set -u

# Discard stdin payload — this segment depends only on env state.
cat >/dev/null 2>&1 || true

ROOT="${ROOT:-$PWD}"
# shellcheck source=/dev/null
. "$(dirname "$0")/../_cache.sh"

compute_mode() {
  local mode="${HARNESS_REFERENCE_ONLY_MODE:-shadow}"
  case "$mode" in
    enforce) printf "⚔ enforce" ;;
    shadow|"") printf "🛡 shadow" ;;
    *) printf "🛡 %s" "$mode" ;;
  esac
}

cache_get_or_compute "harness-mode" 10 'compute_mode'
