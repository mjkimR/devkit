---
id: FB-worktree-module-layout-stale
title: Task worktree module layout lists modules the package no longer has
scope: repo
kind: change-request
category: docs-mismatch
target: CAP-WT-task-worktrees (section 7 Module Layout)
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-worktree-module-layout-stale] Task worktree module layout lists modules the package no longer has

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `CAP-WT-task-worktrees` §7 lists flat modules `extensions.py`, `lifecycle.py`, `stale.py`,
  `merging.py`, `config.py` and `errors.py`. The package is laid out by layer: `models/` (`config`, `errors`,
  `lifecycle`, `planning`, `pull_request`), `repositories/`, `services/` (`extensions`, `merging`) and `usecases/`
  (`configured`, `lifecycle`, `planning`, `stale`).
- **Proposed Procedure**: rewrite §7 to the layered layout, or point to `docs/development/reference/worktree.md`.
- **Expected Benefit**: a reader opens files that exist.
- **Cost & Risk**: one section; no behavior.
- **Attempted**: only the `cli.py` line was fixed (item 12 of `SPEC-living-spec-consistency-sweep`); the rest is
  outside its 22 items.

## Diagnostic Details

- **Reproduction**: `ls packages/devkit/src/devkit_agt/features/worktree/*/`.
- **Expected / Actual**: flat modules / layered directories.
- **Versions**: worktree head of `dev-living-spec-consistency-sweep`.
- **Conditions**: not applicable.
- **Workarounds Attempted**: not attempted.
- **Related Assets**: `CAP-WT-task-worktrees`.

## Evidence

```text
features/worktree/: cli.py models/ repositories/ services/ usecases/ (no top-level stale.py, merging.py, config.py, errors.py)
```
