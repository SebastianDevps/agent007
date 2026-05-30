#!/usr/bin/env python3
"""
agent-tool-allowlist.py — Enforces per-agent tool allowlists (F2 of plugin
master plan).

CONTRACT: fail-CLOSED on any error.
  Any uncaught exception, malformed frontmatter, unreadable agent file, corrupt
  state, symlink at the state path, or unparseable input → emit a `block`
  envelope. Silent allow is the original vulnerability (audit C-1, C-2, H-1
  through H-4, M-1, M-3) — this rewrite eliminates every fail-OPEN code path.

THREAT MODEL (audit 2026-05-27, .sdlc/state/security-audits/):
  - Stale state across dispatches (H-1): every PreToolUse(Agent) rotates a
    UUID4 nonce; non-Agent tools verify the state's mtime is fresh (<
    STALE_SECONDS) and BLOCK otherwise.
  - Symlink swap on state path (H-2): writes use
    os.open(O_NOFOLLOW|O_CREAT|O_TRUNC|O_WRONLY, 0o600). ELOOP → block.
  - Malformed frontmatter (H-4): yaml.safe_load; YAMLError → block.
  - Path traversal in subagent_type (M-2): name validated against
    ^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$.
  - Prefix-match bypass (H-3): only the `entry__` MCP-namespace form is
    honored. The speculative `entry(` parenthesized form is removed.
  - Profile downgrade (C-2): CLAUDE_HOOK_PROFILE=minimal requires BOTH the env
    var AND settings.json hooks.allow_minimal_profile == true.

EVENTS:
  1. PreToolUse(Agent|Task) — record {name, tools, nonce, created_at} into
     .claude/state/active-subagent.json after validating the subagent_type
     name and parsing the agent file frontmatter.
  2. PreToolUse(<other>) — read state, verify freshness, enforce allowlist.
  3. SubagentStop — clear state.

ALWAYS-ALLOWED (regardless of allowlist):
  - Read   (subagents must read their SKILL.md)
  - Skill  (skill invocation is orthogonal to tool gating)

EMPTY ALLOWLIST (`tools: []`):
  Restrictive. Only ALWAYS_ALLOWED runs. A warning is emitted to stderr per
  the docstring contract (audit M-5).

Performance budget: < 20ms.

CONFIGURATION:
  AGENT_TOOL_ALLOWLIST_STALE_SECONDS — override the staleness threshold.
    Range: 60–7200 (seconds). Default: 1800 (30 min).
    Out-of-range or non-integer values log a warning to stderr and fall back
    to the default. Useful for long-running subagent sessions (e.g. ralph-loop
    overnight) where 30 min would prematurely invalidate active state.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import uuid
from pathlib import Path

try:
    import yaml  # PyYAML, stdlib-of-our-harness (6.0.3 verified present)
except ImportError:  # pragma: no cover — fail-CLOSED if yaml missing
    print(json.dumps({
        "decision": "block",
        "reason": "[agent-tool-allowlist] PyYAML missing; cannot enforce safely. "
                  "Install pyyaml or set hooks.allow_minimal_profile in settings.json.",
    }))
    sys.exit(0)


STATE_REL = Path(".claude") / "state" / "active-subagent.json"
AGENTS_REL = Path(".claude") / "agents"
SETTINGS_REL = Path(".claude") / "settings.json"
ALWAYS_ALLOWED = frozenset({"Read", "Skill"})
SUBAGENT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_STALE_DEFAULT = 30 * 60
_STALE_MIN = 60
_STALE_MAX = 7200


def _load_stale_seconds() -> int:
    raw = os.environ.get("AGENT_TOOL_ALLOWLIST_STALE_SECONDS")
    if raw is None:
        return _STALE_DEFAULT
    try:
        v = int(raw)
        if _STALE_MIN <= v <= _STALE_MAX:
            return v
        print(
            f"[agent-tool-allowlist] STALE_SECONDS={raw} out of range "
            f"[{_STALE_MIN},{_STALE_MAX}]; using default {_STALE_DEFAULT}",
            file=sys.stderr,
        )
    except ValueError:
        print(
            f"[agent-tool-allowlist] STALE_SECONDS={raw!r} not an integer; "
            f"using default {_STALE_DEFAULT}",
            file=sys.stderr,
        )
    return _STALE_DEFAULT


STALE_SECONDS = _load_stale_seconds()


# ---------------------------------------------------------------------------
# Hook envelopes
# ---------------------------------------------------------------------------

def allow() -> None:
    print(json.dumps({"continue": True}))
    sys.exit(0)


def block(message: str) -> None:
    print(json.dumps({
        "decision": "block",
        "reason": f"[agent-tool-allowlist] {message}",
    }))
    sys.exit(0)


# ---------------------------------------------------------------------------
# Profile / settings gating (C-2 fix)
# ---------------------------------------------------------------------------

def minimal_profile_authorized(root: Path) -> bool:
    """CLAUDE_HOOK_PROFILE=minimal requires explicit settings.json opt-in.

    Both must be true: env var set AND settings has
    hooks.allow_minimal_profile == true. Anything else → enforcement stays on.
    """
    if os.environ.get("CLAUDE_HOOK_PROFILE") != "minimal":
        return False
    settings_path = root / SETTINGS_REL
    if not settings_path.is_file():
        return False
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(data, dict):
        return False
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return False
    return hooks.get("allow_minimal_profile") is True


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def parse_payload() -> dict | None:
    """Return parsed JSON payload, or None on parse failure (caller fails-closed)."""
    try:
        raw = sys.stdin.read()
    except Exception:
        return None
    if not raw.strip():
        return {}
    try:
        obj = json.loads(raw)
    except ValueError:
        return None
    return obj if isinstance(obj, dict) else None


def project_root() -> Path:
    cur = Path(os.getcwd())
    while cur != cur.parent:
        if (cur / ".claude").is_dir():
            return cur
        cur = cur.parent
    return Path(os.getcwd())


# ---------------------------------------------------------------------------
# Frontmatter parsing — yaml.safe_load (H-4 fix)
# ---------------------------------------------------------------------------

def parse_agent_frontmatter(agent_md: Path) -> tuple[str, dict | None]:
    """Return (status, data). status ∈ {"ok","missing","unreadable","malformed","no_frontmatter"}.

    - ok: data is the parsed mapping (possibly empty).
    - missing: file does not exist → caller treats as a stock built-in agent.
    - unreadable: OSError other than FileNotFoundError → fail-CLOSED.
    - malformed: YAML parse error or non-mapping root → fail-CLOSED.
    - no_frontmatter: file exists but no leading `---` block → treat as no
      tools declaration (permissive); caller decides.
    """
    try:
        text = agent_md.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ("missing", None)
    except OSError:
        return ("unreadable", None)

    if not text.startswith("---"):
        return ("no_frontmatter", None)
    parts = text.split("---", 2)
    if len(parts) < 3:
        return ("no_frontmatter", None)
    fm_raw = parts[1]

    try:
        data = yaml.safe_load(fm_raw)
    except yaml.YAMLError:
        return ("malformed", None)
    if data is None:
        return ("ok", {})
    if not isinstance(data, dict):
        return ("malformed", None)
    return ("ok", data)


def load_agent_tools(root: Path, name: str) -> tuple[str, list[str] | None]:
    """Look up an agent file. Returns (status, tools_or_None).

    status:
      - "missing"     → no file (stock agent) → caller ALLOWS + clears state.
      - "unreadable"  → file exists but unreadable → BLOCK (M-1 fix).
      - "malformed"   → YAML error → BLOCK (H-4 fix).
      - "permissive"  → no `tools:` field declared → caller writes state with
                        tools=None.
      - "restricted"  → tools list (possibly empty); caller writes state.
    """
    agent_md = root / AGENTS_REL / f"{name}.md"
    status, fm = parse_agent_frontmatter(agent_md)
    if status == "missing":
        return ("missing", None)
    if status == "unreadable":
        return ("unreadable", None)
    if status == "malformed":
        return ("malformed", None)
    if status == "no_frontmatter":
        return ("permissive", None)
    # status == "ok"
    assert fm is not None
    if "tools" not in fm:
        return ("permissive", None)
    tools = fm.get("tools")
    if tools is None:
        return ("permissive", None)
    if isinstance(tools, str):
        return ("restricted", [tools])
    if isinstance(tools, list):
        out: list[str] = []
        for t in tools:
            if not isinstance(t, (str, int, float)):
                # Non-scalar list item (e.g. a dict) → malformed intent.
                return ("malformed", None)
            out.append(str(t))
        return ("restricted", out)
    # tools field is a dict or other unexpected shape.
    return ("malformed", None)


# ---------------------------------------------------------------------------
# State file I/O — symlink-safe (H-2 fix), restricted perms (M-4 fix)
# ---------------------------------------------------------------------------

def write_state(root: Path, payload: dict) -> tuple[bool, str]:
    """Write state atomically, refusing to follow symlinks. Returns (ok, err)."""
    state_path = root / STATE_REL
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return (False, f"cannot create state dir: {exc}")

    # Pre-delete only if it's a regular file owned by us. If it's a symlink
    # the O_NOFOLLOW open will fail with ELOOP and we BLOCK — caller surfaces.
    try:
        if state_path.is_symlink():
            return (False, "state path is a symlink — refusing to write (audit H-2)")
    except OSError as exc:
        return (False, f"cannot stat state path: {exc}")

    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    old_umask = os.umask(0o077)
    try:
        try:
            fd = os.open(str(state_path), flags, 0o600)
        except OSError as exc:
            return (False, f"cannot open state for write ({exc.errno}): {exc}")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(json.dumps(payload))
        except OSError as exc:
            return (False, f"state write failed: {exc}")
    finally:
        os.umask(old_umask)
    return (True, "")


def clear_state(root: Path) -> None:
    state_path = root / STATE_REL
    try:
        if state_path.is_symlink() or state_path.exists():
            state_path.unlink()
    except OSError:
        # Best-effort clear; next dispatch will overwrite.
        pass


def read_state(root: Path) -> tuple[str, dict | None]:
    """Returns (status, data). status ∈ {"none","ok","corrupt","stale","symlink"}."""
    state_path = root / STATE_REL
    try:
        if state_path.is_symlink():
            return ("symlink", None)
        if not state_path.exists():
            return ("none", None)
    except OSError:
        return ("corrupt", None)
    try:
        st = state_path.stat()
    except OSError:
        return ("corrupt", None)
    if (time.time() - st.st_mtime) > STALE_SECONDS:
        return ("stale", None)
    try:
        raw = state_path.read_text(encoding="utf-8")
    except OSError:
        return ("corrupt", None)
    try:
        data = json.loads(raw)
    except ValueError:
        return ("corrupt", None)
    if not isinstance(data, dict):
        return ("corrupt", None)
    return ("ok", data)


# ---------------------------------------------------------------------------
# Tool allowlist matching (H-3 fix — drop `(` prefix form)
# ---------------------------------------------------------------------------

def tool_allowed(tool: str, allowlist: list[str]) -> bool:
    if tool in ALWAYS_ALLOWED:
        return True
    if tool in allowlist:
        return True
    # MCP namespace prefix only. The speculative `entry(` form removed.
    for entry in allowlist:
        if not isinstance(entry, str) or not entry:
            continue
        if tool.startswith(entry + "__"):
            return True
    return False


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------

def handle_pre_tool_use(payload: dict, root: Path) -> None:
    tool = payload.get("tool_name") or payload.get("toolName") or ""
    inp = (
        payload.get("tool_input")
        or payload.get("toolInput")
        or payload.get("input")
        or {}
    )
    if not isinstance(inp, dict):
        inp = {}

    # CASE 1: Agent/Task dispatch → rotate state with fresh nonce.
    if tool in ("Agent", "Task"):
        subagent_name = (
            inp.get("subagent_type")
            or inp.get("subagentType")
            or ""
        )
        if not subagent_name:
            # No subagent named → not an enforced dispatch (legacy / stock).
            # Clear stale state defensively (H-1 fix).
            clear_state(root)
            allow()
        if not isinstance(subagent_name, str) or not SUBAGENT_NAME_RE.match(subagent_name):
            # M-2 fix: reject traversal / null-bytes / overly long names.
            block(
                f"Rejected subagent name '{subagent_name!r}': must match "
                f"{SUBAGENT_NAME_RE.pattern}"
            )

        status, tools = load_agent_tools(root, subagent_name)
        if status == "missing":
            # Stock built-in agent — clear stale state, allow without enforcement.
            clear_state(root)
            allow()
        if status == "unreadable":
            block(
                f"Agent file for '{subagent_name}' is unreadable. "
                "Fix permissions or remove the file."
            )
        if status == "malformed":
            block(
                f"Agent file for '{subagent_name}' has malformed frontmatter. "
                "Fix YAML or remove the `tools:` declaration."
            )
        # `permissive` (tools field absent) → state.tools=None.
        # `restricted` (tools list/scalar present) → state.tools=[...].
        ok, err = write_state(root, {
            "name": subagent_name,
            "tools": tools,
            "nonce": uuid.uuid4().hex,
            "created_at": time.time(),
        })
        if not ok:
            block(f"State write failed: {err}")
        if isinstance(tools, list) and len(tools) == 0:
            # M-5: empty allowlist warning (docstring contract).
            print(
                f"[agent-tool-allowlist] WARNING: agent '{subagent_name}' has "
                f"empty `tools: []`. Only {sorted(ALWAYS_ALLOWED)} can run.",
                file=sys.stderr,
            )
        allow()

    # CASE 2: Non-Agent tool call → consult active state.
    status, state = read_state(root)
    if status == "none":
        # Main thread or stock agent dispatch — nothing to enforce.
        allow()
    if status == "symlink":
        block("active-subagent.json is a symlink — refusing to read (audit H-2).")
    if status == "corrupt":
        # M-3 fix: corrupt state is an integrity violation, not absence.
        block(
            "active-subagent.json is corrupt or unreadable. "
            "Clear .claude/state/active-subagent.json and re-dispatch."
        )
    if status == "stale":
        # H-1 fix: stale state from a previous session/dispatch must not
        # silently authorize the current call. Clear and block.
        clear_state(root)
        block(
            f"active-subagent.json is older than {STALE_SECONDS}s (stale "
            "dispatch). State cleared; please re-dispatch the subagent."
        )
    assert state is not None
    name = state.get("name", "<unknown>")
    if not isinstance(name, str) or not SUBAGENT_NAME_RE.match(name):
        block("state file contains invalid subagent name (corrupt or tampered).")
    nonce = state.get("nonce")
    if not isinstance(nonce, str) or not nonce:
        # State predates nonce rotation → cannot trust it. Fail-CLOSED.
        block(
            "active-subagent.json missing dispatch nonce. "
            "Clear .claude/state/active-subagent.json and re-dispatch."
        )
    allowlist = state.get("tools")
    if allowlist is None:
        # Agent declared no `tools:` → permissive (intentional, docstring).
        allow()
    if not isinstance(allowlist, list):
        block("state file `tools` field is malformed (expected list or null).")
    if tool_allowed(tool, allowlist):
        allow()
    block(
        f"Agent '{name}' is not permitted to use tool '{tool}'.\n"
        f"  Allowlist (from .claude/agents/{name}.md): {allowlist or '[]'}\n"
        f"  Always allowed: {sorted(ALWAYS_ALLOWED)}\n"
        "If this tool is legitimately required, add it to the agent's "
        "frontmatter `tools:` array."
    )


def handle_subagent_stop(root: Path) -> None:
    clear_state(root)
    allow()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    root = project_root()

    if minimal_profile_authorized(root):
        print(
            "[agent-tool-allowlist] WARNING: minimal profile active "
            "(CLAUDE_HOOK_PROFILE=minimal + settings opt-in). "
            "Enforcement DISABLED for this invocation.",
            file=sys.stderr,
        )
        allow()
    elif os.environ.get("CLAUDE_HOOK_PROFILE") == "minimal":
        # Env var set but settings opt-in missing → ignore the env var.
        print(
            "[agent-tool-allowlist] WARNING: CLAUDE_HOOK_PROFILE=minimal "
            "ignored (settings.json hooks.allow_minimal_profile is not true). "
            "Enforcement remains active.",
            file=sys.stderr,
        )

    payload = parse_payload()
    if payload is None:
        block("malformed hook payload (not valid JSON).")
    assert payload is not None
    event = (
        payload.get("hook_event_name")
        or payload.get("hookEventName")
        or ""
    )

    if event == "SubagentStop":
        handle_subagent_stop(root)
        return
    handle_pre_tool_use(payload, root)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        # C-1 fix: fail-CLOSED on any uncaught error.
        print(json.dumps({
            "decision": "block",
            "reason": f"[agent-tool-allowlist] internal error (fail-closed): "
                      f"{type(exc).__name__}: {exc}",
        }))
        sys.exit(0)
