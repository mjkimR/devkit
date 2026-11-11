---
id: TASKS-mcp-tool-execution-classes
spec: SPEC-mcp-tool-execution-classes
plan: PLAN-mcp-tool-execution-classes
---

# Task Breakdown: `SPEC-mcp-tool-execution-classes` Two MCP tool execution classes

## Phase 1: Implementation
- [ ] **Task 1.1**: Narrow `McpTool.execution`, derive the read-only hint and update the producer and tests
  - **_Boundary**: `packages/devkit-core/src/devkit_core/base/mcp.py`, `packages/devkit-mcp/src/devkit_mcp/features/runtime/mcp/server.py`, `packages/devkit-dist/src/devkit_dist/features/shared/mcp.py`, `packages/devkit-mcp/tests/integration/features/runtime/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit-mcp`, `just test-dist`

## Phase 2: Living Spec
- [ ] **Task 2.1**: State the two classes in the capability
  - **_Boundary**: `docs/capabilities/mcp/CAP-MCP-runtime-registration.md`
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit rules check`
