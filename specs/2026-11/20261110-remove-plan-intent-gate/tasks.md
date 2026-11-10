---
id: TASKS-remove-plan-intent-gate
spec: SPEC-remove-plan-intent-gate
plan: PLAN-remove-plan-intent-gate
---

# Task Breakdown: `SPEC-remove-plan-intent-gate`

- [x] **Task 1**: Remove SDD intent declarations and align agent guidance, with deployed-workflow regressions.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/AGENTS.md.jinja`, `packages/devkit-spec/tests/integration/bundles/`, `packages/devkit-spec/tests/e2e/bundles/`, `packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-03, AC-05_
  - **Verification**: workflow validation, legacy-record evaluation/rules, guidance tests.
- [x] **Task 2**: Simplify acceptance, handoff and policy, retaining acceptance authority and custom gates.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/`, `packages/devkit-spec/src/devkit_spec/features/delivery/`, `packages/devkit-spec/src/devkit_spec/features/policy/`, `packages/devkit-spec/src/devkit_spec/base/errors.py`, `packages/devkit-spec/tests/integration/features/`, `packages/devkit-spec/tests/e2e/features/`, `packages/devkit-spec/tests/support/`
  - _Requirements: AC-02, AC-04_
  - **Verification**: acceptance/handoff/policy regressions and selective native E2E.
- [x] **Task 3**: Update delivery contracts and handbook authorization wording.
  - **_Boundary**: `docs/capabilities/delivery/`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/usecases/delivery/`, `docs/architecture/ARCH-04-delivery-strategy.md`, `docs/architecture/ARCH-04-2-delivery-policy.md`, `handbook/en/concepts.md`, `handbook/en/areas/delivery.md`, `handbook/en/journeys/route-development-intent.md`, `handbook/en/journeys/plan-and-hand-off-a-proposal.md`
  - _Requirements: AC-05_
  - **Verification**: document rules and contract comparison.
