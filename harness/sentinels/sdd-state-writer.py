#!/usr/bin/env python3
"""
sdd-state-writer.py — PostToolUse hook para mantener openspec/changes/_index.json.

Tras un Write/Edit a openspec/changes/<change>/<file>.md, recomputa el estado
del sub-change afectado y hace upsert atómico en _index.json.

Fail-open absoluto: cualquier excepción resulta en {"continue": true} exit 0.
PostToolUse no bloquea nunca — la acción ya ocurrió.
"""

import datetime
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

# PROFILE guard — short-circuit antes de cualquier I/O
if os.environ.get("CLAUDE_HOOK_PROFILE") == "minimal":
    sys.stdout.write('{"continue": true}\n')
    sys.exit(0)

_PATH_RE = re.compile(r"^openspec/changes/([a-z0-9-]+)/[a-z0-9_.-]+\.md$")
_AUDIT_SUBPATH = ".sdlc/state/state-machine-audit.jsonl"


def _project_root() -> Path:
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude" / "harness").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


def _parse_payload() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def _get_tool_name(payload: dict) -> str:
    return payload.get("tool_name") or payload.get("toolName") or ""


def _get_file_path(payload: dict) -> str:
    inp = (
        payload.get("tool_input")
        or payload.get("toolInput")
        or payload.get("input")
        or {}
    )
    return inp.get("file_path") or inp.get("path") or ""


def _to_relative(raw_path: str, root: Path) -> Optional[str]:
    try:
        p = Path(raw_path)
        if p.is_absolute():
            return str(p.relative_to(root)).replace(os.sep, "/")
        return str(p).replace(os.sep, "/")
    except ValueError:
        return None


def _allow() -> None:
    sys.stdout.write('{"continue": true}\n')
    sys.exit(0)


def _restore_from_bak(index_path: Path, bak_path: Path) -> None:
    try:
        if bak_path.exists():
            shutil.copy2(bak_path, index_path)
    except Exception:
        pass


def _noop_audit(audit_path: Path, tool_name: str, target_path: str, reason: str) -> None:
    """Escribe entrada noop al audit JSONL. Solo se llama cuando hay root resuelto."""
    import datetime as _dt
    try:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "tool_name": tool_name,
            "target_path": target_path,
            "decision": "noop",
            "reason": reason,
        }
        with open(audit_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
    except IOError:
        pass


def main() -> None:
    payload = _parse_payload()
    root = _project_root()
    audit_path = root / _AUDIT_SUBPATH

    tool_name = _get_tool_name(payload)
    raw_path = _get_file_path(payload)

    if tool_name not in ("Write", "Edit"):
        _noop_audit(audit_path, tool_name, raw_path, "wrong-tool")
        _allow()

    if not raw_path:
        _noop_audit(audit_path, tool_name, raw_path, "no-path")
        _allow()

    rel = _to_relative(raw_path, root)
    if rel is None:
        _noop_audit(audit_path, tool_name, raw_path, "wrong-path")
        _allow()

    match = _PATH_RE.match(rel)
    if not match:
        _noop_audit(audit_path, tool_name, rel, "wrong-path")
        _allow()

    change_name = match.group(1)
    if change_name == "archive" or change_name.startswith("_"):
        _noop_audit(audit_path, tool_name, rel, "wrong-path")
        _allow()

    # Importar módulo puro desde el mismo directorio
    sys.path.insert(0, str(Path(__file__).parent))
    from _state_machine import detect_phase, load_or_bootstrap, upsert, validate, write_atomic, append_audit  # noqa: E402

    index_path = root / "openspec" / "changes" / "_index.json"
    changes_root = root / "openspec" / "changes"
    bak_path = root / ".sdlc" / "state" / "_index.json.bak"
    change_dir = root / "openspec" / "changes" / change_name
    today = datetime.date.today().isoformat()
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
    audit_path = root / _AUDIT_SUBPATH

    try:
        last_phase, status = detect_phase(change_dir)
        doc = load_or_bootstrap(index_path, changes_root, today)

        existing = next((c for c in doc.get("changes", []) if c["name"] == change_name), None)
        prev_phase = existing["last_phase"] if existing else None
        prev_status = existing["status"] if existing else None

        new_doc = upsert(doc, change_name, (last_phase, status), today)

        try:
            validate(new_doc)
        except ValueError as validation_error:
            _restore_from_bak(index_path, bak_path)
            append_audit(audit_path, {
                "ts": ts,
                "change_name": change_name,
                "decision": "restored",
                "reason": str(validation_error),
            })
            _allow()

        write_atomic(index_path, new_doc, bak_path)

        new_entry = next((c for c in new_doc["changes"] if c["name"] == change_name), None)
        new_phase = new_entry["last_phase"] if new_entry else last_phase
        new_status = new_entry["status"] if new_entry else status
        decision = "noop" if (prev_phase == new_phase and prev_status == new_status) else "updated"

        append_audit(audit_path, {
            "ts": ts,
            "change_name": change_name,
            "prev_phase": prev_phase,
            "new_phase": new_phase,
            "status": new_status,
            "decision": decision,
        })

    except Exception as exc:
        append_audit(audit_path, {
            "ts": ts,
            "change_name": change_name,
            "decision": "error",
            "reason": str(exc),
        })

    _allow()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.stdout.write('{"continue": true}\n')
        sys.exit(0)
