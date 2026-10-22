---
id: TASKS-entrypoints-directory-apply
spec: SPEC-entrypoints-directory-apply
plan: PLAN-entrypoints-directory-apply
---

# Task Breakdown: `SPEC-entrypoints-directory-apply` Apply directory code entrypoints

## Phase 1: Implementation

- [ ] **Task 1.1**: Support directory synthesis and folding for trailing-slash `--code` in entrypoints derivation
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/entrypoints/services/derive.py`, `packages/devkit-spec/src/devkit_spec/features/entrypoints/usecases/derive.py`
  - _Requirements: AC-01, AC-03, AC-04_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/integration/features/entrypoints/test_derive.py`
- [ ] **Task 1.2**: Support directory entrypoint application and collapse in `--apply`
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/entrypoints/usecases/apply.py`, `packages/devkit-spec/tests/integration/features/entrypoints/test_apply.py`
  - _Requirements: AC-02_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/integration/features/entrypoints/test_apply.py`

## Phase 2: Verification

- [ ] **Task 2.1**: End-to-end verification and governance rules check
  - **_Boundary**: `specs/2026-10/20261022-entrypoints-directory-apply/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test-affected && just rules-check`
