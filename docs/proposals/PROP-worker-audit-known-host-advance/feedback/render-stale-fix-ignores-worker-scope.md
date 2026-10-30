---
id: FB-render-stale-fix-ignores-worker-scope
title: The render-stale fix names a full sync, which can write outside a worker's scope
scope: repo
kind: friction
category: tool-error
target: CONFIG_LOCAL_RENDER_STALE advisory of devkit get-context
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-render-stale-fix-ignores-worker-scope] The render-stale fix names a full sync, which can write outside a worker's scope

## 1. Friction / Question (friction, question)

- **Context**: A Planning worker started a turn in its worktree after the Host merged `main` into the `plan-` branch;
  the merge changed the committed receipt. The worker's write scope was the proposal directory only.
- **Expectation**: The mandatory first step, `uv run devkit get-context spec`, either works or names a fix the worker
  may run inside its write scope.
- **Actual**: It raised `CONFIG_LOCAL_RENDER_STALE` with mode `AUTO` and the fix `uv run devkit sync`. A full sync may
  change tracked files (the receipt, the root `AGENTS.md` block, seeded files), which a worker's write scope denies.
- **Workaround (or Interpretation Chosen)**: The worker ran `uv run devkit sync --locked`, which restores only the
  ignored copies the committed receipt records and never changes committed files. `get-context` then worked and the
  worktree stayed clean.
- **Suggestion**: Either the Host refreshes the worktree with `devkit sync --locked` after a base merge, before
  spawning (`spec-delegate` payload, Planning bullet), or the advisory names `devkit sync --locked` when the committed
  receipt is current and only ignored copies or local evidence are stale.

## Evidence

```text
get-context spec: CONFIG_LOCAL_RENDER_STALE "<worktree>/.devkit/transient/local-render.json: missing or stale
  local evidence: receipt changed"; fix "Run `uv run devkit sync` ..."; mode AUTO
.devkit/.gitignore:4:/transient/   (the evidence file is ignored)
sync --locked: [CHANGE: update .devkit/managed/...] and .devkit/transient/local-render.json only
git status --short afterwards: empty
```
