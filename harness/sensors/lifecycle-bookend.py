#!/usr/bin/env python3
"""
lifecycle_bookend.py — SubagentStop hook: registra telemetria de subagentes.

Evento: SubagentStop
Escribe a: .sdlc/state/subagent-log.jsonl (SOLO este archivo — REQ-3.5)
No toca el log de sesiones (clock-in/clock-out — responsabilidad de otros hooks).

Schema linea:
  { ts, parent_session_id, subagent_type, duration_s, status, last_message }

REQ-3 compliance: duration_s y status son null en v1 (payload no provee start_ts
ni status confiable). last_message truncado a <=200 chars.
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Bootstrap path para importar _lifecycle_common desde el mismo directorio
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))

from _lifecycle_common import (  # noqa: E402
    append_jsonl,
    now_iso,
    parse_payload,
    project_root,
    truncate_field,
)

# ---------------------------------------------------------------------------
# PROFILE short-circuit (debe ser la primera logica ejecutable)
# ---------------------------------------------------------------------------
if os.environ.get("CLAUDE_HOOK_PROFILE") == "minimal":
    print(json.dumps({"continue": True}))
    sys.exit(0)


def _resolve_subagent_type(payload: dict) -> str:
    """Resuelve nombre del subagente con cadena de fallback (design §5.3).

    Orden: agent_type -> subagent_name -> agentId -> "unknown"
    """
    return (
        payload.get("agent_type")
        or payload.get("subagent_name")
        or payload.get("agentId")
        or "unknown"
    )


def main() -> dict:
    """Logica principal del hook. Retorna siempre {"continue": True}."""
    payload = parse_payload()

    parent_session_id = payload.get("session_id") or os.environ.get(
        "CLAUDE_SESSION_ID", ""
    )
    subagent_type = _resolve_subagent_type(payload)

    # v1: no derivamos duration_s (no hay start_ts en payload SubagentStop)
    duration_s = None  # null literal — REQ-3 amendment OQ-D2

    # v1: no derivamos status (heuristic diferida a v2)
    status = None  # null literal — REQ-3 amendment OQ-D2

    last_message = truncate_field(
        payload.get("last_assistant_message"), 200
    )

    event = {
        "ts": now_iso(),
        "parent_session_id": parent_session_id,
        "subagent_type": subagent_type,
        "duration_s": duration_s,
        "status": status,
        "last_message": last_message,
    }

    root = project_root()
    subagent_log = root / ".sdlc" / "state" / "subagent-log.jsonl"

    # REQ-3.5: writes to subagent-log.jsonl ONLY
    append_jsonl(subagent_log, event)

    return {"continue": True}


if __name__ == "__main__":
    try:
        result = main()
        print(json.dumps(result or {"continue": True}))
    except Exception as exc:  # noqa: BLE001
        print(exc, file=sys.stderr)
        print(json.dumps({"continue": True}))
        sys.exit(0)
