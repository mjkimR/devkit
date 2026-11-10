---
reconcile_id: REC-remove-plan-intent-gate
status: pending
targets:
  - file: docs/architecture/ARCH-04-2-delivery-policy.md
    resolution: modified
  - file: docs/architecture/ARCH-04-delivery-strategy.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-proposal-planning.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/decisions/2026-10/20261022-proposal-acceptance.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-delivery-approval-and-lifecycle-authority.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-delivery-classification.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-roadmap-and-milestones-ledger.md
    resolution: modified
  - file: docs/decisions/2026-11/20261102-ux-screens.md
    resolution: modified
  - file: docs/decisions/2026-11/20261110-remove-plan-intent-gate.md
    resolution: modified
  - file: docs/usecases/delivery/UC-drive-development-to-integration.md
    resolution: modified
  - file: docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md
    resolution: modified
  - file: docs/usecases/delivery/UC-route-development-intent.md
    resolution: modified
---

# Reconciliation: `SPEC-remove-plan-intent-gate`

The changed contract removes duplicate task-intent approval while retaining explicit task authorization,
non-gate eligibility, historical records and all later boundaries. Capabilities/use cases/architecture and the
four English handbook pages restate the delivered behavior. The new ADR and five partial pointers were promoted
by handoff; their statement text remains unchanged and agrees with the final contract.

No domain term is introduced or renamed, so the glossary is unchanged. This CLI/guidance change has no product
screen and no UX document. Documentation splitting remains independent Host-owned hygiene work, outside this spec.
No required acceptance criterion is deferred. Runtime legacy-record/custom-gate/policy/size coverage is in
`packages/devkit-spec/tests/integration/bundles/spec/test_workflows.py` and the proposal/policy regressions.

The diagnostic correction in the existing handoff statement error removes a placeholder from actionable FIX text;
its stable error code, target and failure condition remain unchanged. Host authorized it as verification repair.

Entrypoint derivation proposed broad task boundaries and tests. Existing doorway paths remain valid because no
public operation moved or was added; no new pair is applied. Handbook/test/helper candidates are rejected as
non-doorways, and shared feature-directory candidates are rejected as too broad.
