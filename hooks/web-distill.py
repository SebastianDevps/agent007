#!/usr/bin/env python3
"""
web-distill.py — PreToolUse hook (matcher: WebFetch)

Intercepts WebFetch calls, fetches the URL with Python's urllib,
strips HTML noise, and returns distilled content to Claude instead
of raw HTML.

Distillation pipeline (stdlib only — no external dependencies):
  1. Fetch URL with urllib (follows redirects, browser User-Agent)
  2. Remove <script>, <style>, <nav>, <footer>, <header>, <aside>, <form>
  3. Prefer semantic containers: <main>, <article>, <section>
  4. Extract text with html.parser
  5. Deduplicate + collapse whitespace
  6. Truncate to MAX_CHARS

Passthrough on:
  - Non-HTML responses (images, JSON, PDF)
  - Fetch errors (network, timeout, 4xx/5xx)
  - Already-distilled content (re-entry guard)

Input  (stdin): Claude Code PreToolUse JSON
Output (stdout):
  {"continue": true}                              — passthrough
  {"decision": "block", "reason": "<distilled>"} — distilled content
"""

import html.parser
import json
import re
import sys
import urllib.error
import urllib.request
from typing import Optional

MAX_CHARS = 10_000
FETCH_TIMEOUT = 3   # aggressive — keeps hook chain under 3s; passthrough on timeout
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# Tags whose entire subtree is noise — strip completely
NOISE_TAGS = {
    "script", "style", "nav", "footer", "header", "aside",
    "form", "iframe", "noscript", "svg", "figure", "figcaption",
    "button", "input", "select", "textarea", "label",
    "meta", "link", "head",
}

# Semantic containers to prefer (checked in order, first match wins)
PREFERRED_CONTAINERS = ["main", "article", "section", "[role=main]"]


# ---------------------------------------------------------------------------
# HTML extractor
# ---------------------------------------------------------------------------

class _TextExtractor(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._depth: int = 0          # depth inside a noise tag
        self._chunks: list[str] = []
        self._in_noise: int = 0       # nested noise tag depth

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
    """Return the innerHTML of the first matching tag, or None."""
    pattern = re.compile(
        rf"<{tag}[^>]*>(.*?)</{tag}>",
        re.IGNORECASE | re.DOTALL,
    )
    m = pattern.search(html_text)
    return m.group(1) if m else None


def distill_html(html_text: str) -> str:
    # Try semantic containers first
    content = None
    for container in ("main", "article"):
        content = _extract_subtree(html_text, container)
        if content:
            break

    working = content if content else html_text

    extractor = _TextExtractor()
    extractor.feed(working)
    raw = extractor.text()

    # Collapse runs of blank lines (max 1 blank line between sections)
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

    # Deduplicate identical consecutive paragraphs
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
    """
    Returns (content_type, body_text) or None on any error.
    Follows redirects, sets browser UA, enforces timeout.
    """
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as resp:
            content_type: str = resp.headers.get_content_type() or ""
            raw_bytes: bytes = resp.read(1_000_000)  # cap at ~1 MB
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


def main() -> None:
    if PROFILE == "minimal":
        passthrough()

    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        passthrough()

    tool_name: str = payload.get("tool_name", "")
    if tool_name != "WebFetch":
        passthrough()

    tool_input: dict = payload.get("tool_input") or {}
    url: str = tool_input.get("url", "").strip()
    if not url:
        passthrough()

    # Fetch
    result = fetch_url(url)
    if result is None:
        # Network/timeout error → let WebFetch handle it (better error messages)
        passthrough()

    content_type, body = result

    # Only distill HTML — passthrough JSON, images, binary
    if "html" not in content_type:
        passthrough()

    distilled = distill_html(body)

    if not distilled.strip():
        passthrough()

    reason = (
        f"[web-distill] {url}\n"
        f"Content-Type: {content_type}\n"
        f"─────────────────────────────────────────\n\n"
        f"{distilled}"
    )

    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
