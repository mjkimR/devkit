---
reconcile_id: REC-document-bundle-split
status: pending
targets:
- file: docs/architecture/ARCH-05-2-components.md
  resolution: modified
- file: docs/architecture/ARCH-07-deployment.md
  resolution: modified
- file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  resolution: modified
- file: docs/capabilities/documents/CAP-DOCS-document-model.md
  resolution: modified
- file: docs/capabilities/governance/CAP-GOV-spec-rules.md
  resolution: modified
- file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
  resolution: modified
- file: docs/steering/glossary.md
  resolution: modified
- file: docs/usecases/harness/UC-adopt-in-an-existing-repository.md
  resolution: modified
- file: docs/ux/README.md
  resolution: modified
- file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
  resolution: waived
  rationale: Existing command and skeleton contracts use no moved shared-template
    path; proposal template remains spec-owned and runtime behavior is unchanged.
- file: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
  resolution: waived
  rationale: Existing command and skeleton contracts use no moved shared-template
    path; proposal template remains spec-owned and runtime behavior is unchanged.
- file: docs/decisions/2026-10/20261028-document-and-sdd-bundles.md
  resolution: modified
---

# Reconciliation

Shared document assets and SDD lifecycle guidance have separate owners under `ADR-document-and-sdd-bundles`.
The capability, architecture, installation and quick-reference changes match AC-01 through AC-06.

## Deferred milestone work

Runtime lifecycle policy, incubation development guidance and optional baseline transition remain outside this spec.
The Host owns their follow-up draft proposals on the retained base and will link the destinations during integration.
This branch has not merged the advanced base; it claims no milestone completion.

## Review and verification

Independent medium code review found two stale consumer references. The implementer repaired them under Host-approved
exact scope extensions and verified the official consumer smoke. Full affected fallback: 5879 passed, 14 skipped.
Document-only built-wheel smoke, selection round trip and seeded-byte preservation passed.

Entrypoint review retained the docs manifest as the document-distribution doorway. Broad package, test, guide and
configuration candidates were rejected because they are not doorways to the affected behavior. Existing lifecycle
entrypoints remain valid.
