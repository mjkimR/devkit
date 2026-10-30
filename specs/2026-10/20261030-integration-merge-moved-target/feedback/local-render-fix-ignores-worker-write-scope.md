---
id: FB-local-render-fix-ignores-worker-write-scope
title: Stale local render fix names a sync that may write outside a worker's scope
scope: repo
kind: change-request
category: tool-error
target: packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/local_render.py
origin: agent
severity: workaround
recurring: false
status: dismissed
created_at: 2026-10-30
---

# [FB-local-render-fix-ignores-worker-write-scope] Stale local render fix names a sync that may write outside a worker's scope

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: After the Host merged `main` into a `plan-<slug>` branch, the Planning worker's first
  `uv run devkit get-context spec` refused with `CONFIG_LOCAL_RENDER_STALE` (mode `AUTO`, "Run the [FIX] command
  once"). Its fix names a plain `devkit sync`, which may rewrite tracked files (the receipt, the root `AGENTS.md` block,
  seeded files). A Planning or Development worker's write scope denies those paths, so following the AUTO directive
  literally risks an out-of-scope write it may not revert (workers never reset or check out).
- **Proposed Procedure**: When the committed receipt is current and only the ignored copies or the personal render
  evidence are stale, name `devkit sync --locked` in the fix (it restores only Git-ignored copies and never changes the
  receipt, the `AGENTS.md` block or seeded files); keep plain `devkit sync` when committed files would change.
- **Expected Benefit**: A delegated worker can follow the AUTO fix without leaving its write scope or stopping to ask.
- **Cost & Risk**: The fix text depends on whether `--locked` would succeed; a wrong choice sends the agent to a
  `--locked` run that exits 1, after which plain `devkit sync` is still needed.
- **Attempted**: Ran `devkit sync --locked` in the worktree instead: it updated only ignored managed and transient
  files, `git status` stayed clean and `get-context` succeeded.

## Diagnostic Details

- **Reproduction**: merge `main` (with a changed receipt) into a task branch, then run `uv run devkit get-context spec`
  in that worktree before any sync.
- **Expected / Actual**: Expected a fix a scope-restricted worker can run; actual is plain `devkit sync`.
- **Versions**: branch head `bde913ca` (base `main` `b44ff159`).
- **Conditions**: delegated Planning worker whose write scope is the proposal directory; receipt changed by the merge.
- **Workarounds Attempted**: `devkit sync --locked`, then retry: succeeded with a clean `git status`.
- **Related Assets**: `CAP-DIST-context-and-playbooks` (error table row for `CONFIG_LOCAL_RENDER_STALE`);
  `devkit sync --help` (`--locked` "is for a fresh clone, a new worktree and CI").

## Evidence

```text
{"code":"CONFIG_LOCAL_RENDER_STALE", "mode":"AUTO",
 "message":"<worktree>/.devkit/transient/local-render.json: missing or stale local evidence: receipt changed",
 "fix":"Run `uv run devkit sync` in this workspace to refresh personal rendering evidence"}
devkit sync --locked: [CHANGE: update .devkit/managed/spec/...] [CHANGE: update .devkit/transient/local-render.json]
git status --short: (empty)
```

## Disposition

Dismissed as a duplicate of `FB-render-stale-fix-ignores-worker-scope`, which `SPEC-lifecycle-feedback-fixes`
resolved: the `CONFIG_LOCAL_RENDER_STALE` fix now names `uv run devkit sync --locked` first and a plain sync only when
that reports `RECEIPT_STALE`.
