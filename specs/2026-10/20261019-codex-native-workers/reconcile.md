---
reconcile_id: REC-codex-native-workers
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconciliation: `SPEC-codex-native-workers`

`CAP-DLV-delivery-workflows` reflects both workers' Codex emulated/workspace-write metadata, session inheritance,
native invocation without path confinement, named-role/effective-contract fallback and explicit trust restrictions.
It also reflects absolute command/nested-role paths, operation-specific approvals, missing-capability fallback,
truthful refusal and failed preservation, unchanged Host acceptance and the bounded execution evidence.
`ADR-codex-native-worker-execution` is the already accepted decision; its material evidence remains read-only.

The deciding independent code review is `envelopes/review-01.yaml` at the committed implementation. This record and
the capability summary/wrapping are later implementer edits, to be verified by the separate reconcile-reviewer.
No runtime/schema/renderer, architecture or other-host configuration change is required; no new domain term or
story is introduced. A targeted search found no additional current worker/Codex contract needing reflection.

Entrypoint candidates are reviewed under spec-entrypoints. Existing subagent-directory coverage owns the worker
contracts; caller procedure details belong to the agent-guidance capability, so this capability should not acquire
the whole caller skill or test/receipt paths through a mechanical boundary join.

No accepted requirement is deferred. Wider host/version behavior, fresh-host named-role loading and denied or
failed emergency preservation remain evidence limits rather than added live-validation requirements. Existing
`FB-native-worker-command-scoped-approvals` and `FB-verification-sync-requires-network` cover the repeated access and
verification friction; do not duplicate or edit those files from this unit.

The recovery of `envelopes/worker-02.yaml` changes only the existing sync-level regression assertion and unit
records. It verifies the already reflected Codex emulated/workspace-write contract and complete projected body,
while retaining both other-host projections. It adds no behavior, constraint, target, domain term or entrypoint;
the resolved Living Spec targets therefore remain unchanged.
