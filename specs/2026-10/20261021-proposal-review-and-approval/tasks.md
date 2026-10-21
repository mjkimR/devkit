---
id: TASKS-proposal-review-and-approval
spec: SPEC-proposal-review-and-approval
plan: PLAN-proposal-review-and-approval
---

# Task Breakdown: `SPEC-proposal-review-and-approval` Proposal review reports and unified plan-accept MCP approval

## Phase 1: Implementation
- [ ] **Task 1.1**: Source-bound report, approval orchestration, safe integration composition, viewer and review guidance with adversarial tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/, packages/devkit-viewer/src/devkit_viewer/, docs/capabilities/delivery/, docs/capabilities/viewer/, docs/development/reference/, packages/devkit-spec/tests/, packages/devkit-viewer/tests/, packages/devkit-viewer/frontend/, packages/devkit/src/devkit/integration/, packages/devkit/tests/integration/, docs/capabilities/integration/, docs/capabilities/harness/, docs/decisions/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `just test-affected --base main`; package lint/type checks; viewer lint/check/test/build if frontend changes
