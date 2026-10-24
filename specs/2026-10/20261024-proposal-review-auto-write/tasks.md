---
id: TASKS-proposal-review-auto-write
spec: SPEC-proposal-review-auto-write
plan: PLAN-proposal-review-auto-write
---

# Task Breakdown: `SPEC-proposal-review-auto-write` Publish proposal review before acceptance

## Phase 1: Implementation

- [x] **Task 1**: Add typed proposal-review configuration and report effective policy
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/policy/models/config.py`, `packages/devkit-spec/src/devkit_spec/features/policy/services/config.py`, `packages/devkit-spec/src/devkit_spec/features/policy/usecases/inspect.py`, `packages/devkit-spec/src/devkit_spec/features/policy/cli/commands.py`, `packages/devkit-spec/tests/integration/features/policy/`
  - _Requirements: AC-03_
  - **Verification**: `just test devkit-spec tests/unit/features/policy tests/e2e/features/delivery`
- [x] **Task 2**: Publish the proposal report once before acceptance and document both configuration paths
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/SKILL.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/sdd-proposal.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_proposal_review_report_guidance.py`, `docs/capabilities/delivery/CAP-DLV-proposal-incubation.md`, `docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md`
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: focused bundle asset tests and proposal report / acceptance tests via `just test-affected`
