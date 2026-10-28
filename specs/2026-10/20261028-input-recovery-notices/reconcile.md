---
reconcile_id: REC-input-recovery-notices
status: resolved
targets:
  - file: docs/capabilities/integration/CAP-INT-mcp-services.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/development/reference/integration.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
---

# Reconciliation

`SPEC-input-recovery-notices` specializes `INTEGRATION_NOT_READY` input recovery using the session provider's
`SESSION_CLAIMS_INVALID` evidence, with explicit claims on both commands and preserved source/digest/authority checks.
`CAP-INT-mcp-services` reflects the two recovery paths and mixed-failure preservation.

`CAP-DLV-proposal-incubation` documents `SPEC_PROPOSAL_MILESTONE_INACTIVE`, canonical membership, notice-only
review guidance, strict success and unchanged milestone lifecycle. Proposal creation remains the operation's owner.
No use case steps, architecture, terminology, bundle assets or milestone lifecycle contracts change. The optional
`docs/development/reference/spec.md` path does not exist in this checkout. Independent reconciliation found the
existing integration quick reference needed the same recovery distinction; its row now matches the capability.
`CAP-DLV-delivery-workflows` identifies the conditional provider evidence and its claims-recovery purpose. The Host
authorized these two exact documentation boundary additions after the independent findings.

## Source feedback

- `FB-integrate-asks-for-a-new-request-when-claims-are-missing`: resolved by the coded same-command recovery and
  verified retry/digest/source-failure regressions.
- `FB-proposal-new-accepts-a-done-milestone`: resolved within the authorized done/dropped NOTICE scope, verified by
  status/alias and text/JSON/strict regressions without milestone mutation.

No agreed work is deferred.

## Entrypoints

Derived candidates were reviewed. Keep the existing integration feature doorway and add the proposal scaffold
use case doorway to proposal incubation. Reject tests, error models, unrelated cross-capability candidates and
broad proposal directories because they do not identify this operation's reading start.

## Reconciliation verification

The independent review's P1 reference contradiction and P2 conditional-evidence omission were corrected in their
owning documents. At medium effort the implementer checked the exact corrected text against the coded provider
marker, boundary FIX, preserved mixed-source reasons and retained regression outcomes. No implementation changed.
The provider capability retains its existing integration CLI doorway; broader candidates are not needed for this
single evidence description. All four targets are modified in the branch; no waiver is used.
