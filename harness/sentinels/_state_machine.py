"""
_state_machine.py — Módulo puro de state machine para openspec/changes/_index.json.

Expone: detect_phase, validate, upsert, write_atomic, bootstrap, load_or_bootstrap,
append_audit. Ninguna función escribe a disco salvo write_atomic y append_audit.
Sin dependencias externas (stdlib únicamente).
"""

import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

SCHEMA_VERSION: int = 1
MAX_WIP: int = 1
INDEX_PATH: str = "openspec/changes/_index.json"

STATUS_ENUM: frozenset = frozenset({
    "proposing", "speccing", "designing", "tasking",
    "applying", "verifying", "archived", "unknown",
})

LAST_PHASE_ENUM: frozenset = frozenset({
    "propose", "spec", "design", "tasks",
    "apply", "verify", "archive", "unknown",
})

# Tabla de prioridad: archivo → (last_phase, status).
# Orden importa: el primero que matchee en iteración gana (más avanzado primero).
ARTIFACT_TO_PHASE: dict = {
    "archive-report.md": ("archive", "archived"),
    "verify-report.md":  ("verify",  "verifying"),
    "apply-progress.md": ("apply",   "applying"),
    "tasks.md":          ("tasks",   "tasking"),
    "design.md":         ("design",  "designing"),
    "spec.md":           ("spec",    "speccing"),
    "proposal.md":       ("propose", "proposing"),
}

