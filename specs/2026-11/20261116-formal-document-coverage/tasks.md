---
id: TASKS-formal-document-coverage
spec: SPEC-formal-document-coverage
plan: PLAN-formal-document-coverage
---

# Task Breakdown: `SPEC-formal-document-coverage` Formal document coverage across capability areas

## Phase 1: Documents

- [x] **Task 1.1**: Unit A, delivery: workflow stage evaluation design and assignment attention routing
  - **_Boundary**: `docs/designs/delivery/DESIGN-workflow-stage-evaluation/`, `docs/operations/OPS-assignment-attention-routing.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `uv run devkit rules check --ci --base main`
- [x] **Task 1.2**: Unit B, host and mcp: host hook dispatch routing and MCP runtime refusals
  - **_Boundary**: `docs/operations/OPS-host-hook-dispatch-routing.md`, `docs/operations/OPS-mcp-runtime-refusals.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `uv run devkit rules check --ci --base main`
- [x] **Task 1.3**: Unit C, distribution and search: override lifecycle domain and search mode routing
  - **_Boundary**: `docs/domain/distribution/DOMAIN-override-lifecycle.md`, `docs/operations/OPS-search-mode-and-model-routing.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: `uv run devkit rules check --ci --base main`
