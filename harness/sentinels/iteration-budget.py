#!/usr/bin/env python3
"""
iteration-budget.py — v7.3 Auto-loop Sentinel.

Fires on SubagentStop. Handles 4 failure-mode triggers:
  P0: sdd-verify FAIL          → auto-loop apply→verify
  P1: code-reviewer findings   → auto-loop fix→re-review
  P2a: test/lint fail in apply → auto-loop fix→re-run
  P2b: sdd-verify-diff blocked → auto-loop per blocker
  P2c: global ceiling          → 6 fix→verify cycles / 60-min watchdog per change

Also retains the original status:partial tracking (backward-compatible).

Never blocks. Exit 0 always (graceful degradation).
Stop signals (any one halts all looping):
  - 2 consecutive iterations with identical failure signature → ESCALATE
  - 2 consecutive iterations with file_diff_count == 0      → ESCALATE
  - Per-tier × per-trigger budget exhausted
  - Global ceiling exceeded
  - error_class == permanent                                  → ESCALATE immediately
  - tier == critical                                          → ESCALATE immediately
  - RALPH_AUTO=false env var                                  → disable auto-looping
"""

import fcntl
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

JSON_FENCE_RE = re.compile(r"```(?:json)?\s*\n(\{.*?\})\s*\n```", re.DOTALL)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_TIER = "medium"
VALID_TIERS = ("trivial", "medium", "high", "critical")
VALID_STATUS = ("done", "partial", "blocked", "needs_specialist")
VALID_ERROR_CLASS = ("transient", "permanent", "unknown")

IDENTICAL_SIG_STOP = 2   # consecutive identical sig_hashes
ZERO_PROGRESS_STOP = 2   # consecutive attempts with file_diff_count == 0

GLOBAL_MAX_ITER = 6  # 6 fix→verify cycles. reflection loops are typically capped at ~3; we allow slightly more for the multi-phase SDD loop. NOT 25 — that's for tool-calls, our unit is a full cycle.
GLOBAL_MAX_WALL_MINUTES = 60  # watchdog backstop for a hung iteration, NOT a co-equal budget pillar

# Trigger identifiers (map verdict/status → loop trigger key)
TRIGGER_VERIFY_FAIL = "verify-fail"
TRIGGER_CODE_REVIEW = "code-review-findings"
TRIGGER_VERIFY_DIFF = "verify-diff-blocked"
TRIGGER_TEST_FAIL   = "apply-test-fail"

# Fallback loop budgets when TOML is absent.
FALLBACK_LOOP_BUDGETS: dict[str, dict[str, int]] = {
    TRIGGER_VERIFY_FAIL: {"trivial": 2, "medium": 4, "high": 6, "critical": 0},
    TRIGGER_CODE_REVIEW: {"trivial": 1, "medium": 2, "high": 3, "critical": 0},
    TRIGGER_VERIFY_DIFF: {"trivial": 1, "medium": 2, "high": 3, "critical": 0},
    TRIGGER_TEST_FAIL:   {"trivial": 3, "medium": 5, "high": 7, "critical": 0},
}

# Fallback legacy per-phase partial budgets (unchanged from v7.1).
FALLBACK_BUDGETS: dict[str, dict[str, int]] = {
    "sdd-explore":  {"trivial": 1, "medium": 2, "high": 3},
    "sdd-propose":  {"trivial": 1, "medium": 2, "high": 3},
    "sdd-spec":     {"trivial": 1, "medium": 3, "high": 5},
    "sdd-design":   {"trivial": 1, "medium": 3, "high": 5},
    "sdd-tasks":    {"trivial": 1, "medium": 2, "high": 3},
    "sdd-apply":    {"trivial": 2, "medium": 4, "high": 6},
    "sdd-verify":   {"trivial": 1, "medium": 3, "high": 5},
    "sdd-archive":  {"trivial": 1, "medium": 1, "high": 1},
    "_default":     {"trivial": 1, "medium": 3, "high": 5},
}
FALLBACK_TEMPLATE = (
    "Previous invocation returned status=partial. Reason: {reason}. "
    "Attempt {n}/{max}. Please address and emit status=done."
)

ENVELOPE_STATUS_RE = re.compile(
    r'"?status"?\s*[:=]\s*"?(done|partial|blocked|needs_specialist)"?', re.IGNORECASE
)
PARTIAL_REASON_RE = re.compile(
    r'"?reason"?\s*[:=]\s*"([^"]+)"', re.IGNORECASE
)


# ---------------------------------------------------------------------------
# Real SubagentStop payload normalization
#
# Claude Code's real SubagentStop payload does NOT contain agent_name, status,
# verdict, or failure_signature directly.  The actual fields are:
#   agent_type          — type name (e.g. "code-reviewer", "sdd-verify")
#   agent_transcript_path — direct path to subagent JSONL
#   last_assistant_message — raw text of final agent response (envelope lives here)
#
# These three helpers extract the SubagentResponseV1 envelope so all existing
# parse_* functions (which look at payload.get("status") etc.) work once the
# envelope fields are merged back into the payload dict.
# ---------------------------------------------------------------------------

