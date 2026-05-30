#!/usr/bin/env python3
"""
path-existence-guard.py — PreToolUse hook for Edit / Write / Read

Validates that the target path of an Edit / Read operation exists. For Write
operations, validates that the PARENT directory exists (so we don't create
files in hallucinated directories).

Why this exists:
    LLMs frequently hallucinate file paths under pressure. Editing a non-existent
    file with create_if_missing semantics silently creates rogue files; reading
    one wastes tool calls. This hook catches both before they happen.

Behavior:
    - Edit / Read on a path that does not exist → BLOCK with helpful suggestion
    - Write on a path whose parent directory does not exist → BLOCK
    - All other tools → pass-through (exit 0)

Allowed exceptions (Write only — file may not exist yet):
    - Path is under a known-creation manifest: .sdlc/state/, /tmp/, .claude/state/
    - Path matches an env-allowed prefix: PATH_EXISTENCE_ALLOWLIST (colon-separated)

Performance budget: < 50ms.

Profile gating:
    PROFILE=minimal → no-op
"""

import datetime
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Optional, Tuple

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)

CREATION_ALLOWLIST_PREFIXES = (
    ".sdlc/state/",
    ".claude/state/",
    "/tmp/",
    tempfile.gettempdir().rstrip(os.sep) + os.sep,
    "var/log/",
)


def parse_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def get_tool(payload: dict) -> str:
    return payload.get("tool_name") or payload.get("toolName") or ""


def get_input(payload: dict) -> dict:
    return (
        payload.get("tool_input")
        or payload.get("toolInput")
        or payload.get("input")
        or {}
    )


def project_root() -> Path:
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


