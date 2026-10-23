---
id: FB-git-metadata-sandbox-boundary
title: Make linked-worktree Git metadata permissions explicit
scope: upstream
kind: friction
category: tool-error
target: workspace sandbox permissions for `git commit` in linked worktrees
origin: agent
severity: workaround
recurring: false
status: open
created_at: 2026-10-23
---

# [FB-git-metadata-sandbox-boundary] Make linked-worktree Git metadata permissions explicit

## 1. Friction / Question

- **Context**: Committing verified Development changes from a linked worktree.
- **Expectation**: The repository worktree is writable, so normal Git state updates for that worktree can be completed there.
- **Actual**: The sandbox denied the commit operation because the linked worktree's Git metadata is outside the writable repository root.
- **Workaround (or Interpretation Chosen)**: Run the authorized Git commit through escalated access; the commit completed successfully.
- **Suggestion**: Explain that linked-worktree Git metadata may require escalated access, or make Git index and ref updates available when the worktree itself is writable.

## Evidence

```text
Observed: git commit in the Development worktree required sandbox escalation to update Git metadata; the escalated commit succeeded.
```

## Diagnostic Details

- **Reproduction**: Commit staged files in a linked worktree whose shared Git directory is outside the writable root.
- **Expected / Actual**: Worktree files were writable; the Git state update needed elevated permission.
- **Versions**: unknown
- **Conditions**: Managed workspace-write sandbox, linked Git worktree.
- **Workarounds Attempted**: Authorized `require_escalated` Git commit; passed.
- **Related Assets**: `git commit`; linked-worktree Git metadata.
