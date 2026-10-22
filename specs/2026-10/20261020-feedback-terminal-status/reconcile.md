---
reconcile_id: REC-feedback-terminal-status
status: resolved
targets:
  - file: docs/decisions/2026-10/20261019-feedback-resolution-lifecycle.md
    resolution: modified
  - file: docs/decisions/2026-10/20261020-feedback-terminal-outcomes.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/glossary.md
    resolution: modified
---

# Reconcile: `SPEC-feedback-terminal-status`

The replacement decision separates terminal routing from terminal direct resolution and preserves prior decision
history. The document and guidance contracts define only open feedback as actionable. Delivery contracts and
worker scope agree that terminal source references require no completion writes or implicit authority. Proposal
handoff still preserves terminal feedback in materials and carries open observations into the spec.
The glossary uses the same terminal meanings and current decision owner; the Host authorized this necessary scope
extension after discovery. Existing historical feedback records and status values remain unchanged.

No source feedback was assigned to this task and no required work is deferred. Existing entrypoints cover the
changed worker and bundle implementations; declaration joins to unrelated capability code paths are rejected.
