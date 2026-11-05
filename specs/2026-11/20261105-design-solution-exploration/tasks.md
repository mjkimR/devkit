---
id: TASKS-design-solution-exploration
spec: SPEC-design-solution-exploration
plan: PLAN-design-solution-exploration
---

# Task Breakdown: `SPEC-design-solution-exploration`

- [ ] **Task 1**: Add opt-in content bundle, registration and focused deployment/instruction tests.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/design_explore/`, `packages/devkit-catalog/pyproject.toml`, `packages/devkit-catalog/tests/integration/bundles/test_design_explore.py`, `.devkit/architecture.toml`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: focused catalog integration tests; lint, types and governance checks.
  - **Scope rationale**: architecture configuration changes only the Host-authorized design_explore catalog data root.
- [ ] **Task 2**: Verify built-wheel consumer lifecycle without delivery packages.
  - **_Boundary**: `packages/devkit-catalog/tests/e2e/bundles/design_explore/`
  - _Requirements: AC-01, AC-06_
  - **Verification**: installed consumer wheel lifecycle test; just test-affected preserves full fallback.

Living Spec stage targets: `docs/capabilities/delivery/CAP-DLV-design-exploration.md`,
`docs/usecases/delivery/UC-explore-a-design-problem.md`, `docs/architecture/ARCH-05-2-components.md`,
`docs/decisions/2026-11/20261105-explicit-solution-exploration.md`, `packages/devkit-catalog/README.md`,
`guides/install/bundle-recommendations.md`. Unit records remain within this spec directory.
