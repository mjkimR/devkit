---
id: TASKS-delivery-document-hygiene
spec: SPEC-delivery-document-hygiene
plan: PLAN-delivery-document-hygiene
---

# Task Breakdown: `SPEC-delivery-document-hygiene`

- [x] **Task 1**: Partition the delivery capabilities and retain a section relocation map.
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/capabilities/delivery/CAP-DLV-delivery-roles.md`, `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`, `docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md`, `specs/2026-11/20261110-delivery-document-hygiene/`
  - _Requirements: AC-01, AC-02_
  - **Verification**: line counts, mechanical section comparison, document rules and independent review.
- [x] **Task 2**: Repair exact current references and backlinks admitted by the Host.
  - **_Boundary**: `docs/architecture/ARCH-04-1-ecosystem-boundaries.md`,
    `docs/architecture/ARCH-04-delivery-strategy.md`,
    `docs/architecture/ARCH-06-runtime-view.md`,
    `docs/capabilities/delivery/CAP-DLV-adaptive-development.md`,
    `docs/capabilities/delivery/CAP-DLV-cli-and-output.md`,
    `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`,
    `docs/capabilities/delivery/CAP-DLV-maintenance-history.md`,
    `docs/capabilities/delivery/CAP-DLV-project-policy.md`,
    `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`,
    `docs/capabilities/delivery/CAP-DLV-spec-bundles.md`,
    `docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md`,
    `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`,
    `docs/capabilities/documents/CAP-DOCS-document-lookup.md`,
    `docs/capabilities/documents/CAP-DOCS-document-model.md`,
    `docs/capabilities/documents/CAP-DOCS-namespaces.md`,
    `docs/capabilities/harness/CAP-HARN-agent-guidance.md`,
    `docs/capabilities/harness/CAP-HARN-command-mount.md`,
    `docs/capabilities/host/CAP-HOST-lifecycle-observation.md`,
    `docs/capabilities/integration/CAP-INT-mcp-services.md`,
    `docs/capabilities/worktree/CAP-WT-task-worktrees.md`,
    `docs/decisions/2026-10/20261007-dual-source-of-truth-and-periodic-reconciliation.md`,
    `docs/decisions/2026-10/20261022-document-id-aliases.md`,
    `docs/decisions/2026-10/20261022-proposal-acceptance.md`,
    `docs/decisions/2026-11/20261102-adaptive-development-and-research.md`,
    `docs/decisions/2026-11/20261102-delivery-approval-and-lifecycle-authority.md`,
    `docs/decisions/2026-11/20261102-delivery-classification.md`,
    `docs/decisions/2026-11/20261102-document-system.md`,
    `docs/decisions/2026-11/20261102-local-and-pull-request-integration.md`,
    `docs/decisions/2026-11/20261102-orchestration-workers.md`,
    `docs/decisions/2026-11/20261102-proposal-handoff.md`,
    `docs/decisions/2026-11/20261102-retire-native-approval-and-moved-ownership-clauses.md`,
    `docs/decisions/2026-11/20261102-review-loop.md`,
    `docs/decisions/2026-11/20261102-roadmap-and-milestones-ledger.md`,
    `docs/decisions/2026-11/20261102-ux-screens.md`,
    `docs/decisions/2026-11/20261102-worktrees-and-scope.md`,
    `docs/decisions/2026-11/20261104-namespace-milestone-roots.md`,
    `docs/decisions/2026-11/20261104-namespace-steering-registers.md`,
    `docs/decisions/2026-11/20261104-post-merge-verification.md`,
    `docs/decisions/2026-11/20261104-recorded-adjacent-path-extensions-for-development-workers.md`,
    `docs/decisions/2026-11/20261110-partial-supersession-statements.md`,
    `docs/decisions/2026-11/20261110-remove-plan-intent-gate.md`,
    `docs/decisions/2026-11/20261110-verification-execution-ownership.md`,
    `docs/usecases/delivery/UC-drive-development-to-integration.md`,
    `docs/usecases/delivery/UC-handle-delivery-problems-and-exceptions.md`,
    `docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md`,
    `docs/usecases/delivery/UC-route-development-intent.md`
  - _Requirements: AC-02_
  - **Verification**: edits limited to the Host's exact link/trace list; no decision or behavior change.
- [x] **Task 3**: Trim duplicate reference configuration and correct the repeated scenario number.
  - **_Boundary**: `docs/development/reference/distribution.md`, `docs/usecases/delivery/UC-drive-development-to-integration.md`
  - _Requirements: AC-03, AC-04_
  - **Verification**: unique diagnostics/examples and scenario preservation, affected tests and hygiene report.
