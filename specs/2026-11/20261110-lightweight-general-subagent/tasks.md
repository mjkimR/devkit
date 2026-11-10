---
id: TASKS-lightweight-general-subagent
spec: SPEC-lightweight-general-subagent
plan: PLAN-lightweight-general-subagent
---

# Task Breakdown: `SPEC-lightweight-general-subagent` Lightweight general subagent for role-file delegation

## Phase 1: Implementation

- [ ] **Task 1**: Ship the `role-worker` contract in the `devkit` bundle's `core` preset, with projection and contract tests
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/bundles/devkit/`, `packages/devkit-dist/tests/integration/features/distribution/test_guide_bundle.py`, `docs/capabilities/distribution/CAP-DIST-agent-projections.md`, `docs/capabilities/distribution/CAP-DIST-content-packages.md`, `docs/decisions/2026-11/20261110-role-worker-subagent.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test devkit-dist packages/devkit-dist/tests/integration/features/distribution/test_guide_bundle.py`; `just test-dist`

- [ ] **Task 2**: Assign subagent types in the deep-research, app-uiux-improve and design-explore orchestration, with catalog tests
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/deep_research/`, `packages/devkit-catalog/src/devkit_catalog/app_uiux_improve/`, `packages/devkit-catalog/src/devkit_catalog/design_explore/`, `packages/devkit-catalog/tests/integration/bundles/`, `docs/capabilities/delivery/CAP-DLV-deep-research.md`, `docs/capabilities/delivery/CAP-DLV-uiux-improvement.md`, `docs/capabilities/delivery/CAP-DLV-design-exploration.md`
  - _Requirements: AC-04, AC-05, AC-06_
  - **Verification**: `just test devkit-catalog packages/devkit-catalog/tests/integration/bundles/`

- [ ] **Task 3**: Make `role-worker` the default skill-local role type in the skill-authoring guidance, with an authoring test
  - **_Boundary**: `packages/devkit/src/devkit_agt/bundles/authoring/bundle/playbooks/skill-authoring/`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`
  - _Requirements: AC-07_
  - **Verification**: `just test devkit packages/devkit/tests/integration/bundles/authoring/test_bundle.py`
