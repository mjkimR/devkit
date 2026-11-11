---
id: TASKS-shared-fingerprinted-memo
spec: SPEC-shared-fingerprinted-memo
plan: PLAN-shared-fingerprinted-memo
---

# Task Breakdown: `SPEC-shared-fingerprinted-memo` One fingerprinted memo store for docs parse and rule facts

## Phase 1: Evidence before the change

- [x] **Task 1.1**: Differential fixture harness and its "before" table on the handoff head
  - **_Boundary**: `specs/2026-11/20261111-shared-fingerprinted-memo/evidence/memo_harness.py`,
    `specs/2026-11/20261111-shared-fingerprinted-memo/evidence/before.md`
  - _Requirements: AC-03, AC-04_
  - **Verification**: `uv run python specs/2026-11/20261111-shared-fingerprinted-memo/evidence/memo_harness.py tmp/probe/harness-before`

## Phase 2: Shared helper

- [x] **Task 2.1**: `devkit_core.core.memo` with `safe_memo_path` and `envelope_problem`, and their unit tests
  - **_Boundary**: `packages/devkit-core/src/devkit_core/core/memo.py`,
    `packages/devkit-core/tests/unit/core/test_memo.py`, `packages/devkit-core/tests/integration/core/test_memo.py`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test devkit-core`

## Phase 3: Memo adoption

- [x] **Task 3.1**: The docs parse memo uses the helper, with the `.devkit/` symlink test
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/documents/repositories/memo.py`,
    `packages/devkit-docs/tests/unit/features/documents/test_memo.py`,
    `packages/devkit-docs/tests/integration/features/documents/test_memo_index.py`
  - _Requirements: AC-03, AC-05_
  - **Verification**: `just test devkit-docs`
- [x] **Task 3.2**: The rule facts memo uses the helper and fingerprints its source, with the extra-key test
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/facts.py`,
    `packages/devkit/tests/integration/features/rules/workspace/test_file_facts.py`
  - _Requirements: AC-04, AC-05_
  - **Verification**: `uv run pytest packages/devkit/tests/integration/features/rules/workspace/test_file_facts.py`
- [x] **Task 3.3**: "After" table compared with "before"
  - **_Boundary**: `specs/2026-11/20261111-shared-fingerprinted-memo/evidence/after.md`
  - _Requirements: AC-03, AC-04_
  - **Verification**: `uv run python specs/2026-11/20261111-shared-fingerprinted-memo/evidence/memo_harness.py tmp/probe/harness-after`

## Phase 4: Living Spec

- [x] **Task 4.1**: Converged path and envelope rule in both capability contracts
  - **_Boundary**: `docs/capabilities/documents/CAP-DOCS-document-model.md`,
    `docs/capabilities/governance/CAP-GOV-rules-engine.md`
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit rules check --ci --base main`
