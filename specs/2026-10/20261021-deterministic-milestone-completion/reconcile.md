---
reconcile_id: REC-deterministic-milestone-completion
feature: SPEC-deterministic-milestone-completion
status: resolved
targets:
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/roadmap/README.md
    resolution: modified
  - file: docs/decisions/2026-10/20261021-milestone-closure-confirmations.md
    resolution: modified
  - file: docs/decisions/2026-10/20261021-separate-unit-prerequisites-from-milestone-themes.md
    resolution: modified
---

# Reconciliation

`CAP-HARN-agent-guidance` reflects the shipped Backlog close procedure and the pre-handoff entrypoints, including
current authority, evidence gaps, direct scope dispositions, invalidation and terminal records.
`CAP-DOCS-document-model` defines the two plain assertions without changing indexing or schema.
`CAP-DLV-proposal-incubation` places membership invalidation before lifecycle changes as an agent procedure,
without changing runtime handoff. The repository roadmap README mirrors the seeded guidance.

`ADR-milestone-closure-confirmations` names the actual prerequisite ADR as predecessor and explicitly retains its
unit ordering, PROP membership and unaffected milestone policy. The predecessor receives an append-only disposition.
Individual milestones and historical done records are unchanged. No runtime, schema, viewer or integration impact.
No directly linked open source feedback requires resolution and no accepted work is deferred.

Entrypoints: review the derived broad bundle/test candidates against existing ownership. Agent guidance already
owns skills/templates/seed; document model and proposal incubation retain their runtime entrypoints because this
change adds procedural reflection, not runtime behavior. No new broad entrypoints are needed.
