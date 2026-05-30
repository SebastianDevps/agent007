#!/usr/bin/env python3
"""
sdd-wip-guard.py — PreToolUse hook, WIP=1 enforcement.

Bloquea Write a openspec/changes/<name>/proposal.md cuando wip_count >= max_wip.
Deja pasar: tools no-Write, paths que no son proposal.md, bootstrap (sin _index.json),
re-edición del mismo sub-change activo, escape hatch wip-override-once, excepciones
internas (fail-open). Identity se loguea pero no condiciona la decisión.
"""

import datetime
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")
if PROFILE == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)

_PATH_RE = re.compile(r"^openspec/changes/([a-z0-9-]+)/proposal\.md$")


def _project_root() -> Path:
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude" / "harness").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


def _resolve_identity(payload: dict) -> Optional[str]:
    # Replica path-existence-guard._resolve_identity (design §5.3)
    return (
        payload.get("agent_type")
        or payload.get("subagent_name")
        or payload.get("subagent_id")
        or payload.get("agentId")
        or None
    )


def _resolve_candidate(payload: dict, root: Path) -> Optional[str]:
    inp = payload.get("tool_input") or payload.get("toolInput") or payload.get("input") or {}
    raw = inp.get("file_path") or inp.get("path") or ""
    if not raw:
        return None
    target = Path(raw)
    if target.is_absolute():
        try:
            target = target.relative_to(root)
        except ValueError:
            return None
    rel = str(target).replace(os.sep, "/")
    m = _PATH_RE.match(rel)
    return m.group(1) if m else None


def _audit(root: Path, candidate: Optional[str], identity: Optional[str],
           active: list, decision: str, reason: Optional[str] = None) -> None:
    try:
        audit_path = root / ".sdlc" / "state" / "wip-guard-audit.jsonl"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        entry: dict = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "candidate": candidate,
            "identity": identity,
            "active_changes": active,
            "decision": decision,
        }
        if reason:
            entry["reason"] = reason
        with open(audit_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except IOError:
        pass


def _check_override_consume(root: Path) -> bool:
    """Consume .sdlc/state/wip-override-once si existe. Retorna True si existía."""
    flag = root / ".sdlc" / "state" / "wip-override-once"
    if not flag.exists():
        return False
    try:
        flag.unlink()
    except OSError:
        pass
    return True


def _allow(root: Path, candidate: Optional[str], identity: Optional[str],
           active: list, reason: str) -> None:
    _audit(root, candidate, identity, active, "allow", reason)
    print(json.dumps({"continue": True}))
    sys.exit(0)


def _block(root: Path, candidate: str, identity: Optional[str], active: list,
           max_wip: int) -> None:
    names = ", ".join(active) if active else "(none)"
    msg = (
        f"[sdd-wip-guard] BLOCKED: there are {len(active)} active sub-change(s). "
        f"max_wip={max_wip}.\n"
        f"Active: {names}.\n"
        f'Archive an active sub-change before creating "{candidate}".\n'
        f"One-shot override: touch .sdlc/state/wip-override-once and retry."
    )
    _audit(root, candidate, identity, active, "block")
    sys.stderr.write(msg + "\n")
    print(json.dumps({"decision": "block", "reason": msg}))
    sys.exit(2)


def _load_index_safe(index_path: Path) -> Optional[dict]:
    try:
        with open(index_path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _noop_audit_guard(root: Path, tool: str, raw_path: str, reason: str) -> None:
    """Escribe entrada noop al audit JSONL del guard."""
    try:
        audit_path = root / ".sdlc" / "state" / "wip-guard-audit.jsonl"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "tool_name": tool,
            "target_path": raw_path,
            "decision": "noop",
            "reason": reason,
        }
        with open(audit_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except IOError:
        pass


def main() -> None:
    try:
        raw = sys.stdin.read()
        payload: dict = json.loads(raw) if raw.strip() else {}
    except Exception:
        payload = {}

    tool = payload.get("tool_name") or payload.get("toolName") or ""
    root = _project_root()
    inp = payload.get("tool_input") or payload.get("toolInput") or payload.get("input") or {}
    raw_path = inp.get("file_path") or inp.get("path") or ""

    if tool != "Write":
        _noop_audit_guard(root, tool, raw_path, "wrong-tool")
        print(json.dumps({"continue": True}))
        sys.exit(0)

    candidate = _resolve_candidate(payload, root)

    if candidate is None:
        # Path no matchea el filtro — no es un proposal.md → no-op
        _noop_audit_guard(root, tool, raw_path, "wrong-path")
        print(json.dumps({"continue": True}))
        sys.exit(0)

    identity = _resolve_identity(payload)

    try:
        index_path = root / "openspec" / "changes" / "_index.json"

        if not index_path.exists():
            _allow(root, candidate, identity, [], "bootstrap")

        doc = _load_index_safe(index_path)
        if doc is None:
            _allow(root, candidate, identity, [], "allow-on-corrupt")

        active_entries = [c for c in doc.get("changes", []) if c.get("status") != "archived"]
        active_names = [c["name"] for c in active_entries]

        # Re-edición del mismo sub-change activo → siempre allow
        if candidate in active_names:
            _allow(root, candidate, identity, active_names, "re-edit-existing-active")

        # Escape hatch consume-on-use
        if _check_override_consume(root):
            _audit(root, candidate, identity, active_names, "override")
            print(json.dumps({"continue": True}))
            sys.exit(0)

        max_wip = doc.get("max_wip", 1)
        if len(active_entries) >= max_wip:
            _block(root, candidate, identity, active_names, max_wip)

        _allow(root, candidate, identity, active_names, "under-wip")

    except SystemExit:
        raise
    except Exception as exc:
        # Fail-open: cualquier bug del hook → allow + audit de error
        try:
            identity_safe = _resolve_identity(payload)
        except Exception:
            identity_safe = None
        _audit(root, candidate, identity_safe, [], "error", str(exc))
        print(json.dumps({"continue": True}))
        sys.exit(0)


if __name__ == "__main__":
    main()
