# Sentinel Hardening Pattern

> Distilled from V7.3 race-condition hardening (P1.1, 2026-05-27). Apply when writing any hook in `.claude/harness/sentinels/` that maintains persistent state under potentially-concurrent invocations.

## Context

Sentinels fire on `SubagentStop`, `PostToolUse`, `Stop` — events that CAN occur concurrently in real V7 workflows (parallel subagent dispatches via Agent tool, `dispatching-parallel-agents`, ralph-loop overnight, etc.). Sentinel state must survive concurrency, partial writes, and double-fires.

## Mandatory hardening checklist

When a sentinel reads or writes any state file (`.sdlc/state/<change>/*.jsonl`, `*.json`, etc.), it MUST address ALL of:

### 1. Atomicity of writes
**No `open(path, "w")` followed by `write()`.** A crash mid-write leaves a truncated/empty file. Other readers see corruption and (per fail-CLOSED contract) escalate when they shouldn't.

```python
import os
from pathlib import Path

def _atomic_write_json(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(data))
    os.replace(str(tmp), str(path))  # POSIX-atomic rename
```

**The `.tmp.{os.getpid()}` suffix matters** — two processes writing to the same target each get their own tmp file, no `FileNotFoundError` on parallel rename.

### 2. Concurrency: file locks on read-modify-write
**`os.replace` is atomic per-write, but NOT per-counter-increment.** Two processes both reading `global_iter=N` and both writing `N+1` lose one increment.

```python
import fcntl
import contextlib

@contextlib.contextmanager
def _file_lock(path: Path):
    lock_path = path.with_suffix(path.suffix + ".lock")
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)  # blocks until lock acquired
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)

# Usage at every read-modify-write site:
with _file_lock(loop_budget_path):
    data = read_loop_budget(...)
    data["global_iter"] += 1
    _atomic_write_json(loop_budget_path, data)
```

### 3. Concurrency: JSONL appends
**Plain `open("a")` is NOT safe for parallel appends** when rows exceed PIPE_BUF (4096B on Linux). Interleaved bytes produce malformed JSON lines.

```python
with _file_lock(jsonl_path):
    with open(jsonl_path, "a") as f:
        f.write(json.dumps(row) + "\n")
```

### 4. Idempotency
**Hook can re-fire for the same event** (retries, network blips, dual stop events). Without dedupe, counters double-increment and feedback files get overwritten.

Strategy: dedupe by `invocation_id` (from envelope) OR hash of `(agent_name, sig_hash, attempt)`. Maintain a ring buffer of last N seen events (e.g. 50) in the state file.

```python
def _is_duplicate(state, invocation_id):
    return invocation_id in state.get("recent_invocations", [])[-50:]

# At every increment site:
if _is_duplicate(state, invocation_id):
    print(f"[sentinel] skipping duplicate invocation {invocation_id}")
    return
```

### 5. Fail-CLOSED on parse errors
**`try/except → continue/return None` is fail-OPEN dressed as safety.** Every uncaught error must escalate by default.

```python
# WRONG (fail-open):
try:
    data = json.loads(content)
except Exception:
    return None  # silent allow!

# RIGHT (fail-closed):
try:
    data = json.loads(content)
except Exception as e:
    print(f"[sentinel] state file unparseable: {e}", file=sys.stderr)
    # Treat as escalation-required; do NOT proceed as if state was empty
    return ("corrupt", None)
```

### 6. Schema validation on config load
**TOML/JSON config typos must FAIL LOUD, not silently revert to defaults.** Operator believes ceiling=50, real ceiling=25.

```python
def load_config():
    try:
        cfg = tomllib.loads(config_path.read_text())
    except Exception as e:
        if os.environ.get("RALPH_STRICT_CONFIG", "").lower() == "true":
            raise  # fail-loud opt-in
        print(f"[sentinel] config load failed, falling back: {e}", file=sys.stderr)
        return FALLBACK_CONFIG
    # Always log when falling back
    return validate_schema(cfg)
```

### 7. Sentinel handler: parse → classify → check budget → emit envelope
The canonical control flow:

```python
def main():
    payload = json.loads(sys.stdin.read())
    envelope_status = payload.get("status")

    # Pass-through cases (don't touch counters)
    if envelope_status in ("done", "needs_specialist"):
        return _emit({"continue": True})

    # Idempotency dedupe
    if _is_duplicate(state, payload["invocation_id"]):
        return _emit({"continue": True})

    # Classify trigger
    trigger = classify_trigger(payload)
    if trigger is None and envelope_status != "partial":
        return _emit({"continue": True})

    # Lock-protected counter increment
    with _file_lock(loop_budget_path):
        state = read_state(...)
        if budget_exhausted(state, trigger):
            write_escalation(...)
            return _emit({"continue": False, "reason": "..."})
        increment_loop_budget(...)
        write_feedback(...)
    return _emit({"continue": True})
```

## Tests every sentinel MUST have

Per `tests/harness/sentinels/test_iteration_budget_autoloop.py` as the reference pattern:

1. **Concurrent appends** — spawn N=10 threads/processes each writing 1 row, assert N rows valid JSON in final file
2. **Atomic write under crash** — kill mid-write, assert old or new file but not corrupt
3. **Idempotent double-fire** — fire same envelope twice with same invocation_id, assert counter incremented once
4. **Corrupted tail fail-CLOSED** — append malformed trailing line, assert stop-signal triggers (escalate, not retry)
5. **Invalid config logs and falls back** — feed malformed TOML, assert stderr log + fallback used
6. **Wall-clock fail-CLOSED on corrupt ts** — corrupt `first_ts`, assert wall-clock returns `inf` (forces escalation)
7. **Passthrough cases (`status: done`, `needs_specialist`)** — no feedback written, no counter touched

## Anti-patterns

- **NEVER** `json.dumps` directly into the target file. Always temp+rename.
- **NEVER** `try/except Exception: pass`. Either escalate or specifically handle.
- **NEVER** assume PIPE_BUF size protects you from interleaved writes. Use locks.
- **NEVER** silently revert to defaults on config error without stderr log + env-var fail-loud option.
- **NEVER** dedupe by hash without considering when hash collisions could leak (e.g. same agent + same sig + 2 different attempts → must include attempt number).

## When to apply

Apply this checklist when:
- Writing a new sentinel hook in `.claude/harness/sentinels/`
- Modifying any hook that persists state across invocations
- Reviewing a hook PR — gate merge on these 7 items + tests

## Source

Pattern distilled from:
- `.claude/harness/sentinels/iteration-budget.py` (V7.3 reference implementation, 836 LOC)
- `.sdlc/state/p1-1-v73-race-conditions-report.md` (P1.1 hardening report, 2026-05-27)
- `tests/harness/sentinels/test_iteration_budget_autoloop.py` (17 tests, including 10-process parallel smoke at `.sdlc/state/p1-1-smoke.py`)
