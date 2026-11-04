---
id: TASKS-research-local-roles
spec: SPEC-research-local-roles
plan: PLAN-research-local-roles
---

# Task Breakdown

- [x] **Task 1**: Localize research roles and verify deployment and upgrade behavior
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/deep_research/`, `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py`, `packages/devkit-catalog/tests/e2e/bundles/deep_research/`, `packages/devkit-catalog/README.md`, `guides/INSTALL_GUIDE.md`, `guides/install/existing-repository.md`, `docs/capabilities/delivery/CAP-DLV-deep-research.md`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/decisions/2026-11/20261104-skill-local-research-roles.md`, `docs/decisions/2026-11/20261102-adaptive-development-and-research.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test-affected`, catalog lint and type checks, governance and independent review.
