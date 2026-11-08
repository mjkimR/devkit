---
id: TASKS-adaptive-task-contracts
spec: SPEC-adaptive-task-contracts
plan: PLAN-adaptive-task-contracts
---

# Task Breakdown: `SPEC-adaptive-task-contracts`

## Implementation

- [ ] **Task 1**: Strengthen bounded assignment and role guidance with representative contract review.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/references/delegation.md`, `packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/references/orchestration.md`, `packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/skills/adaptive-dev/roles/`, `packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle/subagents/swarm-planner.md`, `packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: Review three assignment fixtures and four overlays, then run catalog asset checks and `just test-affected`.
