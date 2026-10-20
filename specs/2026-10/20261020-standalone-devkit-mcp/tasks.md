---
id: TASKS-standalone-devkit-mcp
spec: SPEC-standalone-devkit-mcp
plan: PLAN-standalone-devkit-mcp
---

# Task Breakdown: `SPEC-standalone-devkit-mcp`

- [ ] **Task 1**: Extract dependency-free contracts and optional runtime, with transport and packaging tests.
  - **_Boundary**: packages/devkit-mcp/, packages/devkit-dist/src/devkit/core/, packages/devkit-dist/src/devkit/host/, packages/devkit-dist/tests/, packages/devkit-dist/pyproject.toml, packages/devkit/pyproject.toml, packages/devkit/tests/, packages/devkit-spec/tests/, packages/devkit/src/devkit/integration/, packages/devkit-spec/src/devkit_spec/handoff_mcp.py, pyproject.toml, uv.lock
  - _Requirements: AC-01, AC-02_
- [ ] **Task 2**: Reconcile exact project registrations, retained runtime descriptors and transactions with lifecycle tests.
  - **_Boundary**: packages/devkit-dist/src/devkit/host/, packages/devkit-dist/src/devkit/distribution/, packages/devkit-dist/tests/, packages/devkit-mcp/, packages/devkit/tests/, packages/devkit-spec/tests/
  - _Requirements: AC-03, AC-05_
- [ ] **Task 3**: Bind invocation configuration and enforce cloud/form/lock/mutation/resume guards with domain tests.
  - **_Boundary**: packages/devkit-dist/src/devkit/core/, packages/devkit-dist/tests/, packages/devkit-mcp/, packages/devkit/src/devkit/integration/, packages/devkit/src/devkit/worktree/lifecycle.py, packages/devkit/tests/, packages/devkit-spec/src/devkit_spec/handoff_mcp.py, packages/devkit-spec/tests/
  - _Requirements: AC-02, AC-04, AC-05_
- [ ] **Task 4**: Wire package matrices, affected-test selection and Host-owned approval guidance; record evidence limitations.
  - **_Boundary**: scripts/, pyproject.toml, uv.lock, justfile, .github/workflows/, AGENTS.md, guides/, packages/devkit-mcp/, packages/devkit-dist/README.md, packages/devkit/README.md, packages/devkit-spec/README.md, packages/devkit-spec/src/devkit_spec/bundle/skills/, packages/devkit-spec/src/devkit_spec/bundle/subagents/, packages/devkit-spec/tests/, packages/devkit-dist/tests/, packages/devkit/tests/
  - _Requirements: AC-01, AC-06_
