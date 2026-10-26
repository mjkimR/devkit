---
id: TASKS-table-driven-document-kinds
spec: SPEC-table-driven-document-kinds
plan: PLAN-table-driven-document-kinds
---

# Task Breakdown: `SPEC-table-driven-document-kinds` Table-driven document kind definitions

## Phase 1: Implementation

- [ ] **Task 1.1**: Kind definition table, accessors and derived ID grammar, with unit tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/documents/, packages/devkit-spec/tests/unit/features/documents/
  - _Requirements: AC-01, AC-02, AC-06_
  - **Verification**: `just test devkit-spec tests/unit/features/documents`
- [ ] **Task 1.2**: Spec rules, entrypoint paths and the index read the table; fallbacks become explicit lookups, with injected-table tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/governance/, packages/devkit-spec/src/devkit_spec/features/entrypoints/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/, packages/devkit-spec/tests/
  - _Requirements: AC-03, AC-04_
  - **Verification**: `just test-affected`
- [ ] **Task 1.3**: Characterization comparison at the final head
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/, .devkit/installation.json
  - _Requirements: AC-05_
  - **Verification**: `scratch/char/capture.sh after && diff -r -x ws scratch/char/before scratch/char/after`
