---
reconcile_id: REC-merge-not-ff-auto
status: resolved
targets:
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/development/reference/worktree.md
    resolution: modified
---

# Reconciliation: `SPEC-merge-not-ff-auto` Auto advisory mode for WORKTREE_MERGE_NOT_FF

`CAP-WT-task-worktrees`, `CAP-INT-mcp-services`, and `docs/development/reference/worktree.md` now specify that `WORKTREE_MERGE_NOT_FF` is an `ERROR (AUTO)` advisory rather than `INTERACTION`:
- `MergeNotFastForwardError` inherits from `WorktreeError` with `actor = Actor.TOOL`, causing AAP to derive `mode = ActionMode.AUTO`.
- The `[ACTION]` directive now instructs: `AUTO — Run the [FIX] command once, then retry the operation once.`
- The `[FIX]` instruction remains unchanged: merging the target branch into the task branch in its worktree without rebasing.
- `MergeConflictError` (`WORKTREE_MERGE_CONFLICT`) retains `actor = Actor.USER` (`INTERACTION`), ensuring agents only interrupt users when genuine merge conflicts occur.
- `FB-merge-not-ff-asks-the-user`: Fully resolved and documented with its resolution disposition.
