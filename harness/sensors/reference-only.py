#!/usr/bin/env python3
"""harness/sensors/reference-only.py — v7-F2 anti-broken-telephone enforcer.

Validates SubagentStop payloads against SubagentResponseV1. Mode via env var
HARNESS_REFERENCE_ONLY_MODE: shadow (default, always exit 0) | enforce (exit 1 on fail).
File-based refs only post-engram-removal (2026-05-23). No network, no LLM.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MODE_SHADOW, MODE_ENFORCE, DEFAULT_MODE = "shadow", "enforce", "shadow"
MAX_SUMMARY_CHARS = 240
MAX_SUMMARY_NEWLINES = 3

REQUIRED_KEYS = {"status", "artifact_ref", "executive_summary",
                 "next_recommended", "skill_resolution"}
ALLOWED_STATUS = {"done", "partial", "blocked"}
ALLOWED_SKILL_RESOLUTION = {"injected", "fallback-registry", "fallback-path", "none"}

ARTIFACT_REF_FILE_RE = re.compile(r"^file:[A-Za-z0-9/_.\-]+(#[^\s]+)?$")
MARKDOWN_FENCE_RE = re.compile(r"```|\*\*")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_LOG_PATH = PROJECT_ROOT / ".sdlc" / "state" / "reference-only-audit.jsonl"
TRANSCRIPT_TAIL_LINES = 400
JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n(\{.*?\})\s*\n```", re.DOTALL)


def _resolve_subagent_transcript(transcript_path: str) -> str:
    """Disambiguate layer: SubagentStop receives the PARENT session transcript;
    the actual bare envelope lives in a sibling sidechain at
    `<dir>/<session_id>/subagents/agent-*.jsonl`. Pick the newest if present."""
    p = Path(transcript_path)
    sub_dir = p.with_suffix("") / "subagents"
    if not sub_dir.is_dir():
        return transcript_path
    candidates = sorted(sub_dir.glob("agent-*.jsonl"),
                        key=lambda c: c.stat().st_mtime, reverse=True)
    return str(candidates[0]) if candidates else transcript_path


def _extract_reply_from_transcript(transcript_path: str) -> str:
    """Pull subagent envelope from JSONL: prefer the first fenced JSON block
    in the newest assistant text block; fall back to raw assistant text."""
    if not transcript_path:
        return ""
    resolved = _resolve_subagent_transcript(transcript_path)
    if not Path(resolved).exists():
        return ""
    try:
        lines = Path(resolved).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    fallback = ""
    for raw in reversed(lines[-TRANSCRIPT_TAIL_LINES:]):
        try:
            entry = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            continue
        if entry.get("type") != "assistant":
            continue
        content = entry.get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for block in reversed(content):
            if not (isinstance(block, dict) and block.get("type") == "text"):
                continue
            text = block.get("text")
            if not (isinstance(text, str) and text.strip()):
                continue
            match = JSON_FENCE_RE.search(text)
            if match:
                return match.group(1)
            if not fallback:
                fallback = text
    return fallback


def _finding(check: str, result: str, detail: str) -> dict:
    return {"check": check, "result": result, "detail": detail}


def _validate_schema(obj: dict) -> dict:
    missing = REQUIRED_KEYS - obj.keys()
    if missing:
        return _finding("schema", "fail", f"missing required keys: {sorted(missing)}")
    if obj.get("status") not in ALLOWED_STATUS:
        return _finding("schema", "fail", f"status must be one of {sorted(ALLOWED_STATUS)}")
    if obj.get("skill_resolution") not in ALLOWED_SKILL_RESOLUTION:
        return _finding("schema", "fail", "skill_resolution not in allowed enum")
    if not isinstance(obj.get("executive_summary"), str):
        return _finding("schema", "fail", "executive_summary must be string")
    if not isinstance(obj.get("artifact_ref"), str):
        return _finding("schema", "fail", "artifact_ref must be string")
    return _finding("schema", "pass", "all required keys present and typed")


def _validate_summary(summary: str) -> dict:
    if len(summary) > MAX_SUMMARY_CHARS:
        return _finding("summary_length", "fail", f"{len(summary)} chars > {MAX_SUMMARY_CHARS}")
    if summary.count("\n") > MAX_SUMMARY_NEWLINES:
        return _finding("summary_length", "fail",
                        f"{summary.count(chr(10))} newlines > {MAX_SUMMARY_NEWLINES}")
    if MARKDOWN_FENCE_RE.search(summary):
        return _finding("summary_format", "fail", "markdown fences or bold markers not allowed")
    return _finding("summary_length", "pass", f"{len(summary)} chars, plain text")


def _ref_shape_finding(ref: str) -> dict:
    if ARTIFACT_REF_FILE_RE.match(ref):
        return _finding("artifact_ref_shape", "pass", "matches file: contract pattern")
    return _finding("artifact_ref_shape", "fail", "does not match file: pattern")


def _resolve_artifact(ref: str) -> dict:
    raw = ref[len("file:"):].split("#", 1)[0]
    path = Path(raw) if Path(raw).is_absolute() else PROJECT_ROOT / raw
    if path.exists():
        return _finding("artifact_resolves", "pass", f"file exists: {raw}")
    return _finding("artifact_resolves", "fail", f"file not found: {raw}")


def _build_findings(reply: str) -> list[dict]:
    findings: list[dict] = []
    if not reply:
        findings.append(_finding("json_parse", "fail", "empty reply"))
        return findings
    try:
        parsed = json.loads(reply)
        findings.append(_finding("json_parse", "pass", "reply parses as JSON"))
    except json.JSONDecodeError as exc:
        findings.append(_finding("json_parse", "fail", f"reply is not valid JSON: {exc}"))
        return findings
    if not isinstance(parsed, dict):
        findings.append(_finding("schema", "fail", "top-level value is not an object"))
        return findings

    findings.append(_validate_schema(parsed))
    summary = parsed.get("executive_summary")
    if isinstance(summary, str):
        findings.append(_validate_summary(summary))
    ref = parsed.get("artifact_ref")
    if isinstance(ref, str):
        shape = _ref_shape_finding(ref)
        findings.append(shape)
        if shape["result"] == "pass":
            findings.append(_resolve_artifact(ref))
    return findings


def _append_audit(payload: dict, status: str, findings: list[dict], mode: str) -> None:
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    counts = {"pass": 0, "fail": 0, "unknown": 0}
    for f in findings:
        counts[f.get("result", "unknown")] = counts.get(f.get("result", "unknown"), 0) + 1
    line = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "subagent_id": (payload.get("subagent_id")
                        or payload.get("subagent_name")
                        or payload.get("agentId")
                        or payload.get("attributionAgent")),
        "session_id": payload.get("session_id"),
        "transcript_path": payload.get("transcript_path"),
        "status": status,
        "findings_count": counts,
    }
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line) + "\n")


def _resolve_mode() -> str:
    mode = os.environ.get("HARNESS_REFERENCE_ONLY_MODE", DEFAULT_MODE).strip().lower()
    return mode if mode in {MODE_SHADOW, MODE_ENFORCE} else DEFAULT_MODE


def main() -> int:
    mode = _resolve_mode()
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}
    # Synthetic tests pass `reply` directly. Real Claude Code SubagentStop
    # payload has no `reply` — extract from transcript_path.
    reply = (payload.get("reply") or "").strip()
    if not reply:
        reply = _extract_reply_from_transcript(payload.get("transcript_path", "")).strip()
    findings = _build_findings(reply)

    has_failures = any(f["result"] == "fail" for f in findings)
    status = "fail" if has_failures else "pass"
    hint = ("Re-emit a single JSON object that matches SubagentResponseV1. "
            "Persist detail behind artifact_ref. No prose outside the envelope."
            ) if has_failures else None

    json.dump({"status": status, "findings": findings,
               "remediation_hint": hint, "mode": mode}, sys.stdout)
    _append_audit(payload, status, findings, mode)

    if mode == MODE_ENFORCE and has_failures:
        sys.stderr.write(json.dumps({"remediation_hint": hint, "findings": findings}) + "\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
