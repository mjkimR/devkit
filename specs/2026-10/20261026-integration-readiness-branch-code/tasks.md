---
id: TASKS-integration-readiness-branch-code
spec: SPEC-integration-readiness-branch-code
plan: PLAN-integration-readiness-branch-code
---

# Task Breakdown: `SPEC-integration-readiness-branch-code` Integration readiness loads branch rules with branch code

## Phase 1: Reproduce

- [ ] **Task 1.1**: Regression test reproducing the refusal with the real `spec` provider
  - **_Boundary**: packages/devkit-spec/tests/e2e/features/delivery/test_integration_rule_runtime.py
  - _Requirements: AC-01, AC-03, AC-04_
  - **Verification**: `just test devkit-spec tests/e2e/features/delivery/test_integration_rule_runtime.py`

## Phase 2: Fix

- [ ] **Task 2.1**: Rule runtime diagnosis before the readiness provider, with its error and tests
  - **_Boundary**: packages/devkit/src/devkit_agt/features/integration/, packages/devkit/tests/integration/features/integration/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit tests/integration/features/integration`
- [ ] **Task 2.2**: Contracts and quick reference name the code and the evaluation runtime
  - **_Boundary**: docs/capabilities/integration/CAP-INT-mcp-services.md, docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md, docs/usecases/delivery/UC-drive-development-to-integration.md, docs/development/reference/integration.md, specs/2026-10/20261026-foundation-documents/feedback/integration-readiness-loads-new-rule-with-base-code.md
  - _Requirements: AC-01, AC-02_
  - **Verification**: `uv run devkit rules check --ci --base main`
