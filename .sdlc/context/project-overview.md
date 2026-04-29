# Project Overview — Agent007 v5.1

## What It Is
Claude Code plugin that converts Claude Code CLI into an autonomous software development system.
Used by a technical team (devs + project leads) for development and large problem resolution.

## Key Numbers
- 10 expert agents (opus/sonnet, each with typed domain + tool_profile)
- 35 skills (pipeline, domain, orchestration, quality-gates, utils)
- 18 hooks (deterministic enforcement at tool boundary)
- LLM-native routing via agent descriptions

## Agent Roster
backend-db-expert · frontend-ux-expert · platform-expert · product-expert ·
security-expert · code-reviewer · loop-operator · refactor-cleaner ·
architect · performance-optimizer

## Core Pipeline
Trivial → Skill('generate') + Skill('verify')
Substantial → SDD: explore → propose → spec → design → tasks → apply → verify → archive

## Entry Commands
/dev "task"         — master command, auto-routes
/consult "question" — expert consultation
/ralph-loop "task"  — autonomous loop until COMPLETE

## Key Files
- .claude/CLAUDE.md — orchestrator instructions (source of truth)
- .claude/settings.json — hook registrations + permissions
- .claude/agents/ — 10 agent definitions
- .claude/skills/ — 35 skills
- .claude/hooks/ — 18 Python/JS hook scripts
- .sdlc/state/ — session state, context budget, loop detection
- .sdlc/context/ — THIS DIRECTORY — project context for subagents

## Philosophy
- Hooks over prompts: deterministic > probabilistic enforcement
- Evidence contract: no "done" without [cmd] → [output]
- LLM-native routing: agent descriptions are the routing signal
- Binary pipeline: Trivial or Substantial — no 3-tier ambiguity