TRANSCRIPT_TAIL_LINES = 400


def _extract_json_from_text(text: str) -> dict:
    """Return the first fenced-JSON dict found in text, or {} if none."""
    if not text:
        return {}
    m = JSON_FENCE_RE.search(text)
    if m:
        try:
            result = json.loads(m.group(1))
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass
    # Fallback: the whole text might be a bare JSON object.
    try:
        result = json.loads(text.strip())
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass
    return {}


def _extract_envelope_from_transcript(transcript_path: str) -> dict:
    """Parse a subagent JSONL transcript and return the last assistant envelope."""
    if not transcript_path:
        return {}
    p = Path(transcript_path)
    if not p.exists():
        return {}
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return {}
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
            parsed = _extract_json_from_text(block.get("text", ""))
            if parsed and "status" in parsed:
                return parsed
    return {}


def _extract_envelope_from_payload(payload: dict) -> dict:
    """Return the SubagentResponseV1 envelope from any payload shape.

    Priority:
    1. last_assistant_message (direct field — real payload, no file I/O)
    2. agent_transcript_path  (direct subagent JSONL path — real payload)
    3. transcript_path        (parent session JSONL — fallback)
    4. envelope dict / status at top level (synthetic/test payloads)
    """
    # 1. last_assistant_message is the fastest path — Claude Code embeds the
    #    agent's final text response directly in the SubagentStop payload.
    last_msg = payload.get("last_assistant_message") or ""
    if last_msg:
        parsed = _extract_json_from_text(last_msg)
        if parsed and "status" in parsed:
            return parsed

    # 2. agent_transcript_path directly points to the subagent JSONL.
    for key in ("agent_transcript_path", "transcript_path"):
        path = payload.get(key) or ""
        if path:
            parsed = _extract_envelope_from_transcript(path)
            if parsed:
                return parsed

    # 3. Legacy: synthetic/test payloads embed the envelope as a nested dict
    #    or put fields directly at the top level.
    env = payload.get("envelope")
    if isinstance(env, dict):
        return env

    return {}


# ---------------------------------------------------------------------------
# TOML loading (Python 3.11+ stdlib tomllib; fallback to tomli for 3.9/3.10)
# ---------------------------------------------------------------------------

def _load_toml(path: Path) -> dict:
    try:
        import tomllib  # type: ignore[import-not-found]  # Python 3.11+
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except ImportError:
        pass
    try:
        import tomli  # type: ignore[import-not-found]
        with path.open("rb") as fh:
            return tomli.load(fh)
    except ImportError:
        pass
    return {}


# ---------------------------------------------------------------------------
# Repo root
# ---------------------------------------------------------------------------

def find_repo_root(start: Optional[Path] = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ".claude" / "harness").is_dir():
            return candidate
    return here


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_budget_config(repo_root: Path) -> dict:
    cfg_path = repo_root / ".claude" / "harness" / "sentinels" / "iteration-budget.toml"
    if not cfg_path.exists():
        # Fallback path (Agent007 mirror location)
        cfg_path = repo_root / ".claude" / "harness" / "iteration-budget.toml"
    if not cfg_path.exists():
        return {
            "budgets": FALLBACK_BUDGETS,
            "loop_budgets": FALLBACK_LOOP_BUDGETS,
            "template": FALLBACK_TEMPLATE,
            "participants_allow": None,
            "participants_deny": set(),
            "global_max_iter": GLOBAL_MAX_ITER,
            "global_max_wall_minutes": GLOBAL_MAX_WALL_MINUTES,
        }
    fallback = {
        "budgets": FALLBACK_BUDGETS,
        "loop_budgets": FALLBACK_LOOP_BUDGETS,
        "template": FALLBACK_TEMPLATE,
        "participants_allow": None,
        "participants_deny": set(),
        "global_max_iter": GLOBAL_MAX_ITER,
        "global_max_wall_minutes": GLOBAL_MAX_WALL_MINUTES,
    }
    strict = os.environ.get("RALPH_STRICT_CONFIG", "").strip().lower() == "true"

    def _warn_or_raise(reason: str):
        msg = f"[budget] WARN: invalid TOML config at {cfg_path}: {reason}; using fallback"
        if strict:
            raise ValueError(msg)
        print(msg, file=sys.stderr)

    try:
        data = _load_toml(cfg_path)
    except Exception as exc:
        _warn_or_raise(f"parse error: {exc}")
        return fallback

    if not isinstance(data, dict):
        _warn_or_raise("top-level is not a table")
        return fallback

    # Validate expected top-level keys exist (at least one of the loop-config
    # keys must be present and well-formed; otherwise the file is unusable).
    required_top = ("loops", "global")
    missing = [k for k in required_top if k not in data]
    if missing:
        _warn_or_raise(f"missing top-level keys: {missing}")
        return fallback

    if not isinstance(data.get("loops"), dict):
        _warn_or_raise("[loops] must be a table")
        return fallback
    if not isinstance(data.get("global"), dict):
        _warn_or_raise("[global] must be a table")
        return fallback

    try:
        budgets = data.get("budgets", FALLBACK_BUDGETS) or FALLBACK_BUDGETS

        loops_raw = data.get("loops", {}) or {}
        loop_budgets: dict[str, dict[str, int]] = {}
        for trigger_key in (
            TRIGGER_VERIFY_FAIL, TRIGGER_CODE_REVIEW,
            TRIGGER_VERIFY_DIFF, TRIGGER_TEST_FAIL,
        ):
            raw = loops_raw.get(trigger_key, FALLBACK_LOOP_BUDGETS[trigger_key])
            loop_budgets[trigger_key] = {
                k: int(v) for k, v in raw.items()
            }

        template = (
            (data.get("feedback") or {}).get("template", FALLBACK_TEMPLATE)
        )

        participants = data.get("participants", {}) or {}
        allow_list = participants.get("allow") or None  # None = open (all allowed)
        deny_set = set(participants.get("deny") or [])

        glob = data.get("global", {}) or {}
        return {
            "budgets": budgets,
            "loop_budgets": loop_budgets,
            "template": template,
            "participants_allow": allow_list,
            "participants_deny": deny_set,
            "global_max_iter": int(glob.get("max_iterations_per_change", GLOBAL_MAX_ITER)),
            "global_max_wall_minutes": float(glob.get("max_wall_clock_minutes", GLOBAL_MAX_WALL_MINUTES)),
        }
    except Exception as exc:
        _warn_or_raise(f"schema error: {exc}")
        return fallback


