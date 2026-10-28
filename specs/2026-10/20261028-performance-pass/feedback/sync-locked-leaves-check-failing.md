---
id: FB-sync-locked-leaves-check-failing
title: sync --locked in a fresh checkout leaves sync --check failing
scope: repo
kind: friction
category: docs-mismatch
target: devkit sync --locked / devkit sync --check (fresh worktree setup)
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-28
---

# [FB-sync-locked-leaves-check-failing] sync --locked in a fresh checkout leaves sync --check failing

## 1. Friction / Question (friction, question)

- **Context**: Preparing isolated checkouts for parallel edit tasks (review-refactor "Subagent edits": run the
  repository's documented setup before handing the checkout over), with `just init` then `devkit sync --locked`.
- **Expectation**: After the documented setup, `devkit sync --check` passes, so the checkout verifies like the work
  branch (the worker contract records `sync --check` as its `sync_start` check).
- **Actual**: `just init` alone leaves 297 planned changes; after `devkit sync --locked` the check still exits 1 with
  four planned creates (`.agents/mcp_config.json`, `.mcp.json`, `.codex/config.toml`,
  `.devkit/transient/mcp/registrations.json`).
- **Workaround (or Interpretation Chosen)**: Treated the remaining MCP registration files as host-local and used the
  checkouts for authoring only; verification ran on the work branch.
- **Suggestion**: Either have `sync --locked` write the host-local MCP registration files, or have `sync --check`
  distinguish host-local registration drift from managed-asset drift (a separate code or notice), and state in the
  setup docs which command makes a fresh worktree check-clean.

## Diagnostic Details

- **Reproduction**: `git worktree add --detach <path> <head>`; `just init`; `uv run devkit sync --locked`;
  `uv run devkit sync --check`.
- **Expected / Actual**: exit 0 / exit 1 `NOT_SYNCHRONIZED` with 4 planned creates.
- **Versions**: repository head 3a638f42 of `dev-performance-pass`.
- **Conditions**: macOS, Claude Code host; the base checkout passes `sync --check`.
- **Workarounds Attempted**: none beyond the interpretation above.
- **Related Assets**: `FB-mcp-registration-pending-ignores-runtime` (different symptom: a repeated notice).

## Evidence

```text
[SYNC: create=4 update=0 remove=0 seed=0 dry_run=yes]
[CHANGE: create .agents/mcp_config.json]
[CHANGE: create .mcp.json]
[CHANGE: create .codex/config.toml]
[CHANGE: create .devkit/transient/mcp/registrations.json]
[ERROR]  (NOT_SYNCHRONIZED) the workspace does not match the selection: 4 planned changes
```
