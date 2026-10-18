---
reconcile_id: REC-backlog-roadmap-and-issues
feature: SPEC-backlog-roadmap-and-issues
status: resolved
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
    resolution: modified
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
    resolution: modified
  - file: docs/capabilities/governance/CAP-GOV-spec-rules.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/stories/delivery/US-route-development-intent.md
    resolution: modified
  - file: docs/architecture/ARCH-01-introduction-and-goals.md
    resolution: modified
  - file: docs/decisions/2026-10/20261018-roadmap-in-repository.md
    resolution: modified
  - file: docs/decisions/2026-10/20261018-milestone-documents.md
    resolution: modified
  - file: docs/proposals/PROP-draft-direct-acceptance/proposal.md
    resolution: modified
---

# Reconciliation: Repository roadmap and Backlog

The implementation extends document identity/history, relation validation, authoring/provenance and member advisories.
Existing capabilities and the routing story describe the contract; promoted decisions preserve the accepted direction.
The direct-acceptance draft now names the implemented spec as its origin and dependency. README/template/seed updates
mirror these contracts. No tracker field or integration is introduced.

Retained follow-up: `PROP-draft-direct-acceptance` owns Planning-free draft acceptance; its scope remains separate.
Expected task boundaries were extended for seeded root roadmap docs, installation receipt and the quick README reference.

Entrypoint candidates were inspected; broad declaration joins and already-covered paths were rejected.
Only CAP-GOV-spec-rules gained the hygiene.py entrypoint that it owns.
