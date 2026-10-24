---
reconcile_id: REC-proposal-review-auto-write
spec: SPEC-proposal-review-auto-write
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md
    resolution: modified
---

# Reconcile proposal review publication

`CAP-DLV-proposal-incubation` now specifies the `auto_write` setting, policy output, exact-source report reuse, pre-acceptance publication and acceptance's read-only report use. `UC-incubate-and-hand-off-a-proposal` places report preparation before the approval request and records enabled and disabled paths. Both documents name the proposal review skill and policy CLI as entrypoints. The workflow definition is a contract source rather than a code entrypoint; policy models, parsers, use cases and tests are internal or verification paths. No deferred work or source feedback was identified.
