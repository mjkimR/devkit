---
id: FB-smoke-worktree-finish-merge-retired
title: Consumer smoke still calls the retired worktree finish --merge
scope: repo
kind: friction
category: tool-error
target: tests/e2e/smoke.sh
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-11-11
---

# [FB-smoke-worktree-finish-merge-retired] Consumer smoke still calls the retired worktree finish --merge

## 1. Friction

- **Context**: Verifying `SPEC-retire-legacy-integration-provider-key` with `just smoke`, which must reach the
  `smoke_integration.py` step this unit changed.
- **Expectation**: The consumer smoke uses supported commands and passes on the base.
- **Actual**: `tests/e2e/smoke.sh` lines 355-357 run `devkit worktree finish dev-smoke-task --merge`, which
  `SPEC-retire-finish-merge` turned into the `WORKTREE_MERGE_RETIRED` refusal; smoke exits 2 before the MCP
  integration step. The script was not in that unit's scope, so the base fails `just smoke`.
- **Workaround**: Ran an ignored copy of the script with only those three lines removed; every later step, the
  integration fixture included, passed (`==> smoke passed`).
- **Suggestion**: Land the smoke task through `devkit integration prepare` and `integrate --route local` (or a
  cleanup-only `finish`) and keep the existing `test -f task.md` check.

## Evidence

```text
--- devkit worktree: start sets up and syncs a fresh checkout, its commits pass the gates, finish merges
[ERROR]  (WORKTREE_MERGE_RETIRED) worktree finish --merge is retired; land dev-smoke-task with devkit integration integrate --route local; nothing was changed
error: recipe `smoke` failed on line 82 with exit code 2
```
