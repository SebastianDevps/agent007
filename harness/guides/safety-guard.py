#!/usr/bin/env python3
"""
PreToolUse Hook — Safety Guard for Destructive Operations
Intercepts Bash commands containing irreversible operations and blocks them
with an explanatory message and non-rm alternatives. The hook only inspects the
current tool call — there is NO chat-side override phrase.

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


# Read-only tools: a dangerous string in their args is a search PATTERN, not an
# execution. Quote-detection was the old heuristic but it failed for executors
# (psql -c 'DROP TABLE', bash -c 'rm -rf /') that RUN the quoted string. The
# correct distinction is the executing tool, not whether the token is quoted.
_READ_TOOLS = frozenset({
    "rg", "grep", "ag", "ack", "cat", "bat", "less", "more",
    "head", "tail", "echo", "printf", "fd", "find",
})

# SEQUENCING operators: `&&`, `||`, `;` — each side is an INDEPENDENT command.
# Each independent command is evaluated in isolation (existing behaviour).
# `\|\|` must precede `\|` so `||` is not consumed as two single pipes.
_SEQUENCE_SPLIT = re.compile(r"&&|\|\||;")

# PIPE operator: `|` — DATA FLOW inside one command.  The stdout of the left
# segment becomes the stdin of the right segment, so a dangerous string produced
# by a read-tool upstream can be CONSUMED by a real executor downstream.
_PIPE_SPLIT = re.compile(r"\|")


def is_read_tool_invocation(segment: str) -> bool:
    """True if the segment's first word is a known read-only tool — then a
    dangerous string in it is a pattern/arg, not an execution."""
    words = segment.split()
    return bool(words) and words[0] in _READ_TOOLS


def check_patterns(command: str) -> Optional[Tuple[str, str, str, bool]]:
    """Return (pattern, description, alternative, via_pipe) on first dangerous
    match, or None if the command is safe.

    Pipeline data-flow rule: within a single pipe-connected command, if ANY
    stage carries a dangerous token AND at least one stage is NOT a read-tool
    (i.e. a real executor that would receive the piped data), block.  An
    all-read-tool pipeline (echo 'DROP TABLE' | grep) is inert — no executor.
    """
    for independent_cmd in _SEQUENCE_SPLIT.split(command):
        if not independent_cmd.strip():
            continue

        pipeline = [s for s in _PIPE_SPLIT.split(independent_cmd) if s.strip()]

        dangerous_match: Optional[Tuple[str, str, str]] = None
        has_executor = False  # True when at least one stage is NOT a read-tool

        for segment in pipeline:
            if not is_read_tool_invocation(segment):
                has_executor = True

            if dangerous_match is None:
                for pattern, description, alternative in DANGEROUS_PATTERNS:
                    if PROFILE == "minimal" and pattern not in MINIMAL_PATTERNS:
                        continue
                    if re.search(pattern, segment, re.IGNORECASE):
                        dangerous_match = (pattern, description, alternative)
                        break

        if dangerous_match is not None and has_executor:
            pattern, description, alternative = dangerous_match
            # Determine whether the block is a pipe-bypass (dangerous token was
            # ONLY in read-tool segments; the executor segment is downstream).
            via_pipe = len(pipeline) > 1 and all(
                is_read_tool_invocation(s)
                for s in pipeline
                if re.search(dangerous_match[0], s, re.IGNORECASE)
            )
            return pattern, description, alternative, via_pipe

    return None


def build_block_message(command: str, description: str, alternative: str, via_pipe: bool = False) -> str:
    if via_pipe:
        why = (
            f"{description}\n\n"
            f"Data-flow note: the dangerous payload is produced by a read-tool (e.g. echo/printf) "
            f"and piped into a real executor — the executor would receive and act on it."
        )
    else:
        why = description
    return (
        f"[safety-guard] BLOCKED — Destructive operation detected\n\n"
        f"Command: {command}\n\n"
        f"Why blocked: {why}\n\n"
        f"Safer alternative: {alternative}\n\n"
        f"To proceed anyway: use a non-rm command (e.g. Python's shutil.rmtree, "
        f"find -delete, or trash-cli), break the operation into single-file deletions, "
        f"OR set CLAUDE_HOOK_PROFILE=minimal in your env. There is NO chat-side override "
        f"— this hook only inspects the current tool call and cannot see prior messages."
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

    _, description, alternative, via_pipe = match
    print(build_block_message(command, description, alternative, via_pipe), file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
