---
id: TASKS-shipped-bundle-citations-and-doc-fixes
spec: SPEC-shipped-bundle-citations-and-doc-fixes
plan: PLAN-shipped-bundle-citations-and-doc-fixes
---

# Task Breakdown: `SPEC-shipped-bundle-citations-and-doc-fixes` Forbid repository document IDs in shipped bundle text and fix two contract gaps

## Phase 1: Citation convention

- [x] **Task 1.1**: The shipped bundle citation test, with its synthetic-bundle check and discovery completeness
  - **_Boundary**: `tools/devkit-dev/tests/integration/test_bundle_citations.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run pytest tools/devkit-dev/tests/integration/test_bundle_citations.py`
- [x] **Task 1.2**: Reword the flagged shipped text and sync its outputs
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/guide.md`,
    `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-06_
  - **Verification**: `uv run pytest tools/devkit-dev/tests/integration/test_bundle_citations.py`, `uv run devkit sync --check`
- [x] **Task 1.3**: State the convention in the authoring instruction and the content package capability
  - **_Boundary**: `packages/devkit/src/devkit_agt/bundles/authoring/bundle/instructions/agent-asset-writing.md`,
    `docs/capabilities/distribution/CAP-DIST-content-packages.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-04, AC-05_
  - **Verification**: `uv run devkit rules check --phase hygiene packages/devkit/src/devkit_agt/bundles/authoring/bundle/instructions/agent-asset-writing.md`

## Phase 2: Contract gaps

- [x] **Task 2.1**: Name the locked restore as the stale local render remedy
  - **_Boundary**: `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`
  - _Requirements: AC-07_
  - **Verification**: `uv run devkit rules check docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`
- [x] **Task 2.2**: Add the moved-base composed acceptance extensions and scenarios to the proposal use case
  - **_Boundary**: `docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md`
  - _Requirements: AC-08_
  - **Verification**: `uv run devkit rules check docs/usecases/delivery/UC-plan-and-hand-off-a-proposal.md`