def get_budget(cfg: dict, agent_name: str, tier: str) -> int:
    budgets = cfg["budgets"]
    phase_cfg = (
        budgets.get(agent_name)
        or budgets.get("_default")
        or FALLBACK_BUDGETS["_default"]
    )
    return int(phase_cfg.get(tier, phase_cfg.get(DEFAULT_TIER, 3)))


def get_loop_budget(cfg: dict, trigger: str, tier: str) -> int:
    loop_budgets = cfg.get("loop_budgets", FALLBACK_LOOP_BUDGETS)
    trigger_cfg = loop_budgets.get(trigger, FALLBACK_LOOP_BUDGETS.get(trigger, {}))
    return int(trigger_cfg.get(tier, trigger_cfg.get(DEFAULT_TIER, 2)))


# ---------------------------------------------------------------------------
# Participant filtering
# ---------------------------------------------------------------------------

def is_participant(cfg: dict, agent_name: str) -> bool:
    """Return True when agent_name should participate in loop budgets."""
    deny = cfg.get("participants_deny", set())
    if agent_name in deny:
        return False
    allow = cfg.get("participants_allow")
    if allow is None:
        return True  # open list — everyone not denied participates
    return agent_name in allow


# ---------------------------------------------------------------------------
# Triage lookup
# ---------------------------------------------------------------------------

def read_triage_tier(repo_root: Path, change_name: str) -> Optional[str]:
    triage_path = repo_root / ".sdlc" / "state" / change_name / "triage.json"
    if not triage_path.is_file():
        return None
    try:
        data = json.loads(triage_path.read_text(encoding="utf-8"))
        tier = data.get("triage_tier")
        if tier in VALID_TIERS:
            return tier
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Change-name resolution
# ---------------------------------------------------------------------------

def resolve_change_name(payload: dict, repo_root: Path) -> str:
    name = (
        payload.get("change_name")
        or payload.get("change")
        or os.environ.get("SDD_CHANGE_NAME", "")
    )
    if name:
        return name
    pointer = repo_root / ".sdlc" / "state" / "active-change.txt"
    if pointer.is_file():
        try:
            return pointer.read_text(encoding="utf-8").strip()
        except Exception:
            return ""
    return ""


# ---------------------------------------------------------------------------
# Envelope parsing
# ---------------------------------------------------------------------------

def parse_envelope_status(payload: dict) -> Optional[str]:
    status = payload.get("status") or (payload.get("envelope") or {}).get("status")
    if isinstance(status, str) and status.lower() in VALID_STATUS:
        return status.lower()
    transcript = payload.get("transcript") or payload.get("subagent_output") or ""
    if isinstance(transcript, str) and transcript:
        m = ENVELOPE_STATUS_RE.search(transcript)
        if m:
            return m.group(1).lower()
    return None


def parse_partial_reason(payload: dict) -> str:
    reason = (
        payload.get("reason")
        or (payload.get("envelope") or {}).get("reason")
    )
    if isinstance(reason, str) and reason.strip():
        return reason.strip()
    transcript = payload.get("transcript") or payload.get("subagent_output") or ""
    if isinstance(transcript, str):
        m = PARTIAL_REASON_RE.search(transcript)
        if m:
            return m.group(1).strip()
    return "unspecified"


