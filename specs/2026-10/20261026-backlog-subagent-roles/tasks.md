---
id: TASKS-backlog-subagent-roles
spec: SPEC-backlog-subagent-roles
plan: PLAN-backlog-subagent-roles
---

# Task Breakdown: `SPEC-backlog-subagent-roles` Backlog triage and decomposer subagent roles

## Phase 1: Size gate

- [x] **Task 1.1**: The size predicate in `accept --direct` and the `plan-` attach check, with tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/`, `packages/devkit-spec/src/devkit_spec/features/delivery/`, `packages/devkit-spec/tests/integration/features/`
  - _Requirements: AC-08, AC-09_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_size_gate.py tests/integration/features/delivery/test_attach.py`
- [x] **Task 1.2**: The `intent-proposal` size exit check in `sdd-proposal`, with `next` and `answer` tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/sdd-proposal.md`, `packages/devkit-spec/tests/integration/features/proposals/test_size_gate.py`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_size_gate.py tests/integration/bundles/spec/test_workflows.py`

## Phase 2: Roles and guidance

- [x] **Task 2.1**: The `triage` and `decomposer` contracts, their registration and payload rows, with role tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/`, `packages/devkit-spec/tests/integration/bundles/spec/`, `.devkit/installation.json`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_role_contracts.py tests/integration/bundles/spec/test_workflows.py`
- [x] **Task 2.2**: Invocation, Host verification and size guidance; the `XL` definition; the support-role snapshot that resolves `FB-support-role-diff-check-on-dirty-tree`, with guidance tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/SKILL.md` (Host-admitted for the feedback), `specs/2026-10/20261026-backlog-subagent-roles/feedback/support-role-diff-check-on-dirty-tree.md` (Host-admitted), `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-hygiene/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/sdd-proposal.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/templates/proposal.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/seed/docs/proposals/README.md`, `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`, `packages/devkit-spec/tests/`, `.devkit/installation.json`
  - _Requirements: AC-04, AC-05, AC-10, AC-11_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec`
- [x] **Task 2.3**: A fixture decomposition test of the Host procedure
  - **_Boundary**: `packages/devkit-spec/tests/integration/features/proposals/test_decomposition_fixture.py`
  - _Requirements: AC-12_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_decomposition_fixture.py`
- [x] **Task 2.4**: A dogfood `triage` run over the open feedback, recorded in the final change report
  - **_Boundary**: `specs/2026-10/20261026-backlog-subagent-roles/`
  - _Requirements: AC-13_
  - **Verification**: `git status --porcelain` empty before and after the run
