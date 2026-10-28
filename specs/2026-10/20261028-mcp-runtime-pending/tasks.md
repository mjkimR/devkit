---
id: TASKS-mcp-runtime-pending
spec: SPEC-mcp-runtime-pending
plan: PLAN-mcp-runtime-pending
---

# Task Breakdown: `SPEC-mcp-runtime-pending`

- [x] **Task 1**: Delete speculative general-status registration reporting and obsolete helpers, with focused absence/preservation regression tests.
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/host/`, `packages/devkit-dist/src/devkit_dist/features/distribution/`, `packages/devkit-dist/tests/integration/features/host/`, `packages/devkit-dist/tests/integration/features/distribution/`, `docs/capabilities/mcp/CAP-MCP-runtime-registration.md`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `docs/development/reference/distribution.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: Focused registration/output tests, `just lint-check dist`, `just check dist`, `just test-affected`, `just test-dist` and committed governance checks.