def parse_error_class(payload: dict) -> str:
    ec = payload.get("error_class") or (payload.get("envelope") or {}).get("error_class")
    if isinstance(ec, str) and ec.lower() in VALID_ERROR_CLASS:
        return ec.lower()
    return "unknown"


def parse_verdict(payload: dict) -> Optional[str]:
    """Extract verdict field: PASS | WARN | FAIL | findings | blocked | test_fail."""
    v = payload.get("verdict") or (payload.get("envelope") or {}).get("verdict")
    if isinstance(v, str):
        return v.strip()
    return None


def parse_failure_signature(payload: dict, reason: str) -> str:
    """Return the failure_signature from the envelope, or derive from reason."""
    sig = payload.get("failure_signature") or (payload.get("envelope") or {}).get("failure_signature")
    if isinstance(sig, str) and sig.strip():
        raw = sig.strip()
    else:
        raw = reason
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


def parse_file_changes(payload: dict) -> int:
    """Return file_changes integer, or -1 if not present/parseable. Uses is-None checks to preserve 0."""
    def _get(d, *keys):
        for k in keys:
            v = d.get(k)
            if v is not None:
                return v
        return None

    val = _get(payload, "file_changes", "file_diff_count")
    if val is None:
        env = payload.get("envelope") or {}
        val = _get(env, "file_changes", "file_diff_count")
    if val is None:
        return -1
    try:
        return int(val)
    except (TypeError, ValueError):
        return -1  # -1 = unknown (not 0-progress)


def classify_trigger(payload: dict, agent_name: str) -> Optional[str]:
    """
    Return the loop trigger key based on verdict + agent_name.
    Returns None if this doesn't map to an auto-loop trigger.
    """
    verdict = parse_verdict(payload)
    status = parse_envelope_status(payload)
    v = (verdict or "").upper()

    if agent_name == "sdd-verify" and v == "FAIL":
        return TRIGGER_VERIFY_FAIL
    if agent_name == "code-reviewer" and verdict in ("findings", "FINDINGS"):
        return TRIGGER_CODE_REVIEW
    if agent_name == "sdd-verify-diff" and (v == "BLOCKED" or status == "blocked"):
        return TRIGGER_VERIFY_DIFF
    if agent_name == "sdd-apply" and (v == "TEST_FAIL" or status == "blocked"):
        return TRIGGER_TEST_FAIL
    return None


# ---------------------------------------------------------------------------
# State directory helpers
# ---------------------------------------------------------------------------

def state_dir(repo_root: Path, change_name: str) -> Path:
    out = repo_root / ".sdlc" / "state" / change_name
    out.mkdir(parents=True, exist_ok=True)
    return out


def _atomic_append_jsonl(path: Path, row: dict) -> None:
    """Append a JSON row to a JSONL file under an exclusive POSIX file lock.

    Prevents interleaved bytes when parallel SubagentStop hooks fire — a
    single write() is only atomic when < PIPE_BUF (4096B), which is not
    guaranteed for sig rows.
    """
    line = json.dumps(row, sort_keys=True) + "\n"
    with path.open("a", encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            fh.write(line)
            fh.flush()
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


class _file_lock:
    """Exclusive cross-process lock for read-modify-write critical sections.

    Uses a sidecar ``.lock`` file so the locked target can be replaced via
    ``os.replace`` without invalidating the lock fd.
    """

    def __init__(self, path: Path) -> None:
        self._lock_path = path.with_suffix(path.suffix + ".lock")
        self._fh = None

    def __enter__(self):
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self._lock_path.open("a+")
        fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        if self._fh is not None:
            try:
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
            finally:
                self._fh.close()
                self._fh = None
        return False


def _atomic_write_json(path: Path, data: dict) -> None:
    """Atomically write a JSON snapshot via tmp file + os.replace.

    Prevents truncated/empty files if the process crashes mid-write.
    """
    # Per-process unique tmp suffix prevents collisions when multiple
    # processes write concurrently — each writes its own tmp, then the
    # rename is atomic and "last writer wins" semantically.
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    payload = json.dumps(data, indent=2, sort_keys=True) + "\n"
    with tmp.open("w", encoding="utf-8") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(str(tmp), str(path))


# ---------------------------------------------------------------------------
# iteration-log.jsonl (legacy — backward compatible)
# ---------------------------------------------------------------------------

def count_invocations(repo_root: Path, change_name: str, agent_name: str) -> int:
    log_path = state_dir(repo_root, change_name) / "iteration-log.jsonl"
    if not log_path.is_file():
        return 0
    n = 0
    try:
        for line in log_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue
            if row.get("agent") == agent_name:
                n += 1
    except Exception:
        return 0
    return n


def append_iteration_log(
    repo_root: Path, change_name: str, agent_name: str,
    status: str, tier: str, attempt: int, budget: int,
) -> None:
    log_path = state_dir(repo_root, change_name) / "iteration-log.jsonl"
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "agent": agent_name,
        "status": status,
        "tier": tier,
        "attempt": attempt,
        "budget": budget,
    }
    _atomic_append_jsonl(log_path, row)


