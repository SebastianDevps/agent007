#!/usr/bin/env python3
"""sdd-verify-diff — _aggregator.py

Pure-logic aggregation for v7.1 P3 per-diff adversarial verify.

Inputs: a list of SubagentResponseV1 envelopes from `code-reviewer` subagents,
each one having reviewed a single file's diff in adversarial mode.

Output: a deterministic AggregateReport summarizing findings across diffs,
mapping code-reviewer severities (CRITICAL/HIGH/MEDIUM/LOW) into the
aggregate scale (high/med/low + blocking flag), and emitting a mechanical
verdict (clean | findings | blocked).

Determinism: same envelope inputs → same report bytes. No I/O, no time
calls inside the pure aggregation path (elapsed_ms is supplied or computed
by `aggregate_reviews` itself for top-level use).
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional

# --- Named constants ------------------------------------------------------

FINDING_HASH_LEN = 12

Severity = Literal["high", "med", "low"]
Verdict = Literal["clean", "findings", "blocked"]

# code-reviewer (existing P0 agent) emits CRITICAL/HIGH/MEDIUM/LOW.
# The aggregator collapses to high/med/low + blocking flag.
SEVERITY_MAP: dict[str, tuple[Severity, bool]] = {
    "CRITICAL": ("high", True),
    "HIGH":     ("high", True),
    "MEDIUM":   ("med",  False),
    "LOW":      ("low",  False),
}

SEVERITY_RANK: dict[Severity, int] = {"high": 3, "med": 2, "low": 1}

# Bullet form in the code-reviewer artifact body (REVIEWER mode):
#   ### HIGH
#   **<Title>** · `path/to/file:42` · Confidence: 90%
_HEADER_SEV_RE = re.compile(r"^###\s+(CRITICAL|HIGH|MEDIUM|LOW)\b", re.IGNORECASE)
_BULLET_RE = re.compile(r"^\*\*(?P<title>[^*]+?)\*\*\s*·\s*`(?P<path>[^`]+?)`")

# --- Data shapes ---------------------------------------------------------

@dataclass(frozen=True)
class Finding:
    finding_id: str
    file_path: str
    severity: Severity
    blocking: bool
    claim: str
    review_ref: str


@dataclass
class AggregateReport:
    files_reviewed: int
    findings_by_severity: dict[str, int]
    blocking_findings: list[Finding]
    review_refs: list[str]
    verdict: Verdict
    elapsed_ms: int
    all_findings: list[Finding] = field(default_factory=list)

    def to_dict(self, change_name: str = "", ts: str = "") -> dict:
        return {
            "ts": ts,
            "change": change_name,
            "files_reviewed": self.files_reviewed,
            "findings_by_severity": self.findings_by_severity,
            "blocking_findings": [asdict(f) for f in self.blocking_findings],
            "review_refs": self.review_refs,
            "verdict": self.verdict,
            "elapsed_ms": self.elapsed_ms,
        }


# --- Helpers --------------------------------------------------------------

def hash_finding(file_path: str, claim: str) -> str:
    key = (file_path + "::" + claim).encode("utf-8")
    return hashlib.sha1(key).hexdigest()[:FINDING_HASH_LEN]


def _extract_findings_from_body(body: str, default_path: str, review_ref: str) -> list[Finding]:
    """Parse a code-reviewer REVIEWER-mode artifact body into Findings."""
    out: list[Finding] = []
    current_sev: Optional[str] = None
    for raw in body.splitlines():
        line = raw.rstrip()
        header_match = _HEADER_SEV_RE.match(line)
        if header_match:
            current_sev = header_match.group(1).upper()
            continue
        bullet_match = _BULLET_RE.match(line)
        if not (bullet_match and current_sev):
            continue
        mapping = SEVERITY_MAP.get(current_sev)
        if not mapping:
            continue
        severity, blocking = mapping
        claim = bullet_match.group("title").strip()
        path_field = bullet_match.group("path").strip()
        file_path = path_field.split(":")[0] if path_field else default_path
        out.append(Finding(
            finding_id=hash_finding(file_path, claim),
            file_path=file_path,
            severity=severity,
            blocking=blocking,
            claim=claim,
            review_ref=review_ref,
        ))
    return out


def _findings_from_envelope(envelope: dict) -> list[Finding]:
    """Pull findings out of one SubagentResponseV1 envelope.

    Looks at envelope.body (test-fixture extension) first, then falls back
    to the executive_summary when body is absent. The artifact_ref is the
    review_ref carried into each Finding for traceability.
    """
    review_ref = envelope.get("artifact_ref", "") or ""
    default_path = envelope.get("file_path", "") or ""
    body = envelope.get("body") or envelope.get("artifact_body") or ""
    if body:
        return _extract_findings_from_body(body, default_path, review_ref)
    # Degraded mode: no body in fixture → use prefab findings list if present
    raw_findings = envelope.get("findings") or []
    out: list[Finding] = []
    for entry in raw_findings:
        sev_label = (entry.get("severity") or "").upper()
        mapping = SEVERITY_MAP.get(sev_label)
        if not mapping:
            continue
        severity, blocking_default = mapping
        # Allow explicit "blocking" override on the entry
        if "blocking" in entry:
            blocking = bool(entry["blocking"])
        else:
            blocking = blocking_default
        file_path = entry.get("file_path") or default_path or "unknown"
        claim = entry.get("claim") or entry.get("title") or ""
        if not claim:
            continue
        out.append(Finding(
            finding_id=hash_finding(file_path, claim),
            file_path=file_path,
            severity=severity,
            blocking=blocking,
            claim=claim,
            review_ref=review_ref,
        ))
    return out


def _dedupe_keep_highest(findings: list[Finding]) -> list[Finding]:
    by_id: dict[str, Finding] = {}
    for f in findings:
        existing = by_id.get(f.finding_id)
        if existing is None:
            by_id[f.finding_id] = f
            continue
        # Keep the one with higher severity; ties → keep the existing (stable)
        if SEVERITY_RANK[f.severity] > SEVERITY_RANK[existing.severity]:
            by_id[f.finding_id] = f
        elif (SEVERITY_RANK[f.severity] == SEVERITY_RANK[existing.severity]
              and f.blocking and not existing.blocking):
            # Same severity but new entry is blocking → prefer it
            by_id[f.finding_id] = f
    # Deterministic order: by file_path then finding_id
    return sorted(by_id.values(), key=lambda x: (x.file_path, x.finding_id))


def _derive_verdict(findings: list[Finding]) -> Verdict:
    if not findings:
        return "clean"
    if any(f.blocking for f in findings):
        return "blocked"
    return "findings"


# --- Public entrypoint ---------------------------------------------------

def aggregate_reviews(
    change_name: str,
    review_envelopes: list[dict],
) -> AggregateReport:
    """Aggregate N SubagentResponseV1 review envelopes into a single report."""
    started = time.monotonic()

    all_findings: list[Finding] = []
    review_refs: list[str] = []
    for env in review_envelopes:
        ref = env.get("artifact_ref")
        if ref:
            review_refs.append(ref)
        all_findings.extend(_findings_from_envelope(env))

    deduped = _dedupe_keep_highest(all_findings)

    counts = {"high": 0, "med": 0, "low": 0}
    for f in deduped:
        counts[f.severity] += 1

    blocking = [f for f in deduped if f.blocking]
    verdict = _derive_verdict(deduped)
    elapsed_ms = int((time.monotonic() - started) * 1000)

    return AggregateReport(
        files_reviewed=len(review_envelopes),
        findings_by_severity=counts,
        blocking_findings=blocking,
        review_refs=sorted(review_refs),
        verdict=verdict,
        elapsed_ms=elapsed_ms,
        all_findings=deduped,
    )


__all__ = [
    "Finding",
    "AggregateReport",
    "aggregate_reviews",
    "hash_finding",
    "SEVERITY_MAP",
]
