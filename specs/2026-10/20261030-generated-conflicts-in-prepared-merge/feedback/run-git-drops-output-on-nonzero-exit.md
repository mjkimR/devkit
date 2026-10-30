---
id: FB-run-git-drops-output-on-nonzero-exit
title: run_git drops standard output when Git exits nonzero
scope: repo
kind: suggestion
category: other
target: packages/devkit-core/src/devkit_core/core/git.py run_git
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-30
---

# [FB-run-git-drops-output-on-nonzero-exit] run_git drops standard output when Git exits nonzero

Tooling API gap in the shared Git runner.

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current**: `run_git` raises `GitError` on any nonzero exit, and `GitError` carries the command, exit status and
  standard error but not standard output. `git merge-tree --write-tree` reports a conflict with exit `1` and writes the
  tree id and the conflicted entries to standard output, so `worktree/services/merging.py` runs that one command
  through `subprocess` itself, copying `run_git`'s environment and timeout handling.
- **Proposal**: let `run_git` accept the exit statuses that are answers (for example `ok_returncodes=(0, 1)`), or keep
  standard output on `GitError`, so callers reading such commands stay on the shared runner.
- **Benefit**: one place for Git's environment, timeout and memoization rules; no second copy to drift.
