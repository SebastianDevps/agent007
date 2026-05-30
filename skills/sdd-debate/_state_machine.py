#!/usr/bin/env python3
"""
sdd-debate — _state_machine.py

Deterministic dual-proposer convergence engine for v7.1 P1.

Inputs: two design proposals (markdown, from blind sdd-design A and B).
Process: extract findings → hash → run stance state machine over disputed
findings → derive verdict mechanically (no LLM judge).

Public surface:
    run_debate(...)  -> DebateResult

Same inputs MUST produce same outputs (determinism is part of the contract).

This module is pure logic. The skill caller handles persistence (file writes
to .sdlc/state/<change>/, etc.) and any real subagent re-invocations. When
`subagent_invoker` is None (test mode), disputed-but-budget-remaining
findings fall back to a fixed "both stick to their stance" simulation —
this keeps the machine deterministic without real LLM calls.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Callable, Literal, Optional

# --- Named constants -------------------------------------------------------

FINDING_HASH_LEN = 12
MEDIUM_TIER_ROUNDS = 1
HIGH_TIER_ROUNDS = 2
MEDIUM_TIER_WALL_MS = 90_000
HIGH_TIER_WALL_MS = 180_000

VALID_TIERS = ("medium", "high")
VALID_STANCES = ("accept", "concede", "defend", "dismiss")
Stance = Literal["accept", "concede", "defend", "dismiss"]
TerminalState = Literal["agreed", "rejected", "disputed", "pending"]
Verdict = Literal["consensus", "hybrid", "divergence"]
Instance = Literal["A", "B", "both"]

# --- Stance transition table ----------------------------------------------
# Key: frozenset would lose order (we need to know who said what), so we use
# tuple (A_stance, B_stance). The table maps to (terminal_state, needs_round).
# When needs_round=True the caller must re-invoke and call resolve_round()
# with the new stances; when False the terminal_state is final.
#
# Edge cases not in spec, with sensible defaults documented inline:
#   - (concede, concede): both partial agree → agreed
#   - (concede, accept):  symmetric of (accept, concede) → agreed
#   - (defend, accept):   symmetric of (accept, defend) → needs round
#   - (defend, concede):  symmetric of (concede, defend) → needs round
#   - (defend, dismiss):  one defends, other dismisses → disputed (mutual hold)
#   - (dismiss, defend):  symmetric → disputed
#   - (concede, dismiss): caveat vs. out-of-scope → disputed
#   - (dismiss, concede): symmetric → disputed

INITIAL_TRANSITIONS: dict[tuple[Stance, Stance], tuple[TerminalState, bool]] = {
    ("accept",  "accept"):  ("agreed",   False),
    ("accept",  "concede"): ("agreed",   False),
    ("concede", "accept"):  ("agreed",   False),
    ("concede", "concede"): ("agreed",   False),
    ("accept",  "defend"):  ("pending",  True),
    ("defend",  "accept"):  ("pending",  True),
    ("concede", "defend"):  ("pending",  True),
    ("defend",  "concede"): ("pending",  True),
    ("defend",  "defend"):  ("disputed", False),
    ("accept",  "dismiss"): ("pending",  True),
    ("dismiss", "accept"):  ("pending",  True),
    ("dismiss", "dismiss"): ("rejected", False),
    ("defend",  "dismiss"): ("disputed", False),
    ("dismiss", "defend"):  ("disputed", False),
    ("concede", "dismiss"): ("disputed", False),
    ("dismiss", "concede"): ("disputed", False),
}

# After a round of re-invocation, the table is the same — we just re-look-up.
# If both sides STILL produce a pair that needs a round and the budget is
# exhausted, the finding terminates as `disputed`.

# --- Data shapes -----------------------------------------------------------

@dataclass
class Finding:
    finding_id: str
    source_instance: Instance
    file_path: str
    claim: str
    initial_stance: dict = field(default_factory=dict)
    final_stance: dict = field(default_factory=dict)
    terminal_state: TerminalState = "pending"


@dataclass
class DebateResult:
    verdict: Verdict
    rounds_executed: int
    findings: list[Finding]
    consensus_proposal: Optional[str]
    divergence_report: Optional[str]
    elapsed_ms: int


# --- Finding extraction ----------------------------------------------------

# A finding line looks like: "- <file/path>: <claim text>" or a bullet under
# a heading like "## Recommendations" / "## Issues" / "## Findings".
# This parser is intentionally simple — proposals from sdd-design follow a
# stable enough structure that regex on bullets is sufficient.

_FINDING_LINE_RE = re.compile(r"^\s*[-*]\s+`?([^`:]+?)`?\s*[:—–-]\s+(.+)$")
_FINDING_HEADINGS = ("findings", "issues", "recommendations", "concerns", "risks")


def _is_findings_heading(line: str) -> bool:
    stripped = line.strip().lower().lstrip("#").strip()
    return any(stripped.startswith(h) for h in _FINDING_HEADINGS)


def extract_findings(markdown: str, source: Literal["A", "B"]) -> list[Finding]:
    """Pull findings out of a design proposal markdown body.

    Pragmatic parser: scans for findings-y headings, collects subsequent
    bullet lines of shape `- <file>: <claim>`. Anything outside that
    pattern is ignored — the rest of the proposal is narrative.
    """
    in_section = False
    out: list[Finding] = []
    for raw in markdown.splitlines():
        if raw.startswith("#"):
            in_section = _is_findings_heading(raw)
            continue
        if not in_section:
            continue
        m = _FINDING_LINE_RE.match(raw)
        if not m:
            continue
        file_path = m.group(1).strip()
        claim = m.group(2).strip()
        out.append(Finding(
            finding_id=hash_finding(file_path, claim),
            source_instance=source,
            file_path=file_path,
            claim=claim,
        ))
    return out


def hash_finding(file_path: str, claim: str) -> str:
    key = (file_path + "::" + claim).encode("utf-8")
    return hashlib.sha1(key).hexdigest()[:FINDING_HASH_LEN]


# --- Merging ---------------------------------------------------------------

def merge_findings(a: list[Finding], b: list[Finding]) -> list[Finding]:
    """Hash-merge findings from A and B.

    Same finding_id → single Finding with source="both" and initial_stance
    {A:accept,B:accept} (both raised it independently → automatic consensus).
    """
    by_id: dict[str, Finding] = {}
    for f in a:
        f.initial_stance = {"A": "accept", "B": "defend"}  # placeholder; B may dispute
        by_id[f.finding_id] = f
    for f in b:
        if f.finding_id in by_id:
            existing = by_id[f.finding_id]
            existing.source_instance = "both"
            existing.initial_stance = {"A": "accept", "B": "accept"}
            existing.terminal_state = "agreed"
            existing.final_stance = dict(existing.initial_stance)
        else:
            f.initial_stance = {"A": "defend", "B": "accept"}
            by_id[f.finding_id] = f
    return list(by_id.values())


# --- Stance resolution -----------------------------------------------------

def _normalize_pair(a: str, b: str) -> tuple[Stance, Stance]:
    a_n = a.lower() if a in VALID_STANCES else "defend"
    b_n = b.lower() if b in VALID_STANCES else "defend"
    return (a_n, b_n)  # type: ignore[return-value]


def resolve_stance_pair(a: Stance, b: Stance) -> tuple[TerminalState, bool]:
    pair = _normalize_pair(a, b)
    return INITIAL_TRANSITIONS.get(pair, ("disputed", False))


# A subagent_invoker signature: given (finding, opponent_stance) return new stance.
SubagentInvoker = Callable[[Finding, Stance], Stance]


def _default_invoker(finding: Finding, opponent_stance: Stance) -> Stance:
    """Deterministic stand-in when no real subagent is wired in.

    Models a "stubborn proposer": if its current stance is defend or dismiss,
    it sticks. If it was accept/concede and the opponent now defends, it
    upgrades to concede (caveat) but doesn't flip to defend. This keeps
    test behavior predictable without an LLM.
    """
    current = finding.final_stance or finding.initial_stance
    # We don't know which side this invoker speaks for here; the caller
    # passes opponent_stance, and we keep stance stable. Tests override this.
    last = "defend"
    for v in current.values():
        last = v
        break
    if last in ("defend", "dismiss"):
        return last  # type: ignore[return-value]
    if opponent_stance == "defend":
        return "concede"
    return "accept"


def resolve_finding(
    finding: Finding,
    max_rounds: int,
    invoker_a: SubagentInvoker,
    invoker_b: SubagentInvoker,
) -> int:
    """Drive a single finding through up to max_rounds.

    Returns the number of rounds actually executed for this finding.
    Mutates finding.final_stance and finding.terminal_state.
    """
    if not finding.initial_stance:
        finding.initial_stance = {"A": "accept", "B": "defend"}
    finding.final_stance = dict(finding.initial_stance)

    a_stance: Stance = finding.final_stance.get("A", "defend")  # type: ignore[assignment]
    b_stance: Stance = finding.final_stance.get("B", "defend")  # type: ignore[assignment]
    terminal, needs_round = resolve_stance_pair(a_stance, b_stance)

    if not needs_round:
        finding.terminal_state = terminal
        return 0

    rounds_used = 0
    while needs_round and rounds_used < max_rounds:
        rounds_used += 1
        new_a = invoker_a(finding, b_stance)
        new_b = invoker_b(finding, a_stance)
        a_stance, b_stance = _normalize_pair(new_a, new_b)
        finding.final_stance = {"A": a_stance, "B": b_stance}
        terminal, needs_round = resolve_stance_pair(a_stance, b_stance)

    if needs_round:
        # Budget exhausted while still pending → mark disputed
        finding.terminal_state = "disputed"
    else:
        finding.terminal_state = terminal
    return rounds_used


# --- Verdict derivation ----------------------------------------------------

def derive_verdict(findings: list[Finding]) -> Verdict:
    if not findings:
        return "consensus"
    has_disputed = any(f.terminal_state == "disputed" for f in findings)
    if has_disputed:
        return "divergence"
    sources = {f.source_instance for f in findings if f.terminal_state == "agreed"}
    # If every agreed finding came from "both" → pure consensus.
    if sources <= {"both"}:
        return "consensus"
    # Otherwise A and B each contributed distinct valid points → hybrid.
    return "hybrid"


# --- Rendering -------------------------------------------------------------

def render_consensus(findings: list[Finding]) -> str:
    lines = ["# Consensus Design", "", "## Findings"]
    for f in findings:
        if f.terminal_state == "agreed":
            tag = "(both)" if f.source_instance == "both" else f"(from {f.source_instance})"
            lines.append(f"- `{f.file_path}`: {f.claim} {tag}")
    return "\n".join(lines) + "\n"


def render_hybrid(findings: list[Finding]) -> str:
    lines = ["# Hybrid Design", "",
             "Both proposers raised valid, non-overlapping points.", "",
             "## Findings"]
    for f in findings:
        if f.terminal_state == "agreed":
            tag = "(both)" if f.source_instance == "both" else f"(from {f.source_instance})"
            lines.append(f"- `{f.file_path}`: {f.claim} {tag}")
    return "\n".join(lines) + "\n"


def render_divergence(findings: list[Finding]) -> str:
    lines = ["# Divergence Report", "",
             "The proposers could not reach consensus on the following findings.",
             "Escalating to user.", "",
             "## Disputed"]
    for f in findings:
        if f.terminal_state == "disputed":
            lines.append(f"- `{f.file_path}`: {f.claim}")
            lines.append(f"  - A: {f.final_stance.get('A','?')}, "
                         f"B: {f.final_stance.get('B','?')}")
    lines.extend(["", "## Agreed (carry forward)"])
    for f in findings:
        if f.terminal_state == "agreed":
            lines.append(f"- `{f.file_path}`: {f.claim}")
    return "\n".join(lines) + "\n"


# --- Path resolution -------------------------------------------------------

def _load_proposal(path_or_topic: str) -> str:
    """Load a proposal body. Accepts:
       - file:<path>   → read file
       - <sdlc-path>   → read from .sdlc/state/<change>/ (passed as file path)
       - any other string starting with '#' is treated as raw markdown.
    """
    if path_or_topic.startswith("file:"):
        from pathlib import Path
        return Path(path_or_topic[5:]).read_text(encoding="utf-8")
    # If it looks like a file path that exists, read it; else treat as raw.
    from pathlib import Path
    p = Path(path_or_topic)
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8")
    return path_or_topic


# --- Public entrypoint -----------------------------------------------------

def run_debate(
    change_name: str,
    proposal_a_path: str,
    proposal_b_path: str,
    tier: str = "medium",
    max_rounds: Optional[int] = None,
    invoker_a: Optional[SubagentInvoker] = None,
    invoker_b: Optional[SubagentInvoker] = None,
) -> DebateResult:
    """Run the debate state machine and return a DebateResult.

    `change_name` is passed through for context but not used by pure logic.
    """
    started = time.monotonic()
    if tier not in VALID_TIERS:
        tier = "medium"
    if max_rounds is None:
        max_rounds = HIGH_TIER_ROUNDS if tier == "high" else MEDIUM_TIER_ROUNDS
    invoker_a = invoker_a or _default_invoker
    invoker_b = invoker_b or _default_invoker

    md_a = _load_proposal(proposal_a_path)
    md_b = _load_proposal(proposal_b_path)

    findings_a = extract_findings(md_a, "A")
    findings_b = extract_findings(md_b, "B")
    merged = merge_findings(findings_a, findings_b)

    rounds_total = 0
    for f in merged:
        if f.terminal_state == "pending" or f.terminal_state == "":
            f.terminal_state = "pending"
        if f.terminal_state == "agreed":
            continue
        rounds_total = max(rounds_total, resolve_finding(f, max_rounds, invoker_a, invoker_b))

    verdict = derive_verdict(merged)
    elapsed_ms = int((time.monotonic() - started) * 1000)

    if verdict == "consensus":
        consensus = render_consensus(merged)
        return DebateResult(verdict, rounds_total, merged, consensus, None, elapsed_ms)
    if verdict == "hybrid":
        hybrid = render_hybrid(merged)
        return DebateResult(verdict, rounds_total, merged, hybrid, None, elapsed_ms)
    # divergence
    report = render_divergence(merged)
    return DebateResult(verdict, rounds_total, merged, None, report, elapsed_ms)


__all__ = [
    "Finding",
    "DebateResult",
    "run_debate",
    "extract_findings",
    "hash_finding",
    "merge_findings",
    "resolve_finding",
    "resolve_stance_pair",
    "derive_verdict",
    "INITIAL_TRANSITIONS",
    "MEDIUM_TIER_ROUNDS",
    "HIGH_TIER_ROUNDS",
    "MEDIUM_TIER_WALL_MS",
    "HIGH_TIER_WALL_MS",
]
