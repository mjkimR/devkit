---
id: TASKS-mcp-onboarding
spec: SPEC-mcp-onboarding
plan: PLAN-mcp-onboarding
---

# Task Breakdown: `SPEC-mcp-onboarding` MCP onboarding

- [x] **Task 1**: Implement registration inspection, explicit setup and CLI/advisory boundaries with behavior tests.
  - **_Boundary**: `packages/devkit/src/devkit/host/mcp/onboarding.py`, `packages/devkit/src/devkit/host/cli.py`, `packages/devkit/src/devkit/host/errors.py`, `packages/devkit/tests/host/test_mcp_onboarding.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
- [x] **Task 2**: Connect installation routes to optional MCP onboarding and verify the isolated real CLI path.
  - **_Boundary**: `guides/install/mcp.md`, `guides/install/new-repository.md`, `guides/install/existing-repository.md`, `guides/INSTALL_GUIDE.md`
  - _Requirements: AC-05_
