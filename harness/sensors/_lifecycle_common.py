"""
_lifecycle_common.py — Helpers compartidos para lifecycle hooks (clock-in, clock-out, bookend).

No es un hook ejecutable. Importado por lifecycle-clock-in.py, lifecycle-clock-out.py
y lifecycle-bookend.py. Stdlib-only.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

PIPE_BUF_LIMIT: int = 4096
DEFAULT_RECOVERY_WINDOW_HOURS: int = 4
TAIL_LINES: int = 200
LIFECYCLE_RECOVERY_WINDOW_HOURS: str = "LIFECYCLE_RECOVERY_WINDOW_HOURS"


# ---------------------------------------------------------------------------
# Funciones utilitarias
# ---------------------------------------------------------------------------

def project_root() -> Path:
    """Retorna el directorio raiz del proyecto buscando .claude/ hacia arriba."""
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


def now_iso() -> str:
    """Retorna timestamp ISO-8601 con timezone UTC."""
    return datetime.now(timezone.utc).isoformat()


def parse_payload() -> dict:
    """Lee stdin JSON; retorna {} en cualquier excepcion (fail-open)."""
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except Exception:
        return {}


def truncate_field(value: Optional[str], max_chars: int = 200) -> Optional[str]:
    """Trunca un string a max_chars agregando '...' si fue cortado."""
    if value is None:
        return None
    if len(value) <= max_chars:
        return value
    return value[:max_chars] + "..."


def _truncate_string_fields(record: dict, max_chars: int = 200) -> dict:
    """Trunca todos los campos string del dict a max_chars."""
    result = {}
    for key, val in record.items():
        if isinstance(val, str):
            result[key] = truncate_field(val, max_chars)
        else:
            result[key] = val
    return result


def append_jsonl(path: Path, record: dict) -> None:
    """Append-only atomico a JSONL. Crea directorio padre si no existe.

    Si la linea serializada supera PIPE_BUF_LIMIT bytes, trunca los campos
    string a 200 chars y reintenta. Si aun asi supera, escribe igual.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record) + "\n"
    if len(line.encode("utf-8")) >= PIPE_BUF_LIMIT:
        truncated = _truncate_string_fields(record, max_chars=200)
        line = json.dumps(truncated) + "\n"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line)


def _try_read_json(file_path: Path) -> Optional[dict]:
    """Intenta leer y parsear un archivo JSON. Retorna None en falla."""
    try:
        with file_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, IOError, OSError):
        return None


def read_index_with_fallback(root: Path) -> Optional[dict]:
    """Lee _index.json; en falla intenta .sdlc/state/_index.json.bak.

    Nunca escribe. Retorna None si ambos fallan.
    """
    primary = root / "openspec" / "changes" / "_index.json"
    backup = root / ".sdlc" / "state" / "_index.json.bak"
    result = _try_read_json(primary)
    if result is not None:
        return result
    return _try_read_json(backup)


if __name__ == "__main__":
    pass
