---
id: TASKS-consolidated-record-length
spec: SPEC-consolidated-record-length
plan: PLAN-consolidated-record-length
---

# Task Breakdown: `SPEC-consolidated-record-length`

## Phase 1: Implementation

- [ ] **Task 1**: Add rule-local eligibility, validation and budget selection with regression coverage.
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/services/builtins/file_length/`, `packages/devkit/tests/integration/features/rules/cli/test_commands.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: rule-owned pytest and rules CLI integration tests; Ruff and Pyright.
- [ ] **Task 2**: Align consumer guidance and opt repository into the bounded budget.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/adr-consolidation/SKILL.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-consolidation/SKILL.md`, `packages/devkit-spec/tests/integration/bundles/spec/`, `docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md`, `docs/development/reference/rules.md`, `docs/decisions/2026-11/20261104-consolidated-record-budgets.md`, `.devkit/config.toml`
  - _Requirements: AC-05_
  - **Verification**: spec bundle-content pytest, sync --check and rules checks.
- [ ] **Task 3**: Record the same-head disabled/enabled outcome by ADR identity.
  - **_Boundary**: `docs/materials/2026-11/20261104-consolidated-record-length/`
  - _Requirements: AC-06_
  - **Verification**: in-memory rule evaluations against the same files with all other settings preserved.
