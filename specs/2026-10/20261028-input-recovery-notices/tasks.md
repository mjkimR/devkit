---
id: TASKS-input-recovery-notices
spec: SPEC-input-recovery-notices
plan: PLAN-input-recovery-notices
summary: "Implement and verify integration claim recovery and nonblocking inactive milestone membership notices."
---

# Tasks

- [ ] **Task 1**: Specialize missing session claim recovery and retain integration regression coverage.
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/integration/`, `packages/devkit/tests/integration/features/integration/`, `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/integration.py`, `packages/devkit-spec/tests/integration/features/delivery/`, `docs/capabilities/integration/CAP-INT-mcp-services.md`, `specs/2026-10/feedback/20261027-integrate-asks-for-a-new-request-when-claims-are-missing.md`
  - _Requirements: AC-01, AC-02_
  - **Verification**: Integration CLI and readiness integration suites.

- [ ] **Task 2**: Return a NOTICE for done/dropped milestone membership with proposal/CLI regression coverage.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/`, `packages/devkit-spec/src/devkit_spec/base/errors.py`, `packages/devkit-spec/tests/integration/features/proposals/`, `packages/devkit-spec/tests/integration/package/test_documented_codes.py`, `docs/capabilities/delivery/CAP-DLV-proposal-incubation.md`, `docs/development/reference/spec.md`, `docs/proposals/PROP-performance-pass/feedback/proposal-new-accepts-a-done-milestone.md`
  - _Requirements: AC-03, AC-04_
  - **Verification**: Proposal roadmap and CLI integration suites, including aliases, strict, JSON and unchanged milestone bytes.
