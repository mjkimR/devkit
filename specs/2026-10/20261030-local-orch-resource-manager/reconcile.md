---
reconcile_id: REC-local-orch-resource-manager
status: resolved
targets:
  - file: docs/materials/2026-10/20261030-local-orch-resource-manager/20261030-development-evidence.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md
    resolution: modified
  - file: docs/architecture/ARCH-04-1-ecosystem-boundaries.md
    resolution: modified
  - file: docs/steering/glossary.md
    resolution: modified
  - file: docs/decisions/2026-10/20261030-reusable-lifecycle-resource-manager.md
    resolution: modified
---

# Reconciliation: `SPEC-local-orch-resource-manager`

All six blueprint targets, the accepted ADR wording/evidence update and the Development evidence material are reflected. Delivery owns role lifetime,
lean defaults, per-job interface, Host decisions and worker separation. Integration preserves CLI guards and maps
partial effects independently of role status. Both use cases cover reuse, current authority and incomplete effects.
Architecture and glossary separate Host supervision from bounded execution. The ADR's decision is unchanged;
future promotion wording and selected-model evidence limits are repaired.

`MAT-git-operator-development-evidence` retains native read-only Terra continuation and the same-head role-disabled
comparison separately from replay and engine mutation fixtures. No total-token, cost, latency or selected-model
mutation superiority is claimed. Claude/Antigravity live coverage and context-loss/denial paths remain unexercised;
these are verification limits, not deferred required implementation. No new future-work scope or source feedback
was introduced. Lifecycle and distribution engines are unchanged.

Entrypoint derivation added the git-operator contract doorway to the two capabilities and two use cases.
Rejected candidates: the installation receipt, broad bundle directory and test directory are not behavioral
doorways. Existing engine entrypoints remain applicable; no new CLI/API entrypoint exists.

The independent reconcile reviewer found one inventory omission (Development evidence material), corrected above.
The implementer verifies this bounded record correction; the reviewed contracts and implementation are unchanged.
