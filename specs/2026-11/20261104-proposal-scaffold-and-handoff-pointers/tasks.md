---
id: TASKS-proposal-scaffold-and-handoff-pointers
spec: SPEC-proposal-scaffold-and-handoff-pointers
plan: PLAN-proposal-scaffold-and-handoff-pointers
---

# Task Breakdown: `SPEC-proposal-scaffold-and-handoff-pointers` Lean proposal scaffold and handoff supersession pointers

## Phase 1: Scaffold

- [x] **Task 1**: `new` writes no empty directory; the module docstring and the proposal template comment name
  on-demand creation; scaffold tests assert the layout and `padr` creating `decisions/`
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`,
    `packages/devkit-spec/tests/integration/features/proposals/test_proposal_scaffold.py`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_proposal_scaffold.py`

## Phase 2: Handoff pointers

- [x] **Task 2**: pointer planning, writing, roll-back and `HandoffResult.pointers` in the handoff use case, with the
  handoff tests for the fixture, presence, skipped targets, the title fallback, the roll-back and a bundle without
  directories
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py`,
    `packages/devkit-spec/src/devkit_spec/features/proposals/__init__.py`,
    `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff.py`
  - _Requirements: AC-02, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_proposal_handoff.py`
- [x] **Task 3**: the `[SUPERSEDED_IN_PART: ...]` text line and the CLI docstring, with the CLI text and JSON tests
  and the `dev-<slug>` staging test
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/delivery/cli/proposals.py`,
    `packages/devkit-spec/tests/integration/features/proposals/test_proposal_cli.py`,
    `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff_worktree.py`
  - _Requirements: AC-03, AC-08_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_proposal_cli.py tests/integration/features/proposals/test_proposal_handoff_worktree.py`

## Phase 3: Guidance

- [x] **Task 4**: the planning reference says `materials/` is created with its first file; the managed and projected
  copies are regenerated; a guidance test asserts the sentence
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py`, `.devkit/installation.json`
  - _Requirements: AC-09_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_writing_guidance.py` and `uv run devkit sync --check`
