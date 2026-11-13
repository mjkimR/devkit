---
id: TASKS-linter-change-notices
spec: SPEC-linter-change-notices
plan: PLAN-linter-change-notices
---

# Task Breakdown: `SPEC-linter-change-notices`

- [x] **Task 1**: Add immutable change evidence and exact source capture with semantic/deletion and autofix tests.
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/`, `packages/devkit/tests/unit/features/rules/`, `packages/devkit/tests/integration/features/rules/`
  - _Requirements: AC-01, AC-02, AC-05, AC-09, AC-10_
  - **Verification**: focused change-evidence and snapshot integration tests.
- [x] **Task 2**: Add NOTICE severity, policy/phase/output compatibility and gate notice delivery.
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/`, `packages/devkit/src/devkit_agt/features/gate/usecases/gates/rules.py`, `packages/devkit/src/devkit_agt/features/gate/models/errors.py`, `packages/devkit/tests/unit/features/rules/`, `packages/devkit/tests/integration/features/rules/`, `packages/devkit/tests/integration/features/gate/`, `packages/devkit/tests/integration/features/workflow/`, `packages/devkit/tests/e2e/features/gate/`
  - _Requirements: AC-03, AC-04, AC-06, AC-08_
  - **Verification**: evaluator/policy/CLI/gate/workflow tests, selected gate E2E.
- [x] **Task 3**: Implement bounded explicit read companion and transient session suppression with failure tests.
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/`, `packages/devkit/tests/unit/features/rules/`, `packages/devkit/tests/integration/features/rules/`
  - _Requirements: AC-07, AC-09_
  - **Verification**: context command and memo integration tests.
- [x] **Task 4**: Restate shipped rule contracts and command usage.
  - **_Boundary**: `packages/devkit/README.md`, `docs/capabilities/governance/CAP-GOV-rules-engine.md`, `docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md`, `docs/capabilities/governance/CAP-GOV-rule-authoring.md`, `docs/capabilities/gate/CAP-GATE-commit-gates.md`, `docs/development/reference/rules.md`, `docs/decisions/2026-11/20261113-change-scoped-rule-notices.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10_
  - **Verification**: document rules and reconcile comparison.
