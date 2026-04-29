# Tech Stack — Agent007 Plugin

## Runtime
- Claude Code CLI (latest) — host environment
- Python 3.9+ — all hooks (.claude/hooks/*.py)
- Node.js 18+ — wave-scheduler.js, bootstrap scripts
- Markdown — skills, agents, rules, commands

## Languages
- Python: hooks (deterministic enforcement at tool boundary)
- Markdown: skills, agent definitions, rules, commands
- JSON: settings.json, state files (.sdlc/state/*.json)
- JavaScript: .claude/scripts/ utilities

## Hook System (21 hooks)
- PreToolUse: safety-guard, rtk-rewrite, block-no-verify, pre-commit-guard, mutation-guard, tool-policy-guard, sdd-guard, config-guard, context-engine, web-distill
- PostToolUse: context-window-guard, tool-loop-detection, format-on-save, sdd-guard
- Stop: state-sync, context-engine
- SessionStart: memory-check, rtk-bootstrap, memory-decay
- SubagentStart: subagent-context, transcript-policy
- UserPromptSubmit: constraint-reinforcement

## Key Dependencies (hooks use stdlib only)
- urllib, html.parser, json, re, hashlib, pathlib — no pip installs required
- RTK binary (/opt/homebrew/bin/rtk 0.34.3) — CLI output compression

## Memory
- Engram MCP — persistent cross-session memory
- .sdlc/state/ — session state, context budget, loop detection, mutation guard

## External Services
- Anthropic API (via Claude Code) — claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5-20251001