# ---------------------------------------------------------------------------
# failure-signatures.jsonl
# ---------------------------------------------------------------------------

def append_failure_signature(
    repo_root: Path, change_name: str,
    phase: str, attempt: int, sig_hash: str,
    sig_excerpt: str, file_diff_count: int,
) -> None:
    sig_path = state_dir(repo_root, change_name) / "failure-signatures.jsonl"
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "attempt": attempt,
        "sig_hash": sig_hash,
        "sig_excerpt": sig_excerpt[:120],
        "file_diff_count": file_diff_count,
    }
    _atomic_append_jsonl(sig_path, row)


def read_failure_signatures(repo_root: Path, change_name: str) -> list[dict]:
    sig_path = state_dir(repo_root, change_name) / "failure-signatures.jsonl"
    if not sig_path.is_file():
        return []
    raw_lines = [
        l.strip() for l in sig_path.read_text(encoding="utf-8").splitlines() if l.strip()
    ]
    rows: list[dict] = []
    for idx, line in enumerate(raw_lines):
        try:
            rows.append(json.loads(line))
        except Exception:
            if idx == len(raw_lines) - 1:
                # Corrupt LAST line — likely a partial write from a crashed
                # parallel append. Fail CLOSED: synthesize a row whose
                # sig_hash matches the previous row so the same-signature
                # stop-signal trips instead of resetting the counter.
                print(
                    f"[budget] WARN: corrupted JSONL tail in {sig_path}, "
                    f"treating as identical-signature",
                    file=sys.stderr,
                )
                if rows:
                    prev = rows[-1]
                    rows.append({
                        "ts": datetime.now(timezone.utc).isoformat(),
                        "phase": prev.get("phase", "unknown"),
                        "attempt": int(prev.get("attempt", 0)) + 1,
                        "sig_hash": prev.get("sig_hash"),
                        "sig_excerpt": "[corrupted-tail]",
                        "file_diff_count": prev.get("file_diff_count", 0),
                    })
            # Mid-file malformed rows are skipped (legacy behavior — these
            # cannot be partial writes since later writes succeeded).
            continue
    return rows


def same_signature_count(log: list[dict]) -> int:
    """Return the count of consecutive identical sig_hashes at the tail of log."""
    if not log:
        return 0
    tail_hash = log[-1].get("sig_hash")
    if tail_hash is None:
        return 0
    count = 0
    for row in reversed(log):
        if row.get("sig_hash") == tail_hash:
            count += 1
        else:
            break
    return count


def zero_progress_count(log: list[dict]) -> int:
    """Return the count of consecutive attempts with file_diff_count == 0 at the tail."""
    if not log:
        return 0
    count = 0
    for row in reversed(log):
        fdc = row.get("file_diff_count")
        if fdc == 0:
            count += 1
        else:
            break
    return count


# ---------------------------------------------------------------------------
# loop-budget.json (running counters per change)
# ---------------------------------------------------------------------------

