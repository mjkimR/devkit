---
reconcile_id: REC-incubation-lifecycle-policy
status: pending
targets:
- file: docs/architecture/ARCH-05-2-components.md
  resolution: modified
- file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
  resolution: modified
- file: docs/capabilities/delivery/CAP-DLV-project-policy.md
  resolution: modified
- file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
  resolution: modified
- file: docs/capabilities/delivery/CAP-DLV-spec-bundles.md
  resolution: modified
- file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
  resolution: modified
- file: docs/capabilities/governance/CAP-GOV-rules-engine.md
  resolution: modified
- file: docs/capabilities/governance/CAP-GOV-spec-rules.md
  resolution: modified
- file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
  resolution: modified
- file: docs/capabilities/integration/CAP-INT-mcp-services.md
  resolution: modified
- file: docs/decisions/2026-10/20261028-own-development-approach-policy-outside-sdd.md
  resolution: modified
- file: docs/steering/glossary.md
  resolution: modified
- file: docs/usecases/delivery/UC-route-development-intent.md
  resolution: modified
---

# Reconciliation

The shared approach owner, effective inspection, inactive mutations, explicit lifecycle omissions, retained binding
ownership and independent project provider are reflected in their owning capability contracts. Routing use case,
architecture, glossary, package READMEs and installation guidance agree with the implementation.

Code review findings were fixed and independently reverified. Tests: affected full fallback 5898 passed,14 skipped;
dist-only1271 passed; installed document-only consumer proves common inspection and actual project readiness without
devkit-spec; official smoke passed. The project retains the default SDD approach.

## Remaining milestone work

`PROP-incubation-development-guidance` owns the incubation entry/roles/context; `PROP-incubation-sdd-baseline` owns baseline adoption.
Those explicitly excluded features are in separate Host-coordinated worktrees; this spec claims no milestone
completion. Host will incorporate their final identifiers at integration.

## Entrypoints

Common config inspection retains its existing CLI/use-case doorway. New project readiness is an alternate installed
provider doorway under the existing integration CLI, with SDD-specific judgments remaining in spec. Broad package,
model, test and guide candidates are not operational entrypoints.
