---
id: FB-planning-context-command-can-trigger-unavailable-sync
title: Planning context command can trigger unavailable dependency synchronization
scope: repo
kind: friction
category: tool-error
target: .devkit/managed/spec/skills/spec/SKILL.md
skill: spec
agent: codex
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-20
---

# [FB-planning-context-command-can-trigger-unavailable-sync] Planning context command can trigger unavailable dependency synchronization

## 1. Friction / Question

- **Context**: Loading mandatory spec context in a prepared Planning worktree under restricted network access.
- **Expectation**: The documented `uv run devkit get-context spec` loads installed operational instructions.
- **Actual**: uv attempted to fetch the devkit-embed wheel and failed DNS before the context command ran.
- **Workaround**: The Host identified the prepared worktree environment; `uv run --no-sync devkit get-context spec`
  succeeded, and subsequent workflow commands used the same invocation.
- **Suggestion**: State when a prepared, current worktree environment permits `--no-sync` for read-only operational
  commands. Do not prescribe it for environments whose dependencies are missing or stale.

## Diagnostic Details

- **Reproduction**: One ordinary context call failed; one no-sync context call succeeded in the same worktree.
- **Expected / Actual**: Operational context was available locally but dependency resolution attempted network first.
- **Versions**: Repository baseline ffd6e2bbc684c71bb363a3c658f8f2303678eaae; uv version unknown.
- **Conditions**: Prepared worktree virtual environment and unavailable GitHub DNS/network access.
- **Workarounds Attempted**: `--no-sync` succeeded without changing product or dependency configuration.
- **Related Assets**: Mandatory first context call in the spec skill; Host worktree setup and worker handoff.

## Evidence

```text
uv run devkit get-context spec
Failed to generate package metadata for devkit-embed==0.1.0
Failed to fetch wheel from GitHub release; failed to lookup address information
uv run --no-sync devkit get-context spec
exit 0; spec constitution and instruction catalog returned
```