def read_loop_budget(repo_root: Path, change_name: str) -> dict:
    path = state_dir(repo_root, change_name) / "loop-budget.json"
    if not path.is_file():
        return {
            "global_iter": 0,
            "per_trigger": {
                TRIGGER_VERIFY_FAIL: 0,
                TRIGGER_CODE_REVIEW: 0,
                TRIGGER_VERIFY_DIFF: 0,
                TRIGGER_TEST_FAIL: 0,
            },
            "first_ts": datetime.now(timezone.utc).isoformat(),
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        # Ensure all trigger keys are present
        pt = data.setdefault("per_trigger", {})
        for t in (TRIGGER_VERIFY_FAIL, TRIGGER_CODE_REVIEW, TRIGGER_VERIFY_DIFF, TRIGGER_TEST_FAIL):
            pt.setdefault(t, 0)
        return data
    except Exception:
        return {
            "global_iter": 0,
            "per_trigger": {
                TRIGGER_VERIFY_FAIL: 0,
                TRIGGER_CODE_REVIEW: 0,
                TRIGGER_VERIFY_DIFF: 0,
                TRIGGER_TEST_FAIL: 0,
            },
            "first_ts": datetime.now(timezone.utc).isoformat(),
        }


def write_loop_budget(repo_root: Path, change_name: str, data: dict) -> None:
    path = state_dir(repo_root, change_name) / "loop-budget.json"
    _atomic_write_json(path, data)


def increment_loop_budget(
    repo_root: Path, change_name: str, trigger: Optional[str],
) -> dict:
    """Increment global_iter and the per-trigger counter. Return updated data.

    The read-modify-write is serialised across processes via a sidecar lock
    so parallel SubagentStop hooks cannot lose increments.
    """
    lb_path = state_dir(repo_root, change_name) / "loop-budget.json"
    with _file_lock(lb_path):
        data = read_loop_budget(repo_root, change_name)
        data["global_iter"] = data.get("global_iter", 0) + 1
        if trigger:
            data["per_trigger"][trigger] = data["per_trigger"].get(trigger, 0) + 1
        write_loop_budget(repo_root, change_name, data)
    return data


def global_iter_count(repo_root: Path, change_name: str) -> int:
    return read_loop_budget(repo_root, change_name).get("global_iter", 0)


# Matches sentinel-hardening-pattern.md (ring buffer of ~50). Sized for parallel
# fan-out: a multi-domain apply wave fires a burst of SubagentStop events; a cap
# of 10 could evict an event ID mid-burst and re-admit it as new (replay).
SEEN_EVENTS_CAP = 50


def compute_event_id(
    payload: dict, agent_name: str, sig_hash: str, attempt: int,
) -> str:
    """Stable per-event ID for idempotency.

    Prefers explicit ``invocation_id`` from the payload (or its envelope).
    Falls back to a hash of (agent, sig_hash, file_changes, status, verdict,
    attempt) — attempt distinguishes legitimate sequential invocations from
    a re-fired hook, since the iteration-log only advances on successful
    processing.
    """
    iid = (
        payload.get("invocation_id")
        or (payload.get("envelope") or {}).get("invocation_id")
    )
    if isinstance(iid, str) and iid.strip():
        return iid.strip()
    fc = payload.get("file_changes")
    if fc is None:
        fc = (payload.get("envelope") or {}).get("file_changes")
    status = parse_envelope_status(payload) or ""
    verdict = parse_verdict(payload) or ""
    raw = f"{agent_name}|{sig_hash}|{fc}|{status}|{verdict}|{attempt}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def check_and_record_event(
    repo_root: Path, change_name: str, event_id: str,
) -> bool:
    """Return True if this is a new event (record it), False if duplicate.

    Reads loop-budget.json, checks seen_events, and writes back the updated
    list (capped at SEEN_EVENTS_CAP). Mutation is performed via the atomic
    write helper so a concurrent crash cannot corrupt the snapshot.
    """
    lb_path = state_dir(repo_root, change_name) / "loop-budget.json"
    with _file_lock(lb_path):
        data = read_loop_budget(repo_root, change_name)
        seen = data.get("seen_events") or []
        if event_id in seen:
            return False
        seen.append(event_id)
        if len(seen) > SEEN_EVENTS_CAP:
            seen = seen[-SEEN_EVENTS_CAP:]
        data["seen_events"] = seen
        write_loop_budget(repo_root, change_name, data)
    return True


def wall_minutes_elapsed(loop_data: dict) -> float:
    first_ts_str = loop_data.get("first_ts")
    if not first_ts_str:
        return 0.0
    try:
        first_ts = datetime.fromisoformat(first_ts_str)
        now = datetime.now(timezone.utc)
        return (now - first_ts).total_seconds() / 60.0
    except Exception:
        # Fail CLOSED: corrupted first_ts must trip the wall-clock ceiling so
        # the change escalates instead of silently disabling the limit.
        print(
            "[budget] WARN: corrupted first_ts in loop-budget.json, "
            "treating wall-clock as exceeded",
            file=sys.stderr,
        )
        return float("inf")


# ---------------------------------------------------------------------------
# Output envelopes
# ---------------------------------------------------------------------------

def write_feedback_envelope(
    repo_root: Path, change_name: str, agent_name: str,
    attempt: int, message: str,
) -> Path:
    feedback_dir = state_dir(repo_root, change_name) / "feedback"
    feedback_dir.mkdir(parents=True, exist_ok=True)
    out_path = feedback_dir / f"{agent_name}-attempt-{attempt}.json"
    envelope = {
        "behavior": "deny",
        "message": message,
        "ts": datetime.now(timezone.utc).isoformat(),
        "for_agent": agent_name,
        "change": change_name,
    }
    _atomic_write_json(out_path, envelope)
    return out_path


