---
id: TASKS-foundation-documents
spec: SPEC-foundation-documents
plan: PLAN-foundation-documents
---

# Task Breakdown: `SPEC-foundation-documents` Steering documents for project-wide background

## Phase 1: Implementation

- [x] **Task 1.1**: Manifest `context_documents` field and the get-context `documents` list, with tests
  - **_Boundary**: packages/devkit-dist/src/devkit_dist/features/distribution/, packages/devkit-dist/tests/
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit-dist`
- [x] **Task 1.2**: `RULE-steering-documents` with its guide, manifest asset and tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/governance/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/steering_documents/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml
  - _Requirements: AC-06, AC-07_
  - **Verification**: `uv run devkit rules test packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/steering_documents`
- [x] **Task 1.3**: `RULE-document-reference` reads the moved glossary and resolves IDs cited in steering files; search reads the moved synonyms
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/, packages/devkit-spec/src/devkit_spec/base/, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/, packages/devkit-spec/tests/
  - _Requirements: AC-08, AC-09, AC-10_
  - **Verification**: `just test devkit-spec`
- [x] **Task 1.4**: Spec bundle content: declaration, constitution line, role contracts, seed and guidance paths, with guidance tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/, packages/devkit-spec/tests/, .devkit/installation.json
  - _Requirements: AC-05, AC-11, AC-12_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec` and `uv run devkit sync --check`
- [x] **Task 1.5**: Release handbook script reads either glossary layout, with tests
  - **_Boundary**: scripts/handbook.py, tools/devkit-dev/tests/integration/
  - _Requirements: AC-14_
  - **Verification**: `just test devkit-dev tests/integration/test_handbook_script.py`
- [x] **Task 1.6**: Viewer Steering group, test and rebuilt static page
  - **_Boundary**: packages/devkit-viewer/frontend/src/lib/, packages/devkit-viewer/src/devkit_viewer/static/
  - _Requirements: AC-15_
  - **Verification**: `just viewer test`, `just viewer check`, `just viewer build`
- [x] **Task 1.7**: Move this repository's glossary and update the Living Spec paths
  - **_Boundary**: docs/, guides/
  - _Requirements: AC-13_
  - **Verification**: `uv run devkit rules check` and `uv run devkit get-context spec`
