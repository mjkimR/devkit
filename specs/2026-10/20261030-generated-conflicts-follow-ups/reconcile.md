---
reconcile_id: REC-generated-conflicts-follow-ups
spec: SPEC-generated-conflicts-follow-ups
status: resolved
targets:
  - file: docs/development/reference/core.md
    resolution: modified
  - file: docs/development/workflow.md
    resolution: modified
  - file: docs/development/ci-cd.md
    resolution: modified
---

# Reconcile: `SPEC-generated-conflicts-follow-ups`

## Contract comparison

- `docs/development/reference/core.md` names `run_git_result(cwd, *args, ok_returncodes=(0,), ...) -> GitResult`, its
  accepted statuses, unchanged `GitError` for other statuses and no memo, and that `run_git` is it with only `0`
  accepted (AC-01, AC-02). Code: `packages/devkit-core/src/devkit_core/core/git.py`.
- `CAP-WT-task-worktrees` states that worktree Git runs through `devkit_core.core.git.run_git`; `merge-tree` now runs
  on the same runner (`run_git_result`), so the statement holds without the earlier private call and needs no change
  (AC-03). `docs/development/reference/worktree.md` never named the private call.
- `docs/development/workflow.md` and `docs/development/ci-cd.md` name `devkit generated check`, and `devkit generated
  regen <ids>` with a commit for stale artifacts, before the batch test run, as `ADR-generated-conflicts-in-prepared-merge`
  and the `spec-orchestrate` source state (AC-04). The root `AGENTS.md` Verification paragraph says the same.
- `docs/development/ci-cd.md` lists `specs/` among repository files tests read and says `docs/` and `specs/` select
  the shipped-bundle citation test, matching `scripts/affected_tests.py` (AC-06).

## No impact

- `CAP-DLV-delivery-workflows` lists the payload rules with a cross-role contract (sync outputs, probe paths, scratch
  files); the new `spec-delegate` payload rule (AC-05) changes no role contract or record, so the capability stays as
  is (spec assumption 3).
- `ADR-test-selection-and-ci` decides the selector's approach, not its table entries; no capability states the table.
- The two root `AGENTS.md` lines (AC-05, AC-07) are repository guidance outside the managed block, not Living Spec.

## Source feedback

- `FB-run-git-drops-output-on-nonzero-exit`: resolved (AC-01 to AC-03; `test_git.py`, worktree and integration
  suites).
- `FB-workflow-batch-run-omits-generated-check`: resolved (AC-04; the three sentences reviewed).
- `FB-layering-choice-without-architecture-scope`: resolved (AC-05; `test_architecture_scope_guidance.py`).
- `FB-citation-test-not-selected-by-docs-changes`: resolved (AC-06; `test_affected_tests.py`).
- `FB-bundle-asset-edits-miss-authoring-instruction`: resolved (AC-07; reviewed, `devkit sync --check` clean).

## Deferred work

None in scope. `test_mounted_commands.py::test_a_mounted_command_imports_only_its_area_and_lower_layers[integration]`
fails on this branch and predates it (the integration area imports `generated` since the integrated
`SPEC-generated-conflicts-in-prepared-merge`); it is recorded as feedback at `collect-feedback`.
