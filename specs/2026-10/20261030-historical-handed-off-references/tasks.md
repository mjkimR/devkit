---
id: TASKS-historical-handed-off-references
spec: SPEC-historical-handed-off-references
plan: PLAN-historical-handed-off-references
---

# Task Breakdown: `SPEC-historical-handed-off-references` Accept handed-off proposal IDs in work history

## Phase 1: Implementation

- [x] **Task 1.1**: Regression tests for handed-off proposals in history, live documents and unknown proposals
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test devkit-docs src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`
- [x] **Task 1.2**: Accept a handed-off proposal in history in the rule, with its guide and contract text, synced
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/usecases/document_reference.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/guide.md`,
    `docs/capabilities/governance/CAP-GOV-spec-rules.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: the Task 1.1 tests, `uv run devkit sync --check`, and
    `uv run devkit rules check specs/2026-10/20261030-integration-merge-moved-target` reporting `errors=0`
