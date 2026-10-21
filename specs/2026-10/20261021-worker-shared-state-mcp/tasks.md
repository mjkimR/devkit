---
id: TASKS-worker-shared-state-mcp
spec: SPEC-worker-shared-state-mcp
plan: PLAN-worker-shared-state-mcp
---

# Task Breakdown: `SPEC-worker-shared-state-mcp`

- [ ] **Task 1**: Immutable local artifact API, registration and safety with conformance and filesystem tests
  - **_Boundary**: packages/devkit-dist/src/devkit/shared/, packages/devkit-dist/src/devkit/core/, packages/devkit-dist/tests/, packages/devkit-dist/pyproject.toml
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-06_
- [ ] **Task 2**: CLI and MCP parity, owning-workspace configuration and bounded-write guard tests
  - **_Boundary**: packages/devkit-dist/src/devkit/cli.py, packages/devkit-dist/src/devkit/shared/, packages/devkit-dist/src/devkit/core/, packages/devkit-dist/src/devkit/host/, packages/devkit-dist/tests/, packages/devkit-mcp/src/, packages/devkit-mcp/tests/
  - _Requirements: AC-01, AC-05, AC-06_
- [ ] **Task 3**: Consumer guidance, public extension documentation and layering inventory
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/skills/spec-orchestrate/SKILL.md, packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/references/hosts.md, packages/devkit-spec/tests/, packages/devkit-dist/README.md, packages/devkit-mcp/README.md, AGENTS.md, docs/architecture/, docs/capabilities/, docs/development/reference/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
