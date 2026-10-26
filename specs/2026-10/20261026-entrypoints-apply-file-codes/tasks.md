---
id: TASKS-entrypoints-apply-file-codes
spec: SPEC-entrypoints-apply-file-codes
plan: PLAN-entrypoints-apply-file-codes
---

# Task Breakdown: `SPEC-entrypoints-apply-file-codes` Entrypoints apply accepts or refuses file codes

## Phase 1: Reproduction

- [ ] **Task 1.1**: Reproduction tests for file, folded and unmatched selectors
  - **_Boundary**: `packages/devkit-spec/tests/integration/features/entrypoints/`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test spec packages/devkit-spec/tests/integration/features/entrypoints/`

## Phase 2: Fix

- [ ] **Task 2.1**: Adopt nested selectors and refuse unmatched ones
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/entrypoints/`, `packages/devkit-spec/src/devkit_spec/base/errors.py`, `packages/devkit-spec/tests/integration/features/entrypoints/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test spec packages/devkit-spec/tests/integration/features/entrypoints/`; `just test-affected`
- [ ] **Task 2.2**: Contract and feedback disposition
  - **_Boundary**: `docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md`, `specs/2026-10/20261026-foundation-documents/feedback/entrypoints-apply-ignores-file-codes.md`
  - _Requirements: AC-01, AC-03_
  - **Verification**: `uv run devkit rules check`
