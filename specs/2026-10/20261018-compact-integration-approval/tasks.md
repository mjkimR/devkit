---
id: TASKS-compact-integration-approval
spec: SPEC-compact-integration-approval
plan: PLAN-compact-integration-approval
---

# Tasks: Compact native integration approval

- [x] **Task 1**: Add effect-scope and compact result views, optimize all MCP tools, and verify native approval and recovery.
  - **_Boundary**: `packages/devkit/src/devkit/integration/`, `packages/devkit/tests/integration/`, `scripts/smoke_integration.py`
  - _Requirements: AC-01, AC-02, AC-03_
- [x] **Task 2**: Route native approval once and document the four-tool inspection/recovery flow.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundle/AGENTS.md`, `packages/devkit-spec/src/devkit_spec/bundle/skills/spec/`, `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-integrate/`, `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-next/`, `docs/capabilities/integration/CAP-INT-mcp-services.md`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/development/reference/integration.md`
  - _Requirements: AC-04_
- [x] **Task 3**: Verify packaging, consumer smoke and unchanged authority checks.
  - **_Boundary**: `packages/devkit/`, `packages/devkit-spec/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
