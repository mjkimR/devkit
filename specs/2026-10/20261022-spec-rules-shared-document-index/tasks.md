---
id: TASKS-spec-rules-shared-document-index
spec: SPEC-spec-rules-shared-document-index
plan: PLAN-spec-rules-shared-document-index
---

# Task Breakdown: `SPEC-spec-rules-shared-document-index` Share one document index across a rules run

## Phase 1: Core Cache Slot & Markdown Link Optimization

- [x] **Task 1**: Implement `get_or_compute` on `WorkspaceCache` and test invalidation
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py`, `packages/devkit/tests/integration/features/rules/workspace/test_cache.py`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `uv run pytest packages/devkit/tests/integration/features/rules/workspace/test_cache.py`

- [x] **Task 2**: Defer `DocumentCatalog` building in `MarkdownLinkRule`
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/services/builtins/markdown_link/rule.py`, `packages/devkit/src/devkit_agt/features/rules/services/builtins/markdown_link/tests/test_rule.py`
  - _Requirements: AC-03, AC-04_
  - **Verification**: `uv run pytest packages/devkit/src/devkit_agt/features/rules/services/builtins/markdown_link/tests/test_rule.py`

## Phase 2: Spec Rules In-Process Index Sharing

- [x] **Task 3**: Share `DocumentIndex` across spec rules via `WorkspaceCache.get_or_compute`
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/governance/services/documents.py`, `packages/devkit-spec/tests/unit/features/governance/test_documents.py`
  - _Requirements: AC-01, AC-02, AC-05_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/unit/features/governance/test_documents.py`

## Phase 3: Documentation & Verification

- [x] **Task 4**: Reconcile Living Spec contracts for rules engine and spec rules
  - **_Boundary**: `docs/capabilities/governance/CAP-GOV-rules-engine.md`, `docs/capabilities/governance/CAP-GOV-spec-rules.md`
  - _Requirements: AC-01, AC-03_
  - **Verification**: `just rules-check`
