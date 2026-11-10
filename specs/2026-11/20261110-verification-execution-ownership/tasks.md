---
id: TASKS-verification-execution-ownership
spec: SPEC-verification-execution-ownership
plan: PLAN-verification-execution-ownership
---

# Task Breakdown: `SPEC-verification-execution-ownership`

## Phase 1: Implementation

- [x] **Task 1.1**: Separate Host and worker instruction routing and add rendered regression checks.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`, `packages/devkit-spec/tests/integration/bundles/spec/`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: spec bundle tests, lint/types and rules.
- [x] **Task 1.2**: Align repository and portable consumer guidance with the ownership boundary.
  - **_Boundary**: `AGENTS.md`, `tools/devkit-dev/src/devkit_dev/bundle/instructions/testing.md`, `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/test-management/references/execution.md`, `packages/devkit-catalog/tests/integration/bundles/`, `guides/install/verification-ownership.md`, `guides/INSTALL_GUIDE.md`, `guides/install/new-repository.md`, `guides/install/existing-repository.md`
  - _Requirements: AC-02, AC-03, AC-04_
  - **Verification**: maintenance and spec bundle tests; guide link and contract review.
- [x] **Task 1.3**: Reconcile the cross-bundle ownership decision and capability contracts.
  - **_Boundary**: `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/capabilities/delivery/CAP-DLV-test-management.md`, `docs/decisions/2026-11/20261110-verification-execution-ownership.md`, `specs/2026-11/20261110-verification-execution-ownership/`
  - _Requirements: AC-05_
  - **Verification**: independent reconciliation review, document rules and affected checks.
