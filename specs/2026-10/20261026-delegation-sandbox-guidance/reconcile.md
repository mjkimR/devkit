---
reconcile_id: REC-delegation-sandbox-guidance
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconcile: `SPEC-delegation-sandbox-guidance`

## Living Spec

- `CAP-DLV-delivery-workflows`: the role table's `code-reviewer` "Writes" cell names the throwaway probe tests under
  the ignored probe path; the worker paragraph states the sync outputs in a selected-bundle write scope and the
  worker-producible before/after baseline; the approval paragraph states the fixed task worktree path, the meaning of
  `--workspace-root`, the shared Git directory and the permitted route when either is outside the writable roots.
- No impact: `ARCH-04-1-ecosystem-boundaries` calls the support roles "read-only inspection"; the code reviewer stays
  `x-git-actions: [read]` and leaves `git status --short` unchanged, so the statement still holds.
  `CAP-WT-task-worktrees` already states the fixed worktree path; this unit changes no worktree behaviour.
- No use case changes: the change is role and payload guidance, not a user goal.

## Entrypoints

`devkit spec entrypoints derive` offered the eight changed paths for `CAP-DLV-delivery-workflows`; none was applied,
because each is a wording edit in a guidance document, a test or the sync receipt, not a doorway file of that
capability.

## Source feedback

Each was resolved with a Disposition naming this spec, verified by
`packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py` and `review-01`/`reverify-01`:

- `FB-bundle-change-needs-sync-scope`: resolved (its second suggestion was already covered by the reconcile-target
  write scope).
- `FB-base-measurement-outside-worker-git`: resolved.
- `FB-reviewer-probe-tests`: resolved.
- `FB-worktree-sandbox-location`: resolved with a correction; `--workspace-root` does not relocate a worktree.
- `FB-git-metadata-sandbox-boundary`: resolved for devkit's guidance; making Git metadata writable is the host's
  sandbox configuration.

## Deferred work

None.
