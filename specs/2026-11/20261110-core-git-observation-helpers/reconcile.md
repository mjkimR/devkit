---
reconcile_id: REC-core-git-observation-helpers
status: resolved
targets:
  - file: docs/capabilities/compact/CAP-CMP-bounded-execution.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-adaptive-assignments.md
    resolution: modified
---

# Reconcile: `SPEC-core-git-observation-helpers`

## Living Spec impact

- `CAP-CMP-bounded-execution`: the sentence describing `devkit_agt.features.compact`'s `status_records` export is
  removed, because the export, its module and its unit test are gone ([AC-04]). The rest of the paragraph (the
  `run_command` and `scan` contract and the feature's import boundary) is unchanged.
- `CAP-DLV-adaptive-assignments`: the revision resolution command gains `--end-of-options`, and output other than a
  full hexadecimal commit ID (the `^<id>` a leading `^` prints) is unresolved ([AC-08]). The error code
  `ADAPTIVE_REVISION_UNRESOLVED` and every other contract line are unchanged.
- `docs/development/reference/core.md` (a quick reference, not a Living Spec contract) documents
  `worktree_records`, `parse_worktree_records`, `status_records`, `parse_status_records`, `WorktreeRecord` and
  `StatusRecord` beside `run_git` ([AC-10]).

## No impact

- No use case changes: no command's steps, output or error codes change. The accidental differences [AC-05] to
  [AC-09] change behavior only for input no capability contract describes (quoted or renamed dirty paths in two
  refusal target lists, a worktree-column rename, a non-UTF-8 or newline worktree path, an option-like revision).
- `CAP-WT-task-worktrees` and `ADR-isolated-test-runs`: the standard-library-only execution module is untouched.
- `ARCH-05-2-components` and `.devkit/architecture.toml`: no feature edge changes; `gate` and `generated` keep their
  `compact` edge for `run_command`, and `devkit_core.core` stays a root module every package may import.
- No decision document changes.

## Entrypoints

`devkit spec entrypoints derive` proposed 32 pairs for the two capabilities; none is written. Each candidate is a
broad shared directory or a `devkit-core` file neither capability owns, and each capability changed by one line.

## Source feedback and deferred work

- `FB-no-public-git-observation-helpers` is already `promoted` (terminal): no disposition is recorded. Its worktree
  and status records and the caller migration are delivered here; its revision resolver was declined in Planning
  (no public resolver; the adaptive lookup is fixed locally), so nothing is deferred.
