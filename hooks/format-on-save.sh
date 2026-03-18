#!/bin/bash
# Hook: format-on-save
# Event: PostToolUse (Edit | Write)
# Auto-formats the edited file with Prettier if the project has Prettier configured.
# Exits silently (0) when Prettier is not applicable — never blocks Claude.

set -euo pipefail

# Parse file_path from stdin (Claude passes tool event JSON)
INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('tool_input', {}).get('file_path', ''))
except:
    print('')
" 2>/dev/null || true)

# Nothing to format
[ -z "$FILE_PATH" ] && exit 0
[ ! -f "$FILE_PATH" ] && exit 0

# Only format supported extensions
EXT="${FILE_PATH##*.}"
case "$EXT" in
  ts|tsx|js|jsx|mjs|cjs|json|css|scss|sass|html|md) ;;
  *) exit 0 ;;
esac

# Only run if the project has a Prettier config (don't impose formatting on projects without it)
PRETTIER_CONFIG=false
for config in .prettierrc .prettierrc.json .prettierrc.yml .prettierrc.yaml \
              .prettierrc.js .prettierrc.cjs prettier.config.js prettier.config.ts \
              prettier.config.cjs prettier.config.mjs; do
  [ -f "$config" ] && PRETTIER_CONFIG=true && break
done

# Also check package.json for "prettier" key
if [ "$PRETTIER_CONFIG" = false ] && [ -f "package.json" ]; then
  python3 -c "import json,sys; d=json.load(open('package.json')); sys.exit(0 if 'prettier' in d else 1)" 2>/dev/null \
    && PRETTIER_CONFIG=true || true
fi

[ "$PRETTIER_CONFIG" = false ] && exit 0

# Run Prettier — silently, non-blocking
if command -v npx >/dev/null 2>&1; then
  npx prettier --write --log-level=warn "$FILE_PATH" 2>/dev/null || true
fi

exit 0