def is_creation_allowlisted(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = path
    rel_str = str(rel).replace(os.sep, "/")
    if any(rel_str.startswith(p) for p in CREATION_ALLOWLIST_PREFIXES):
        return True
    extra = os.environ.get("PATH_EXISTENCE_ALLOWLIST", "")
    for prefix in (p.strip() for p in extra.split(":") if p.strip()):
        if rel_str.startswith(prefix):
            return True
    return False


def block(message: str) -> None:
    print(json.dumps({
        "decision": "block",
        "reason": f"[path-existence-guard] {message}",
    }))
    sys.exit(0)


def allow() -> None:
    print(json.dumps({"continue": True}))
    sys.exit(0)


_SDD_IDENTITY_RE = re.compile(
    r"^sdd-(init|explore|propose|spec|design|tasks|apply|verify|archive|onboard|debate|verify-diff)$"
)
_SDD_PATH_RE = re.compile(
    r"^openspec/changes/[a-z0-9-]+/[a-z0-9_.-]+\.md$"
)

# Spec-path guard: /spec command or sdd-spec subagent may write under openspec/specs/.
# Separate from SDD guard — Option B (new regex) to keep _SDD_IDENTITY_RE untouched.
_SPEC_IDENTITY_RE = re.compile(r"^(spec|sdd-spec)$")
_SPEC_PATH_RE = re.compile(r"^openspec/specs/[a-z0-9-]+\.md$")


def _resolve_identity(payload: dict) -> Optional[str]:
    # `agent_type` is the real key Claude Code emits in PreToolUse (value like
    # "sdd-propose"). The others are kept for backward compat with test fixtures
    # and older harness call sites.
    return (
        payload.get("agent_type")
        or payload.get("subagent_name")
        or payload.get("subagent_id")
        or payload.get("agentId")
        or None
    )


def is_sdd_whitelisted(payload: dict, target: Path, root: Path) -> Tuple[bool, str]:
    identity = _resolve_identity(payload)
    if not identity:
        return (False, "no-identity: subagent_name/subagent_id/agentId absent")
    if not _SDD_IDENTITY_RE.match(identity):
        return (False, f"identity-mismatch: {identity!r} not an SDD agent")
    try:
        rel = target.relative_to(root)
    except ValueError:
        rel = target
    rel_str = str(rel).replace(os.sep, "/")
    if not _SDD_PATH_RE.match(rel_str):
        return (False, f"path-mismatch: {rel_str!r} not under openspec/changes/")
    return (True, f"allow:sdd-{identity.split('-', 1)[1]}")


def is_spec_whitelisted(payload: dict, target: Path, root: Path) -> Tuple[bool, str]:
    identity = _resolve_identity(payload)
    if not identity:
        return (False, "no-identity: agent_type/subagent_name absent")
    if not _SPEC_IDENTITY_RE.match(identity):
        return (False, f"identity-mismatch: {identity!r} not spec or sdd-spec")
    try:
        rel = target.relative_to(root)
    except ValueError:
        rel = target
    rel_str = str(rel).replace(os.sep, "/")
    if not _SPEC_PATH_RE.match(rel_str):
        return (False, f"path-mismatch: {rel_str!r} not under openspec/specs/ or filename invalid")
    return (True, "allow:spec")


def write_audit_log(root: Path, subagent_name: Optional[str], target_path: str, decision: str, reason: str) -> None:
    try:
        audit_path = root / ".sdlc" / "state" / "path-guard-audit.jsonl"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        entry = json.dumps({
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "subagent_name": subagent_name,
            "target_path": target_path,
            "decision": decision,
            "reason": reason,
        })
        with audit_path.open("a", encoding="utf-8") as fh:
            fh.write(entry + "\n")
    except IOError:
        pass


def main() -> None:
    payload = parse_payload()
    tool = get_tool(payload)
    if tool not in ("Edit", "Write", "Read"):
        allow()

    inp = get_input(payload)
    raw_path = inp.get("file_path") or inp.get("path") or ""
    if not raw_path:
        allow()

    target = Path(raw_path)
    if not target.is_absolute():
        target = project_root() / target

    if tool == "Read":
        if not target.exists():
            block(
                f"Read target does not exist: {target}\n"
                "Use Glob/Grep to find the real path before Read, or correct the path."
            )
        allow()

    if tool == "Edit":
        if not target.exists():
            block(
                f"Edit target does not exist: {target}\n"
                "Edit requires an existing file. Use Write to create new files, "
                "or Glob to confirm the real path."
            )
        allow()

    # tool == "Write"
    root = project_root()

    # Identity check FIRST for SDD-protected paths (openspec/changes/*/).
    # Must run before parent.exists() to prevent the early-exit bypass.
    try:
        rel_str = str(target.relative_to(root)).replace(os.sep, "/")
    except ValueError:
        rel_str = str(target).replace(os.sep, "/")
    if _SDD_PATH_RE.match(rel_str):
        whitelisted, reason = is_sdd_whitelisted(payload, target, root)
        identity = _resolve_identity(payload)
        if whitelisted:
            write_audit_log(root, identity, str(target), "allow", reason)
            allow()
        write_audit_log(root, identity, str(target), "block", reason)
        block(
            f"SDD path write blocked — {reason}\n"
            "Only SDD sub-agents (sdd-spec, sdd-apply, etc.) may write under openspec/changes/."
        )

    if _SPEC_PATH_RE.match(rel_str):
        whitelisted, reason = is_spec_whitelisted(payload, target, root)
        identity = _resolve_identity(payload)
        if whitelisted:
            write_audit_log(root, identity, str(target), "allow", reason)
            allow()
        write_audit_log(root, identity, str(target), "block", reason)
        block(
            f"Spec path write blocked — {reason}\n"
            "Only /spec command or sdd-spec subagent may write under openspec/specs/."
        )

    parent = target.parent
    if parent.exists():
        allow()

    if is_creation_allowlisted(target, root):
        allow()

    block(
        f"Write parent directory does not exist: {parent}\n"
        "Verify the path or run mkdir explicitly first. If this is an intentional "
        "new directory, add a prefix to PATH_EXISTENCE_ALLOWLIST or place under "
        f"one of: {', '.join(CREATION_ALLOWLIST_PREFIXES)}."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Never block tool use on hook bug — fail open
        print(json.dumps({"continue": True}))
        sys.exit(0)
