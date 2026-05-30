#!/usr/bin/env python3
# CONTRACT EXCEPTION (v7-F1): network IO (WebFetch interception) — target: SP-1 effectors
"""
web-distill.py — PreToolUse hook (matcher: WebFetch)

Intercepts WebFetch calls, fetches the URL with Python's urllib, strips HTML
noise, and returns distilled content to Claude instead of raw HTML.

Distillation pipeline (stdlib only — no external dependencies):
  1. Fetch URL with urllib (follows redirects, browser User-Agent)
  2. Remove <script>, <style>, <nav>, <footer>, <header>, <aside>, <form>
  3. Prefer semantic containers: <main>, <article>, <section>
  4. Extract text with html.parser
  5. Deduplicate + collapse whitespace
  6. Truncate to MAX_CHARS

Cache (NEW v2):
  - Per-URL distilled-content cache at /tmp/agent007-web-cache/<sha256>.json
  - Default TTL 24h (env: WEB_DISTILL_TTL_SECONDS, env: WEB_DISTILL_DISABLE_CACHE)
  - Cache hit returns the same {decision: block, reason} payload — agent never
    sees the difference between hit and miss
  - Cache miss → fetch → distill → cache write → return

Passthrough on:
  - Non-HTML responses (images, JSON, PDF)
  - Fetch errors (network, timeout, 4xx/5xx)
  - Empty distilled body
"""

import hashlib
import html.parser
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

MAX_CHARS = 10_000
FETCH_TIMEOUT = 3
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

CACHE_DIR = Path(tempfile.gettempdir()) / "agent007-web-cache"
DEFAULT_TTL_SECONDS = 24 * 60 * 60  # 24h


def _ttl_seconds() -> int:
    raw = os.environ.get("WEB_DISTILL_TTL_SECONDS", "")
    if not raw.isdigit():
        return DEFAULT_TTL_SECONDS
    return max(60, int(raw))  # floor at 60s — anything less defeats the purpose


def _cache_disabled() -> bool:
    return os.environ.get("WEB_DISTILL_DISABLE_CACHE", "").lower() in {"1", "true", "yes"}


def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _cache_path(url: str) -> Path:
    return CACHE_DIR / f"{_cache_key(url)}.json"


def cache_get(url: str) -> Optional[str]:
    """Return cached distilled body if present and fresh, else None."""
    if _cache_disabled():
        return None
    path = _cache_path(url)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    saved_at = float(data.get("saved_at", 0))
    if time.time() - saved_at > _ttl_seconds():
        return None
    body = data.get("body")
    return body if isinstance(body, str) else None


def cache_set(url: str, body: str) -> None:
    if _cache_disabled():
        return
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        payload = {"url": url, "saved_at": time.time(), "body": body}
        _cache_path(url).write_text(json.dumps(payload), encoding="utf-8")
    except OSError:
        pass  # cache failure must never block the tool call


# ---------------------------------------------------------------------------
# HTML extractor
# ---------------------------------------------------------------------------

NOISE_TAGS = {
    "script", "style", "nav", "footer", "header", "aside",
    "form", "iframe", "noscript", "svg", "figure", "figcaption",
    "button", "input", "select", "textarea", "label",
    "meta", "link", "head",
}


class _TextExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._chunks: list[str] = []
        self._in_noise: int = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in NOISE_TAGS:
            self._in_noise += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in NOISE_TAGS and self._in_noise > 0:
            self._in_noise -= 1

    def handle_data(self, data: str) -> None:
        if self._in_noise == 0:
            stripped = data.strip()
            if stripped:
                self._chunks.append(stripped)

    def text(self) -> str:
        return "\n".join(self._chunks)


def _extract_subtree(html_text: str, tag: str) -> Optional[str]:
    pattern = re.compile(rf"<{tag}[^>]*>(.*?)</{tag}>", re.IGNORECASE | re.DOTALL)
    m = pattern.search(html_text)
    return m.group(1) if m else None


def distill_html(html_text: str) -> str:
    content = None
    for container in ("main", "article"):
        content = _extract_subtree(html_text, container)
        if content:
            break

    working = content if content else html_text
    extractor = _TextExtractor()
    extractor.feed(working)
    raw = extractor.text()

    lines = raw.splitlines()
    cleaned: list[str] = []
    prev_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        cleaned.append(line)
        prev_blank = is_blank

    result = "\n".join(cleaned).strip()

    paragraphs = re.split(r"\n{2,}", result)
    seen: set[str] = set()
    unique: list[str] = []
    for p in paragraphs:
        key = p.strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(p)

    result = "\n\n".join(unique)
    if len(result) > MAX_CHARS:
        result = result[:MAX_CHARS] + "\n\n[… content truncated — distilled to 10k chars]"
    return result


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def fetch_url(url: str) -> Optional[tuple[str, str]]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            content_type: str = resp.headers.get_content_type() or ""
            raw_bytes: bytes = resp.read(1_000_000)
            charset = resp.headers.get_content_charset("utf-8")
            try:
                body = raw_bytes.decode(charset, errors="replace")
            except (LookupError, UnicodeDecodeError):
                body = raw_bytes.decode("utf-8", errors="replace")
            return content_type, body
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Hook entry point
# ---------------------------------------------------------------------------

PROFILE = os.environ.get("CLAUDE_HOOK_PROFILE", "standard")


def passthrough() -> None:
    print(json.dumps({"continue": True}))
    sys.exit(0)


def emit_distilled(url: str, content_type: str, body: str, source: str) -> None:
    """source = 'cache' | 'fetch'. Indicated subtly in the header for debug."""
    header_line = f"[web-distill] {url}"
    if source == "cache":
        header_line += " (cached)"
    reason = (
        f"{header_line}\n"
        f"Content-Type: {content_type}\n"
        f"─────────────────────────────────────────\n\n"
        f"{body}"
    )
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def main() -> None:
    if PROFILE == "minimal":
        passthrough()

    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        passthrough()

    if payload.get("tool_name", "") != "WebFetch":
        passthrough()

    tool_input: dict = payload.get("tool_input") or {}
    url: str = tool_input.get("url", "").strip()
    if not url:
        passthrough()

    cached = cache_get(url)
    if cached is not None:
        emit_distilled(url, "text/html", cached, source="cache")

    result = fetch_url(url)
    if result is None:
        passthrough()

    content_type, body = result
    if "html" not in content_type:
        passthrough()

    distilled = distill_html(body)
    if not distilled.strip():
        passthrough()

    cache_set(url, distilled)
    emit_distilled(url, content_type, distilled, source="fetch")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Fail-open: never block tool use on hook bug
        passthrough()
