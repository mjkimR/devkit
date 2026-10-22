---
id: PLAN-merge-not-ff-auto
spec: SPEC-merge-not-ff-auto
summary: Implementation plan for transitioning WORKTREE_MERGE_NOT_FF from INTERACTION to AUTO mode.
status: planned
created: 2026-10-22
---

# [PLAN-merge-not-ff-auto] Implementation Plan

## 1. Constitution & Invariant Review

- AAP Invariant: An error with `actor = Actor.TOOL` and `level = Level.ERROR` derives `mode = ActionMode.AUTO`.
- Worktree Invariant: `MergeNotFastForwardError` leaves the repository untouched and provides a fix message instructing a base merge.
- Safety Invariant: `MergeConflictError` retains `_Interaction` (`actor = Actor.USER`), so real conflicts still prompt the user.

## 2. Architecture Overview & Impact

- **Impacted components**:
  - `packages/devkit/src/devkit_agt/features/worktree/models/errors.py`:
    - Change `MergeNotFastForwardError` inheritance from `_Interaction` to `WorktreeError`.
    - Explicitly define `actor = Actor.TOOL`.
  - `docs/capabilities/worktree/CAP-WT-task-worktrees.md`:
    - Update error table/description for `WORKTREE_MERGE_NOT_FF` to `ERROR (AUTO)`.
  - `docs/development/reference/worktree.md`:
    - Update reference table for `WORKTREE_MERGE_NOT_FF`.
  - Tests in `packages/devkit/tests/e2e/features/integration/test_base_advance.py` and `packages/devkit/tests/integration/features/worktree/test_merging.py`.

## 3. Component & Interface Design

```python
class MergeNotFastForwardError(WorktreeError):
    """The base moved on since the branch was created and the merge may not absorb it (``AUTO``).

    ``finish --merge`` lands only a branch that contains the base HEAD; the integration service absorbs later target
    commits only under ``merge = "no-ff"`` and only after its approval.
    """

    code = "WORKTREE_MERGE_NOT_FF"
    actor = Actor.TOOL
    fix = _MERGE_TARGET_FIX
```

## 4. Storage & State Management

- No change to persisted state or Git repositories.

## 5. Error Handling & Edge Cases

- Real conflicts during merge continue to raise `MergeConflictError` (`WORKTREE_MERGE_CONFLICT`), which inherits `_Interaction` and preserves `INTERACTION` mode.
- Rerunning the integration command after applying `[FIX]` fast-forwards or lands cleanly.

## 6. Verification & Test Plan

- Unit & integration tests in `packages/devkit/tests/e2e/features/integration/test_base_advance.py` asserting `error.mode is ActionMode.AUTO`.
- Run `just test-affected` and `just rules-check`.
