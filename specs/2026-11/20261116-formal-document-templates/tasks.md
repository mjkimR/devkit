---
id: TASKS-formal-document-templates
spec: SPEC-formal-document-templates
plan: PLAN-formal-document-templates
---

# Task Breakdown: `SPEC-formal-document-templates` Template alignment for formal design, domain and operations documents

## Phase 1: Bundle assets

- [x] **Task 1.1**: Revise the design, domain and operations templates, remove the design-template pointer and update the distribution tests and sync outputs
  - **_Boundary**: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/, packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py, packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py, .devkit/installation.json
  - _Requirements: AC-01, AC-02, AC-06, AC-07_
  - **Verification**: `uv run pytest packages/devkit-docs/tests/integration/bundles/docs/test_distribution.py packages/devkit-docs/tests/e2e/bundles/docs/test_installed_consumer.py`
- [x] **Task 1.2**: Revise the design, domain and operations writing instructions
  - **_Boundary**: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/design-writing.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/domain-writing.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/operations-writing.md
  - _Requirements: AC-03_
  - **Verification**: `uv run devkit rules check --phase hygiene packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions`

## Phase 2: Living Spec

- [ ] **Task 2.1**: Reword the capability clause and drop the pointer from the capability, document model and README
  - **_Boundary**: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md, docs/capabilities/documents/CAP-DOCS-document-model.md, packages/devkit-docs/README.md
  - _Requirements: AC-04, AC-06_
  - **Verification**: `rg -n design-template docs/capabilities docs/architecture docs/development packages` exits 1
- [ ] **Task 2.2**: Restructure the five delivered documents to the revised templates
  - **_Boundary**: docs/designs/, docs/domain/, docs/operations/
  - _Requirements: AC-05_
  - **Verification**: `uv run devkit rules check docs/designs docs/domain docs/operations`; `rg -n '^\*\*Reader question|^## Question' docs/designs docs/domain docs/operations` exits 1