_CHANGE_NAME_RE = re.compile(r"^[a-z0-9-]+$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

_ALLOWED_ENTRY_KEYS = frozenset({"name", "status", "last_phase", "started", "archived"})


# ---------------------------------------------------------------------------
# detect_phase
# ---------------------------------------------------------------------------

def detect_phase(change_dir: Path) -> tuple:
    """Retorna (last_phase, status) para el artefacto más avanzado presente."""
    present = {f.name for f in change_dir.iterdir() if f.suffix == ".md"} if change_dir.is_dir() else set()
    for artifact, phase_status in ARTIFACT_TO_PHASE.items():
        if artifact in present:
            return phase_status
    return ("unknown", "unknown")


# ---------------------------------------------------------------------------
# validate
# ---------------------------------------------------------------------------

def validate(doc: dict) -> None:
    """Valida invariantes del documento _index.json. Lanza ValueError si falla."""
    _validate_top_level(doc)
    _validate_entries(doc["changes"])
    _validate_wip_count(doc)


def _validate_top_level(doc: dict) -> None:
    """Valida campos de nivel raíz y tipos."""
    required = {"schema_version", "wip_count", "max_wip", "changes"}
    missing = required - doc.keys()
    if missing:
        raise ValueError(f"Campos requeridos ausentes: {missing}")
    extra = set(doc.keys()) - required
    if extra:
        raise ValueError(f"Campos extra no permitidos: {extra}")
    if not isinstance(doc["schema_version"], int) or doc["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"schema_version debe ser {SCHEMA_VERSION}, got {doc['schema_version']!r}")
    if not isinstance(doc["max_wip"], int) or doc["max_wip"] != MAX_WIP:
        raise ValueError(f"max_wip debe ser {MAX_WIP}, got {doc['max_wip']!r}")
    if not isinstance(doc["wip_count"], int) or doc["wip_count"] < 0:
        raise ValueError(f"wip_count debe ser int >= 0, got {doc['wip_count']!r}")
    if not isinstance(doc["changes"], list):
        raise ValueError("changes debe ser una lista")


def _validate_entries(entries: list) -> None:
    """Valida cada entrada ChangeEntry."""
    names_seen: set = set()
    for i, entry in enumerate(entries):
        prefix = f"changes[{i}]"
        extra_keys = set(entry.keys()) - _ALLOWED_ENTRY_KEYS
        if extra_keys:
            raise ValueError(f"{prefix}: campos extra no permitidos: {extra_keys}")
        for field in ("name", "status", "last_phase"):
            if field not in entry:
                raise ValueError(f"{prefix}: campo requerido ausente: {field}")
        if not isinstance(entry["name"], str) or not _CHANGE_NAME_RE.match(entry["name"]):
            raise ValueError(f"{prefix}: name inválido: {entry['name']!r}")
        if entry["name"] in names_seen:
            raise ValueError(f"{prefix}: name duplicado: {entry['name']!r}")
        names_seen.add(entry["name"])
        if entry["status"] not in STATUS_ENUM:
            raise ValueError(f"{prefix}: status inválido: {entry['status']!r}")
        if entry["last_phase"] not in LAST_PHASE_ENUM:
            raise ValueError(f"{prefix}: last_phase inválido: {entry['last_phase']!r}")
        if "started" not in entry:
            raise ValueError(f"{prefix}: campo requerido ausente: started")
        if entry["started"] is not None:
            if not isinstance(entry["started"], str) or not _DATE_RE.match(entry["started"]):
                raise ValueError(f"{prefix}: started debe ser YYYY-MM-DD o null")
        _validate_archived_field(entry, prefix)


def _validate_archived_field(entry: dict, prefix: str) -> None:
    """Valida invariante: archived presente ↔ status == 'archived'."""
    is_archived_status = entry["status"] == "archived"
    has_archived_field = "archived" in entry
    if is_archived_status and not has_archived_field:
        raise ValueError(f"{prefix}: status='archived' requiere campo 'archived'")
    if not is_archived_status and has_archived_field:
        raise ValueError(f"{prefix}: campo 'archived' presente pero status={entry['status']!r}")
    if has_archived_field and entry["archived"] is not None:
        if not isinstance(entry["archived"], str) or not _DATE_RE.match(entry["archived"]):
            raise ValueError(f"{prefix}: archived debe ser YYYY-MM-DD o null")


def _validate_wip_count(doc: dict) -> None:
    """Valida que wip_count coincide con el conteo derivado."""
    computed = sum(1 for c in doc["changes"] if c.get("status") != "archived")
    if doc["wip_count"] != computed:
        raise ValueError(f"wip_count={doc['wip_count']} no coincide con computed={computed}")


# ---------------------------------------------------------------------------
# upsert
# ---------------------------------------------------------------------------

def upsert(doc: dict, change_name: str, phase_result: tuple, today_str: str) -> dict:
    """Agrega o actualiza la entrada change_name. Recalcula wip_count. Retorna doc."""
    if not _CHANGE_NAME_RE.match(change_name):
        raise ValueError(f"change_name inválido: {change_name!r}")

    last_phase, status = phase_result
    changes = doc["changes"]

    existing = next((c for c in changes if c["name"] == change_name), None)

    if existing is None:
        entry: dict = {
            "name": change_name,
            "status": status,
            "last_phase": last_phase,
            "started": today_str,
        }
        if last_phase == "archive":
            entry["archived"] = today_str
        changes.append(entry)
    else:
        existing["status"] = status
        existing["last_phase"] = last_phase
        if last_phase == "archive" and "archived" not in existing:
            existing["archived"] = today_str
        if last_phase != "archive" and "archived" in existing:
            del existing["archived"]

    doc["wip_count"] = sum(1 for c in changes if c.get("status") != "archived")
    return doc


# ---------------------------------------------------------------------------
# write_atomic
# ---------------------------------------------------------------------------

def write_atomic(path: Path, doc: dict, bak_path: Path) -> None:
    """Escribe doc en path de forma atómica (tempfile + fsync + os.replace)."""
    parent = path.parent
    parent.mkdir(parents=True, exist_ok=True)
    bak_path.parent.mkdir(parents=True, exist_ok=True)

    # Limpieza pasiva de temporales huérfanos
    for orphan in parent.glob("_index.*.tmp"):
        try:
            os.unlink(orphan)
        except OSError:
            pass

    # Rotar backup antes del write nuevo
    if path.exists():
        shutil.copy2(path, bak_path)

    tmp_path: Optional[str] = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=parent,
            prefix="_index.",
            suffix=".tmp",
            delete=False,
            encoding="utf-8",
        ) as tmp:
            tmp_path = tmp.name
            json.dump(doc, tmp, indent=2, sort_keys=False)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


# ---------------------------------------------------------------------------
# bootstrap
# ---------------------------------------------------------------------------

def bootstrap(changes_root: Path, today_str: str) -> dict:
    """Escanea changes_root y construye índice inicial. No escribe a disco."""
    doc: dict = {
        "schema_version": SCHEMA_VERSION,
        "wip_count": 0,
        "max_wip": MAX_WIP,
        "changes": [],
    }

    if not changes_root.is_dir():
        return doc

    for sub in sorted(changes_root.iterdir()):
        if not sub.is_dir():
            continue
        if sub.name.startswith(".") or sub.name == "archive":
            continue
        last_phase, status = detect_phase(sub)
        entry: dict = {
            "name": sub.name,
            "status": status,
            "last_phase": last_phase,
            "started": None,
        }
        if last_phase == "archive":
            entry["archived"] = None
        doc["changes"].append(entry)

    doc["wip_count"] = sum(1 for c in doc["changes"] if c.get("status") != "archived")
    return doc


# ---------------------------------------------------------------------------
# load_or_bootstrap
# ---------------------------------------------------------------------------

def load_or_bootstrap(index_path: Path, changes_root: Path, today_str: str) -> dict:
    """Carga _index.json. En error, intenta .bak. En fallo total, hace bootstrap."""
    bak_path = index_path.parent.parent.parent / ".sdlc" / "state" / "_index.json.bak"

    doc = _try_load_json(index_path)
    if doc is not None:
        return doc

    doc = _try_load_json(bak_path)
    if doc is not None:
        return doc

    return bootstrap(changes_root, today_str)


def _try_load_json(path: Path) -> Optional[dict]:
    """Intenta leer y parsear JSON. Retorna None en cualquier error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# append_audit
# ---------------------------------------------------------------------------

def append_audit(audit_path: Path, entry: dict) -> None:
    """Agrega una línea JSON al archivo audit JSONL. Fail-open: ignora IOError."""
    try:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except IOError:
        pass
