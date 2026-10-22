---
id: TASKS-lint-clean-target-scoped-rules
spec: SPEC-lint-clean-target-scoped-rules
plan: PLAN-lint-clean-target-scoped-rules
---

# Task Breakdown: `SPEC-lint-clean-target-scoped-rules` Scope target runs to the rules their targets can affect

## Phase 1: Engine

- [x] **Task 1.1**: `inputs` declaration and its validation, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/models/errors.py`, `packages/devkit/src/devkit_agt/features/rules/models/policy.py`, `packages/devkit/src/devkit_agt/features/rules/services/builtins/base.py`, `packages/devkit/src/devkit_agt/features/rules/usecases/project.py`, `packages/devkit/tests/unit/features/rules/`, `packages/devkit/tests/integration/features/rules/engine/`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test agt packages/devkit/tests/unit/features/rules packages/devkit/tests/integration/features/rules/engine`
- [x] **Task 1.2**: Scoping in `evaluate_rules`, `skipped` on the results, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/models/contracts.py`, `packages/devkit/src/devkit_agt/features/rules/services/evaluator.py`, `packages/devkit/src/devkit_agt/features/rules/usecases/project.py`, `packages/devkit/src/devkit_agt/features/rules/__init__.py`, `packages/devkit/tests/unit/features/rules/`, `packages/devkit/tests/integration/features/rules/engine/`
  - _Requirements: AC-03, AC-04, AC-05_
  - **Verification**: `just test agt packages/devkit/tests/unit/features/rules packages/devkit/tests/integration/features/rules/engine`
- [x] **Task 1.3**: `devkit rules explain` shows `inputs`, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/usecases/explain.py`, `packages/devkit/src/devkit_agt/features/rules/cli/output.py`, `packages/devkit/tests/integration/features/rules/cli/test_commands.py`
  - _Requirements: AC-07_
  - **Verification**: `just test agt packages/devkit/tests/integration/features/rules/cli/test_commands.py`

## Phase 2: Declared rules

- [x] **Task 2.1**: Open-file recording for rule tests, and the three rules' declarations, guides and tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/services/testing.py`, `tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/`, `tools/devkit-dev/src/devkit_dev/bundle/rules/usecase-boundaries/`, `packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/`, `.devkit/installation.json`, `packages/devkit/tests/integration/features/rules/engine/`
  - _Requirements: AC-06, AC-08_
  - **Verification**: `uv run devkit rules test RULE-architecture RULE-usecase-boundaries RULE-advisory-unique-code`; `uv run devkit sync --check`

## Phase 3: Documentation and evidence

- [ ] **Task 3.1**: Rule authoring guidance and the reference
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-rule/`, `docs/capabilities/governance/`, `docs/development/reference/rules.md`, `.devkit/installation.json`
  - _Requirements: AC-07_
  - **Verification**: `uv run devkit rules check docs/capabilities/governance docs/development/reference/rules.md packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-rule`; `just test agt packages/devkit/tests/integration/features/rules/test_docs.py packages/devkit/tests/integration/package/test_documented_codes.py`
- [ ] **Task 3.2**: Equivalence, performance and boundary evidence
  - **_Boundary**: `specs/2026-10/20261022-lint-clean-target-scoped-rules/evidence.md`
  - _Requirements: AC-09, AC-10, AC-11_
  - **Verification**: `uv run devkit rules check specs/2026-10/20261022-lint-clean-target-scoped-rules`; `uv run devkit rules check`
