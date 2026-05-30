#!/usr/bin/env python3
"""
debate-trigger.py — v7.1 triage Guide.

Fires on SubagentStop. Self-filters to sdd-design phase. Reads four signals
from the proposal/design/tasks artifacts, decides the triage tier
(trivial | medium | high), and persists the decision to
.sdlc/state/<change-name>/triage.json.

The orchestrator reads this manifest before invoking the four automatic gates:
  - sdd-checklist  (after sdd-spec)    → flag: checklist_required
  - sdd-debate     (after sdd-design)  → flag: debate_required
  - sdd-analyze    (after sdd-tasks)   → flag: analyze_required
  - sdd-verify-diff (after sdd-apply)  → flag: per_diff_verify_required

Flag thresholds:
  - checklist_required: tier in {medium, high}   (cheap; runs broadly)
  - debate_required:    tier in {medium, high}   (same threshold as checklist)
  - analyze_required:   tier in {medium, high} AND files_touched > files_high_tier
                        (heavier; only when scope is wide enough to drift)
  - per_diff_verify_required: tier == high       (heaviest; high-risk only)

Trivial tier skips all four gates (0% token overhead).

Degrades gracefully — missing signals default to medium tier. Never crashes
the orchestrator. Exit 0 always (except on hard I/O error).
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# --- Constants -------------------------------------------------------------

DEFAULT_FILES_HIGH = 3
DEFAULT_FILES_TRIVIAL = 1
DEFAULT_RISK = "medium"

SDD_DESIGN_AGENTS = ("sdd-design", "sdd-design-A", "sdd-design-B")
PUBLIC_SURFACE_KEYWORDS = ("public api", "exported", "breaking change", "public surface")
RISK_HEADING_RE = re.compile(r"^\s*##\s*.*risk", re.IGNORECASE)
RISK_VALUE_RE = re.compile(r"\b(low|medium|high|critical)\b", re.IGNORECASE)
FRONTMATTER_RISK_RE = re.compile(r"^risk[_-]?level\s*:\s*(\w+)", re.IGNORECASE | re.MULTILINE)


# --- TOML loading (stdlib only, Python 3.11+ has tomllib) ------------------

def load_triage_config(repo_root: Path) -> dict:
    """Load triage-paths.toml. Fallback to defaults if missing/unreadable."""
    cfg_path = repo_root / ".claude" / "harness" / "triage-paths.toml"
    defaults = {
        "sensitive_patterns": [
            "auth/", "authentication/", "payment/", "payments/", "billing/",
            "crypto/", "encryption/", "secrets/", "credentials/",
            "migrations/", "schema/", "iam/", "permissions/",
        ],
        "files_high_tier": DEFAULT_FILES_HIGH,
        "files_trivial": DEFAULT_FILES_TRIVIAL,
    }
    if not cfg_path.exists():
        return defaults
    try:
        import tomllib  # type: ignore[import-not-found]
        with cfg_path.open("rb") as fh:
            data = tomllib.load(fh)
        return {
            "sensitive_patterns": data.get("sensitive_paths", {}).get("patterns", defaults["sensitive_patterns"]),
            "files_high_tier": data.get("thresholds", {}).get("files_high_tier", DEFAULT_FILES_HIGH),
            "files_trivial": data.get("thresholds", {}).get("files_trivial", DEFAULT_FILES_TRIVIAL),
        }
    except Exception:
        return defaults


# --- Repo root detection ---------------------------------------------------

def find_repo_root(start: Optional[Path] = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ".claude" / "harness").is_dir():
            return candidate
    return here


# --- Signal extraction -----------------------------------------------------

def read_change_proposal(repo_root: Path, change_name: str) -> dict:
    """Reads proposal signals from either:
       - .sdlc/state/<change>/proposal.json (test fixture / cached)
       - openspec/changes/<change>/proposal.md (file backend)
       Returns {} if nothing found.
    """
    state_json = repo_root / ".sdlc" / "state" / change_name / "proposal.json"
    if state_json.is_file():
        try:
            return json.loads(state_json.read_text(encoding="utf-8"))
        except Exception:
            pass

    md_path = repo_root / "openspec" / "changes" / change_name / "proposal.md"
    if md_path.is_file():
        try:
            text = md_path.read_text(encoding="utf-8", errors="replace")
            return parse_proposal_markdown(text)
        except Exception:
            pass
    return {}


def parse_proposal_markdown(text: str) -> dict:
    out: dict = {}
    fm = FRONTMATTER_RISK_RE.search(text)
    if fm:
        out["risk_level"] = fm.group(1).lower()
    else:
        for i, line in enumerate(text.splitlines()):
            if RISK_HEADING_RE.match(line):
                tail = "\n".join(text.splitlines()[i:i + 6])
                m = RISK_VALUE_RE.search(tail)
                if m:
                    out["risk_level"] = m.group(1).lower()
                    break
    lower = text.lower()
    out["public_surface_changed"] = any(k in lower for k in PUBLIC_SURFACE_KEYWORDS)
    return out


def read_design_signals(repo_root: Path, change_name: str) -> dict:
    state_json = repo_root / ".sdlc" / "state" / change_name / "design.json"
    if state_json.is_file():
        try:
            return json.loads(state_json.read_text(encoding="utf-8"))
        except Exception:
            pass
    md_path = repo_root / "openspec" / "changes" / change_name / "design.md"
    if md_path.is_file():
        try:
            text = md_path.read_text(encoding="utf-8", errors="replace").lower()
            return {"public_surface_changed": any(k in text for k in PUBLIC_SURFACE_KEYWORDS)}
        except Exception:
            pass
    return {}


def read_tasks_signals(repo_root: Path, change_name: str) -> dict:
    state_json = repo_root / ".sdlc" / "state" / change_name / "tasks.json"
    if state_json.is_file():
        try:
            data = json.loads(state_json.read_text(encoding="utf-8"))
            if isinstance(data.get("files"), list):
                return {"files_touched": len(data["files"]), "paths": data["files"]}
            return data
        except Exception:
            pass
    return {}


def match_sensitive_paths(paths: list[str], patterns: list[str]) -> list[str]:
    hits: list[str] = []
    for path in paths:
        for pat in patterns:
            if pat in path:
                hits.append(pat)
    return hits


# --- Decision logic --------------------------------------------------------

def triage_tier(risk: str, files: int, public_surface: bool, sensitive_match: bool,
                override: Optional[str], cfg: dict) -> str:
    if override == "force":
        return "high"
    if override == "skip":
        return "trivial"
    if risk in ("high", "critical"):
        return "high"
    if files > cfg["files_high_tier"]:
        return "high"
    if sensitive_match:
        return "high"
    if (risk == "low" and files <= cfg["files_trivial"]
            and not public_surface and not sensitive_match):
        return "trivial"
    return "medium"


def tier_to_flags(tier: str) -> tuple[bool, bool]:
    if tier == "trivial":
        return (False, False)
    if tier == "medium":
        return (True, False)
    return (True, True)


def compute_gate_flags(tier: str, files_touched: int, files_high_tier: int) -> dict:
    """Compute the four v7.1 automatic-gate flags from tier + scope.

    - checklist_required: medium/high (cheap)
    - debate_required: medium/high (mirrors checklist)
    - analyze_required: medium/high AND files_touched > files_high_tier (heavier)
    - per_diff_verify_required: high only (heaviest)
    """
    if tier == "trivial":
        return {
            "checklist_required": False,
            "debate_required": False,
            "analyze_required": False,
            "per_diff_verify_required": False,
        }
    is_high = tier == "high"
    wide_scope = files_touched > files_high_tier
    return {
        "checklist_required": True,
        "debate_required": True,
        "analyze_required": wide_scope,
        "per_diff_verify_required": is_high,
    }


# --- Output ----------------------------------------------------------------

def write_manifest(repo_root: Path, change_name: str, payload: dict) -> Path:
    out_dir = repo_root / ".sdlc" / "state" / change_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "triage.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


# --- Main ------------------------------------------------------------------

def main() -> int:
    try:
        raw = sys.stdin.read()
        payload: dict[str, Any] = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # never block on malformed input

    agent_name = payload.get("agent_name") or payload.get("subagent_type") or ""
    if agent_name and agent_name not in SDD_DESIGN_AGENTS:
        return 0

    change_name = (payload.get("change_name")
                   or payload.get("change")
                   or os.environ.get("SDD_CHANGE_NAME", ""))
    if not change_name:
        return 0  # nothing to triage

    override = payload.get("debate_override") or os.environ.get("SDD_DEBATE_OVERRIDE")
    if override not in (None, "", "force", "skip"):
        override = None

    repo_root = find_repo_root()
    cfg = load_triage_config(repo_root)

    proposal = read_change_proposal(repo_root, change_name)
    design = read_design_signals(repo_root, change_name)
    tasks = read_tasks_signals(repo_root, change_name)

    risk = (proposal.get("risk_level") or DEFAULT_RISK).lower()
    if risk not in ("low", "medium", "high", "critical"):
        risk = DEFAULT_RISK

    files_touched = (tasks.get("files_touched")
                     or proposal.get("files_touched")
                     or design.get("files_touched")
                     or 1)
    try:
        files_touched = int(files_touched)
    except (TypeError, ValueError):
        files_touched = 1

    public_surface = bool(proposal.get("public_surface_changed")
                          or design.get("public_surface_changed")
                          or False)

    paths = (tasks.get("paths") or proposal.get("paths") or [])
    if not isinstance(paths, list):
        paths = []
    sensitive_hits = match_sensitive_paths([str(p) for p in paths], cfg["sensitive_patterns"])

    tier = triage_tier(risk, files_touched, public_surface, bool(sensitive_hits),
                       override, cfg)
    flags = compute_gate_flags(tier, files_touched, cfg["files_high_tier"])

    manifest = {
        "schema_version": 2,
        "ts": datetime.now(timezone.utc).isoformat(),
        "change": change_name,
        "triage_tier": tier,
        "checklist_required": flags["checklist_required"],
        "debate_required": flags["debate_required"],
        "analyze_required": flags["analyze_required"],
        "per_diff_verify_required": flags["per_diff_verify_required"],
        "signals": {
            "risk_level": risk,
            "files_touched": files_touched,
            "public_surface_changed": public_surface,
            "sensitive_paths_hit": sensitive_hits,
        },
        "manual_override": override if override in ("force", "skip") else None,
    }

    try:
        write_manifest(repo_root, change_name, manifest)
    except Exception as exc:  # I/O failure — informational, never block
        print(f"[triage] change={change_name} tier={tier} write_error={exc}", file=sys.stderr)
        return 0

    sig_summary = (f"r={risk},f={files_touched},"
                   f"p={public_surface},s={len(sensitive_hits)}")
    print(f"[triage] change={change_name} tier={tier} signals={sig_summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
