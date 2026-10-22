---
id: TASKS-document-index-cache
spec: SPEC-document-index-cache
plan: PLAN-document-index-cache
---

# Task Breakdown: `SPEC-document-index-cache` Reuse the document index between commands

## Phase 1: Implementation

- [x] **Task 1.1**: Memo codec, entry encoding and parser fingerprint, with unit tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/documents/repositories/memo.py`, `packages/devkit-spec/tests/unit/features/documents/test_memo.py`
  - _Requirements: AC-03, AC-09_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/unit/features/documents/test_memo.py`
- [x] **Task 1.2**: `DocumentIndex.load` reads and writes the memo, with integration tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/documents/repositories/index.py`, `packages/devkit-spec/src/devkit_spec/features/documents/repositories/memo.py`, `packages/devkit-spec/tests/integration/features/documents/test_memo_index.py`
  - _Requirements: AC-01, AC-02, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/documents`

## Phase 2: Verification

- [x] **Task 2.1**: Speed and multi-process evidence, and the repository checks
  - **_Boundary**: `specs/2026-10/20261022-document-index-cache/materials/speed.md`, `docs/capabilities/documents/CAP-DOCS-document-model.md`, `docs/capabilities/documents/CAP-DOCS-document-lookup.md`
  - _Requirements: AC-06, AC-10, AC-11_
  - **Verification**: `uv run devkit rules check`, `just lint devkit-spec`, `just check devkit-spec`, `just test-affected`
