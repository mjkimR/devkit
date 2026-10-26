---
reconcile_id: REC-feedback-guidance-and-scope
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/worktree/CAP-WT-task-worktrees.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/architecture/ARCH-04-1-ecosystem-boundaries.md
    resolution: modified
  - file: docs/glossary.md
    resolution: modified
---

# Reconciliation: `SPEC-feedback-guidance-and-scope`

- `CAP-DLV-proposal-incubation`: 4.5 and the 4.12 `SPEC_PROPOSAL_TARGET_EXISTS` row state that a materials merge
  conflict is `INTERACTION` (no guardrail, actor `USER`) while an existing target stays `BLOCKED` (AC-03, AC-04). The
  `SPEC_HANDOFF_NOT_READY` and `SPEC_HANDOFF_REPLY_INVALID` rows keep their documented modes: the shipped
  `MAINTENANCE` is a defect, tracked as `FB-handoff-refusals-emit-maintenance` (item 4).
- `CAP-COLL-work-scope-registry`: 4.1 and the unresolved-reason table describe the declared feedback file exception,
  its limits and that it never replaces candidates (AC-05 to AC-07).
- `CAP-DLV-delivery-workflows`: the worker paragraph and the Planning probe paragraph leave ignored scratch files to
  worktree removal and state that a payload never asks for create-then-delete (AC-02).
- `CAP-WT-task-worktrees` section 7, the `CAP-DIST-sync-and-transactions` template example, the
  `ARCH-04-1-ecosystem-boundaries` actor row and the glossary term match the shipped package (AC-08).

No other Living Spec impact: `CAP-TRACE-code-entrypoints` already lists every `specs/...` path as `excluded-tree`
for derivation, which is unchanged. `UC-incubate-and-hand-off-a-proposal` and `UC-run-parallel-work-safely` describe
neither the merge conflict directive nor the `_Boundary` exclusions, so their steps hold. The package README and
`guides/install/mcp.md` are mirrors corrected in this unit (item 5).

## Entrypoints

`devkit spec entrypoints derive` proposed every changed file for every capability target; none is written. The
targets already declare their doorways (`CAP-COLL-work-scope-registry` the `features/scope/` directory; the proposal
handoff behind `features/delivery/`), and the other candidates are tests, guidance mirrors, sync outputs or helpers.

## Source feedback

Resolved with a Disposition: `FB-fixture-removal-denied`, `FB-merge-conflict-guardrail-action`,
`FB-scope-external-feedback-target`, `FB-handoff-error-modes-documented-differently`,
`FB-spec-readme-and-mcp-guide-native-handoff`, `FB-integration-mcp-glossary-and-actor-row`,
`FB-worktree-module-layout-stale` and `FB-sync-config-template-example-stale`.

## Deferred work

- `FB-handoff-refusals-emit-maintenance`: the mode change of `HandoffNotReadyError` and `HandoffReplyError`.
- `FB-code-reviewer-probe-deletion`: whether the code-reviewer also leaves its ignored probes to worktree removal.
