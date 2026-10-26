---
id: TASKS-list-terminal-statuses-historical
spec: SPEC-list-terminal-statuses-historical
plan: PLAN-list-terminal-statuses-historical
---

# Task Breakdown: `SPEC-list-terminal-statuses-historical` Terminal statuses are historical in document browsing

## Phase 1: Implementation

- [x] **Task 1.1**: Terminal statuses in the index, the list filter with the `--status` override, the hidden count
  and `[HISTORY_CMD: ...]`, search candidates, with integration tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/documents/`, `packages/devkit-spec/tests/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: `just test devkit-spec tests/integration/features/documents`
- [x] **Task 1.2**: Call sites that need settled items pass `--history`
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`, `.devkit/installation.json`
  - _Requirements: AC-08_
  - **Verification**: `uv run devkit sync` and `just rules-check`
- [x] **Task 1.3**: ADR and contracts
  - **_Boundary**: `docs/decisions/2026-10/20261026-terminal-statuses-are-historical.md`,
    `docs/capabilities/documents/`
  - _Requirements: AC-01, AC-03, AC-04_
  - **Verification**: `just rules-check`
