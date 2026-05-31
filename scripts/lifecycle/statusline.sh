#!/usr/bin/env bash
# Back-compat shim (added v7.0.2).
# v7 moved the status line to harness/statusline/statusline.sh. Older USER-level
# statusLine configs hardcode this old v6 path; forwarding here keeps their status
# line working after updating, without anyone editing their personal settings.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
exec bash "$DIR/harness/statusline/statusline.sh" "$@"
