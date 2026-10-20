---
id: TASKS-integration-pull-request-cleanup
spec: SPEC-integration-pull-request-cleanup
plan: PLAN-integration-pull-request-cleanup
---

# Task Breakdown: `SPEC-integration-pull-request-cleanup`

- [ ] **Task 1**: GitHub port and remote safety observations, with offline tests
  - **_Boundary**: `packages/devkit/src/devkit/worktree/`, `packages/devkit/tests/worktree/`
  - _Requirements: AC-02, AC-03, AC-07_
- [ ] **Task 2**: Confirmed PR route, pending/resume, landing and ordered cleanup, with offline tests
  - **_Boundary**: `packages/devkit/src/devkit/integration/`, `packages/devkit/tests/integration/`, `packages/devkit-spec/src/devkit_spec/integration.py`, `packages/devkit-spec/tests/test_integration.py`
  - _Requirements: AC-01, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08_
- [ ] **Task 3**: Agent integration procedure and readiness disclosure
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-integrate/`, `docs/capabilities/integration/CAP-INT-mcp-services.md`, `docs/capabilities/worktree/CAP-WT-task-worktrees.md`, `docs/capabilities/delivery/CAP-DLV-project-policy.md`, `docs/development/reference/integration.md`, `docs/development/reference/worktree.md`, `packages/devkit/README.md`, `specs/2026-10/20261017-hook-driven-integration-cleanup/feedback/pr-remote-and-squash-integration.md`
  - _Requirements: AC-01, AC-04, AC-05, AC-06, AC-07, AC-08_
