---
id: TASKS-integration-follow-ups
spec: SPEC-integration-follow-ups
plan: PLAN-integration-follow-ups
---

# Task Breakdown: `SPEC-integration-follow-ups` Integration base advances: merge commits, effective policy digest and readiness on the result

## Phase 1: Worktree

- [x] **Task 1.1**: `[worktree] merge` key, result-commit build, new codes and SHA-preserving fixes, with tests
  - **_Boundary**: packages/devkit/src/devkit/worktree/config.py, packages/devkit/src/devkit/worktree/merging.py,
    packages/devkit/src/devkit/worktree/errors.py, packages/devkit/src/devkit/worktree/__init__.py,
    packages/devkit/tests/worktree/
  - _Requirements: AC-02, AC-04, AC-05, AC-14, AC-15_
- [x] **Task 1.2**: `finish --merge` lands the built result, takes the integration lock, rerun after a merge; plan and
  validation of an already merged branch and of a base containing the result, with tests
  - **_Boundary**: packages/devkit/src/devkit/worktree/lifecycle.py, packages/devkit/src/devkit/worktree/planning.py,
    packages/devkit/src/devkit/worktree/cli.py, packages/devkit/tests/worktree/
  - _Requirements: AC-11, AC-13, AC-14_
  - **Verification**: `just test devkit worktree`

## Phase 2: Integration service

- [x] **Task 2.1**: execution context, provider declarations, effective policy digest and receipt consistency check,
  with tests
  - **_Boundary**: packages/devkit/src/devkit/integration/models.py, packages/devkit/src/devkit/integration/providers.py,
    packages/devkit/src/devkit/integration/receipts.py, packages/devkit/src/devkit/integration/errors.py,
    packages/devkit/src/devkit/integration/__init__.py, packages/devkit/tests/integration/
  - _Requirements: AC-07, AC-08, AC-09_
- [x] **Task 2.2**: builds in the service: target descent, compare-and-swap, readiness on the result, cleanup-only
  request, lock wait, approval lifetime, recovery, confirmation text and result fields, with tests
  - **_Boundary**: packages/devkit/src/devkit/integration/service.py, packages/devkit/src/devkit/integration/models.py,
    packages/devkit/src/devkit/integration/mcp.py, packages/devkit/tests/integration/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-06, AC-07, AC-10, AC-11, AC-12, AC-13_
  - **Verification**: `just test devkit integration`

## Phase 3: devkit-spec

- [x] **Task 3.1**: readiness provider on the result and scoped cleanup after a merge commit, with tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/integration.py, packages/devkit-spec/src/devkit_spec/cleanup.py,
    packages/devkit-spec/tests/test_integration.py, packages/devkit-spec/tests/test_cleanup.py
  - _Requirements: AC-16, AC-17_
- [x] **Task 3.2**: spec-integrate, completion and worktree guidance for merge commits and the confirmation binding
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/skills/spec-integrate/SKILL.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/completion.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/worktree.md
  - _Requirements: AC-04, AC-10, AC-16_

## Phase 4: References

- [x] **Task 4.1**: quick references and the install guide's Git requirement
  - **_Boundary**: docs/development/reference/integration.md, docs/development/reference/worktree.md,
    guides/INSTALL_GUIDE.md
  - _Requirements: AC-05, AC-12, AC-14_