def write_escalation(
    repo_root: Path, change_name: str, agent_name: str,
    attempts: int, budget: int, tier: str, reason: str,
    escalation_reason: str = "iteration_budget_exhausted",
) -> Path:
    out_path = state_dir(repo_root, change_name) / "escalation.json"
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "phase": agent_name,
        "reason": escalation_reason,
        "attempts": attempts,
        "budget": budget,
        "tier": tier,
        "last_partial_reason": reason,
        "next_action_for_user": (
            "Review the partial state, decide whether to extend budget or abort change."
        ),
    }
    _atomic_write_json(out_path, payload)
    return out_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    # RALPH_AUTO=false disables all auto-looping.
    if os.environ.get("RALPH_AUTO", "").strip().lower() == "false":
        return 0

    try:
        raw = sys.stdin.read()
        payload: dict[str, Any] = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0  # never block on malformed input

    # --- Input layer: normalize real SubagentStop payload fields ---------------
    # Real payload: agent_type = type name (e.g. "code-reviewer"), agent_id = UUID.
    # Synthetic/test payloads: agent_name or subagent_type directly.
    agent_name: str = (
        payload.get("agent_name")        # synthetic/test payloads (legacy)
        or payload.get("subagent_type")  # synthetic/test payloads (legacy)
        or payload.get("agent_type")     # REAL field — type name like "code-reviewer"
        or ""
    )
    if not agent_name:
        return 0

    # Extract the SubagentResponseV1 envelope and merge its fields into payload
    # so all existing parse_* helpers (parse_envelope_status, parse_verdict, etc.)
    # work unchanged.  setdefault semantics: direct payload fields win; envelope
    # fields only fill in what is missing (preserves synthetic test behaviour).
    envelope = _extract_envelope_from_payload(payload)
    if envelope:
        for k in (
            "status", "verdict", "failure_signature", "error_class",
            "file_changes", "change_name", "reason", "recommended_specialist",
        ):
            if payload.get(k) is None and envelope.get(k) is not None:
                payload[k] = envelope[k]

    repo_root = find_repo_root()
    cfg = load_budget_config(repo_root)

    # Participant filter — gated by TOML allowlist.
    if not is_participant(cfg, agent_name):
        return 0

    change_name = resolve_change_name(payload, repo_root)
    if not change_name:
        return 0

    tier = read_triage_tier(repo_root, change_name) or DEFAULT_TIER
    envelope_status = parse_envelope_status(payload)
    error_class = parse_error_class(payload)
    verdict = parse_verdict(payload)
    reason = parse_partial_reason(payload)
    sig_input = payload.get("failure_signature") or (payload.get("envelope") or {}).get("failure_signature") or reason
    sig_hash = hashlib.sha256((sig_input or "").encode("utf-8")).hexdigest()[:12]
    file_diff_count = parse_file_changes(payload)

    # --- Legacy status:done tracking (no-op but log) -----------------------
    prior = count_invocations(repo_root, change_name, agent_name)
    attempt = prior + 1
    budget = get_budget(cfg, agent_name, tier)

    # --- Idempotency: dedupe double-fired SubagentStop events --------------
    # The Claude Code harness can re-fire SubagentStop for the same envelope
    # (transient retries, network blips). Without dedupe the counters would
    # double-increment and the feedback file would be overwritten.
    # ``attempt`` distinguishes legitimate sequential identical payloads
    # (iteration-log already advanced) from a true re-fire (it has not).
    event_id = compute_event_id(payload, agent_name, sig_hash, attempt)
    if not check_and_record_event(repo_root, change_name, event_id):
        print(f"[budget] duplicate event {event_id} ignored")
        return 0
    append_iteration_log(
        repo_root, change_name, agent_name,
        envelope_status or "unknown", tier, attempt, budget,
    )

    if envelope_status == "done":
        print(f"[budget] {change_name}/{agent_name} status=done invocation_count={attempt}")
        return 0

    if envelope_status == "needs_specialist":
        # Dispatch escalation — orchestrator must re-dispatch a specialist.
        # NOT a loop-gate halt: do not write a feedback envelope, do not
        # increment loop counters, do not classify as a trigger.
        rec = payload.get("recommended_specialist") or (payload.get("envelope") or {}).get("recommended_specialist") or "<unspecified>"
        print(f"[budget] {change_name}/{agent_name} status=needs_specialist recommended={rec} (pass-through, no loop)")
        return 0

    # --- Detect auto-loop trigger -------------------------------------------
    trigger = classify_trigger(payload, agent_name)

    # Determine if this is a failure that warrants loop logic.
    is_failure = (
        envelope_status in ("partial", "blocked")
        or trigger is not None
        or (verdict or "").upper() in ("FAIL", "BLOCKED", "FINDINGS")
    )

    if not is_failure:
        return 0

    # --- Write failure signature row ----------------------------------------
    if trigger is not None or envelope_status == "partial":
        try:
            append_failure_signature(
                repo_root, change_name, agent_name, attempt,
                sig_hash, sig_input[:120] if sig_input else "", file_diff_count,
            )
        except Exception as exc:
            print(f"[budget] sig_write_error={exc}", file=sys.stderr)

    sig_log = read_failure_signatures(repo_root, change_name)

    # --- Stop signals -------------------------------------------------------
    # 1. error_class == permanent → ESCALATE immediately, no loop.
    if error_class == "permanent":
        try:
            write_escalation(
                repo_root, change_name, agent_name, attempt, 0, tier,
                reason, escalation_reason="permanent_error_class",
            )
        except Exception as exc:
            print(f"[budget] escalation_write_error={exc}", file=sys.stderr)
        print(f"[budget] {change_name}/{agent_name} ESCALATED reason=permanent_error_class")
        return 0

    # 2. tier == critical → ESCALATE immediately.
    if tier == "critical":
        try:
            write_escalation(
                repo_root, change_name, agent_name, attempt, 0, tier,
                reason, escalation_reason="critical_tier_no_auto_loop",
            )
        except Exception as exc:
            print(f"[budget] escalation_write_error={exc}", file=sys.stderr)
        print(f"[budget] {change_name}/{agent_name} ESCALATED reason=critical_tier")
        return 0

    # 3. Same failure signature × 2 consecutive.
    if same_signature_count(sig_log) >= IDENTICAL_SIG_STOP:
        try:
            write_escalation(
                repo_root, change_name, agent_name, attempt, 0, tier,
                reason, escalation_reason="identical_failure_signature",
            )
        except Exception as exc:
            print(f"[budget] escalation_write_error={exc}", file=sys.stderr)
        print(
            f"[budget] {change_name}/{agent_name} ESCALATED reason=identical_failure_signature "
            f"sig_hash={sig_hash}"
        )
        return 0

    # 4. Zero progress × 2 consecutive.
    if zero_progress_count(sig_log) >= ZERO_PROGRESS_STOP:
        try:
            write_escalation(
                repo_root, change_name, agent_name, attempt, 0, tier,
                reason, escalation_reason="zero_progress",
            )
        except Exception as exc:
            print(f"[budget] escalation_write_error={exc}", file=sys.stderr)
        print(f"[budget] {change_name}/{agent_name} ESCALATED reason=zero_progress")
        return 0

    # --- Loop budget checks -------------------------------------------------
    if trigger is not None:
        # Increment counters BEFORE checking limits.
        loop_data = increment_loop_budget(repo_root, change_name, trigger)
        global_iter = loop_data["global_iter"]
        trigger_iter = loop_data["per_trigger"].get(trigger, 0)
        trigger_budget = get_loop_budget(cfg, trigger, tier)
        global_budget = cfg.get("global_max_iter", GLOBAL_MAX_ITER)

        # Global ceiling check.
        if global_iter >= global_budget:
            try:
                write_escalation(
                    repo_root, change_name, agent_name, global_iter,
                    global_budget, tier, reason,
                    escalation_reason="global_iteration_ceiling",
                )
            except Exception as exc:
                print(f"[budget] escalation_write_error={exc}", file=sys.stderr)
            print(
                f"[budget] {change_name}/{agent_name} ESCALATED reason=global_ceiling "
                f"global_iter={global_iter}/{global_budget}"
            )
            return 0

        # Wall-clock check.
        elapsed = wall_minutes_elapsed(loop_data)
        wall_limit = cfg.get("global_max_wall_minutes", GLOBAL_MAX_WALL_MINUTES)
        if elapsed >= wall_limit:
            try:
                write_escalation(
                    repo_root, change_name, agent_name, global_iter,
                    global_budget, tier, reason,
                    escalation_reason="wall_clock_exceeded",
                )
            except Exception as exc:
                print(f"[budget] escalation_write_error={exc}", file=sys.stderr)
            print(
                f"[budget] {change_name}/{agent_name} ESCALATED reason=wall_clock "
                f"elapsed_min={elapsed:.1f}/{wall_limit}"
            )
            return 0

        # Per-trigger budget check.
        if trigger_iter >= trigger_budget:
            try:
                write_escalation(
                    repo_root, change_name, agent_name, trigger_iter,
                    trigger_budget, tier, reason,
                    escalation_reason=f"trigger_budget_exhausted:{trigger}",
                )
            except Exception as exc:
                print(f"[budget] escalation_write_error={exc}", file=sys.stderr)
            print(
                f"[budget] {change_name}/{agent_name} EXHAUSTED trigger={trigger} "
                f"{trigger_iter}/{trigger_budget}"
            )
            return 0

        # Within budget — write feedback envelope.
        message = (
            f"Auto-loop trigger={trigger} tier={tier} "
            f"attempt={trigger_iter}/{trigger_budget}. {reason}"
        )
        try:
            write_feedback_envelope(
                repo_root, change_name, agent_name, trigger_iter, message
            )
        except Exception as exc:
            print(f"[budget] feedback_write_error={exc}", file=sys.stderr)
        print(
            f"[budget] {change_name}/{agent_name} trigger={trigger} "
            f"attempt={trigger_iter}/{trigger_budget} — re-invoke"
        )
        return 0

    # --- Legacy status:partial path (no trigger classified) ----------------
    if envelope_status == "partial":
        if attempt < budget:
            message = cfg["template"].format(reason=reason, n=attempt, max=budget)
            try:
                write_feedback_envelope(
                    repo_root, change_name, agent_name, attempt, message
                )
            except Exception as exc:
                print(f"[budget] feedback_write_error={exc}", file=sys.stderr)
            print(
                f"[budget] {change_name}/{agent_name} status=partial "
                f"attempt={attempt}/{budget} — re-invoke"
            )
            return 0

        # Exhausted.
        try:
            write_escalation(
                repo_root, change_name, agent_name, attempt, budget, tier,
                reason, escalation_reason="iteration_budget_exhausted",
            )
        except Exception as exc:
            print(f"[budget] escalation_write_error={exc}", file=sys.stderr)
        print(
            f"[budget] {change_name}/{agent_name} EXHAUSTED "
            f"{attempt}/{budget} — escalation_required"
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
