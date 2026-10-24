---
id: TASKS-proposal-review-auto-write
spec: SPEC-proposal-review-auto-write
plan: PLAN-proposal-review-auto-write
---

# Task Breakdown: `SPEC-proposal-review-auto-write` Publish proposal review before acceptance

## Phase 1: Implementation

- [x] **Task 1**: Add typed proposal-review configuration and report effective policy
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/policy/`, `packages/devkit-spec/tests/unit/features/policy/`, `packages/devkit-spec/src/devkit_spec/features/delivery/cli/`, related CLI tests
  - _Requirements: AC-03_
  - **Verification**: `just test devkit-spec tests/unit/features/policy tests/e2e/features/delivery`
- [x] **Task 2**: Publish the proposal report once before acceptance and document both configuration paths
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/`, proposal acceptance workflow assets, `packages/devkit-spec/tests/`, `docs/capabilities/delivery/CAP-DLV-proposal-incubation.md`, `docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md`
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: focused bundle asset tests and proposal report / acceptance tests via `just test-affected`
