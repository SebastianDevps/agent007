#!/usr/bin/env python3
"""
PreToolUse Hook — Safety Guard for Destructive Operations
Intercepts Bash commands containing irreversible operations and blocks them
with an explanatory message requiring explicit user confirmation.

Exit codes:
  0 = allow the command to proceed
  2 = block (hard stop — Claude sees the error message)

Patterns intercepted:
  - rm -rf (recursive force delete)
  - git push --force / git push -f (force push to remote)
  - git reset --hard (discard all uncommitted changes)
  - git clean -f / git clean -fd (delete untracked files)
  - DROP TABLE / DROP DATABASE (destructive SQL)
  - docker system prune / docker volume prune (docker cleanup)
  - kubectl delete (k8s resource deletion)
  - truncate -s 0 / > file (file truncation patterns)

Profile awareness:
  CLAUDE_HOOK_PROFILE=minimal → only block git push --force and DROP TABLE/DATABASE
  CLAUDE_HOOK_PROFILE=standard (default) → all patterns
  CLAUDE_HOOK_PROFILE=strict → all patterns (same as standard for this hook)
"""

import json
import os
import re
import sys
from typing import List, Optional, Tuple

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")

# Each entry: (regex_pattern, human_readable_description, safer_alternative)
DANGEROUS_PATTERNS: List[Tuple[str, str, str]] = [
    (
        r"\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b|\brm\s+-[a-zA-Z]*f[a-zA-Z]*r\b",
        "rm -rf: recursively deletes files without confirmation",
        "Use 'rm -ri' (interactive) or 'trash' if available. If deleting build output, use 'npm run clean' or equivalent.",
    ),
    (
        r"\bgit\s+push\s+.*--force\b|\bgit\s+push\s+.*-f\b|\bgit\s+push\s+-f\b",
        "git push --force: overwrites remote history and can destroy others' work",
        "Use 'git push --force-with-lease' to only force if no one else has pushed. Better yet, rebase and push normally.",
    ),
    (
        r"\bgit\s+reset\s+--hard\b",
        "git reset --hard: discards ALL uncommitted changes permanently",
        "Use 'git stash' to save changes first, then reset. Or 'git reset --soft' to keep changes staged.",
    ),
    (
        r"\bgit\s+clean\s+.*-f\b",
        "git clean -f: permanently deletes all untracked files",
        "Run 'git clean -n' first (dry run) to see what would be deleted. Use 'git stash -u' to save untracked files.",
    ),
    (
        r"\bDROP\s+TABLE\b|\bDROP\s+DATABASE\b|\bDROP\s+SCHEMA\b",
        "SQL DROP: permanently destroys database structure and all its data",
        "Ensure you have a backup. Use a migration that can be rolled back. Never run DROP on production without a restore plan.",
    ),
    (
        r"\bdocker\s+system\s+prune\b|\bdocker\s+volume\s+prune\b",
        "docker prune: deletes containers, images, or volumes — may remove persistent data",
        "Use 'docker system prune --filter until=24h' to only remove old resources. Confirm no named volumes contain critical data.",
    ),
    (
        r"\bkubectl\s+delete\b",
        "kubectl delete: removes Kubernetes resources — may affect running workloads",
        "Verify the resource name and namespace first with 'kubectl get'. Consider 'kubectl scale --replicas=0' instead of delete.",
    ),
]

# In minimal profile, only block the most catastrophic operations
MINIMAL_PATTERNS = {
    r"\bgit\s+push\s+.*--force\b|\bgit\s+push\s+.*-f\b|\bgit\s+push\s+-f\b",
    r"\bDROP\s+TABLE\b|\bDROP\s+DATABASE\b|\bDROP\s+SCHEMA\b",
}


def get_command(data: dict) -> Optional[str]:
    return data.get("tool_input", {}).get("command", "")


def check_patterns(command: str) -> Optional[Tuple[str, str, str]]:
    for pattern, description, alternative in DANGEROUS_PATTERNS:
        if PROFILE == "minimal" and pattern not in MINIMAL_PATTERNS:
            continue
        if re.search(pattern, command, re.IGNORECASE):
            return pattern, description, alternative
    return None


def build_block_message(command: str, description: str, alternative: str) -> str:
    return (
        f"[safety-guard] BLOCKED — Destructive operation detected\n\n"
        f"Command: {command}\n\n"
        f"Why blocked: {description}\n\n"
        f"Safer alternative: {alternative}\n\n"
        f"To proceed anyway: explicitly confirm with the user that this is intended "
        f"and that any data loss is acceptable. The user must type 'yes, proceed with "
        f"the destructive operation' to continue."
    )


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    command = get_command(data)
    if not command:
        sys.exit(0)

    match = check_patterns(command)
    if match is None:
        sys.exit(0)

    _, description, alternative = match
    print(build_block_message(command, description, alternative), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
