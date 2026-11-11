---
id: TASKS-cli-naming-consistency
spec: SPEC-cli-naming-consistency
plan: PLAN-cli-naming-consistency
---

# Task Breakdown: `SPEC-cli-naming-consistency` Consistent CLI option naming

## Phase 1: Implementation
- [ ] **Task 1.1**: Bundle refresh previews without digests and drops `--check`
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/cli/bundles.py`, `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/snapshots.py`, `packages/devkit-dist/tests/integration/features/distribution/test_snapshots.py`, `packages/devkit-dist/tests/e2e/cli/test_snapshots.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit-dist tests/integration/features/distribution/test_snapshots.py tests/e2e/cli/test_snapshots.py`
- [ ] **Task 1.2**: List `workflow envelope new` in the envelope group help
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/workflow/cli/envelope.py`, `packages/devkit/tests/integration/features/workflow/test_cli.py`
  - _Requirements: AC-05_
  - **Verification**: `just test devkit tests/integration/features/workflow/test_cli.py tests/integration/package/test_agent_output_contract.py`
- [ ] **Task 1.3**: Add `--task-kind` to `spec new`
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/delivery/cli/specs.py`, `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/specs.py`, `packages/devkit-spec/tests/integration/features/delivery/test_spec_initialization.py`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `just test devkit-spec tests/integration/features/delivery/test_spec_initialization.py`

## Phase 2: Contracts and guidance
- [ ] **Task 2.1**: Update contracts, references, the guide and bundle guidance; synchronize
  - **_Boundary**: `docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md`, `docs/capabilities/delivery/CAP-DLV-cli-and-output.md`, `docs/capabilities/delivery/CAP-DLV-spec-bundles.md`, `docs/development/reference/distribution.md`, `guides/install/existing-repository.md`, `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/instructions/in-repo-bundle.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/SKILL.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worktree.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-specify/SKILL.md`
  - _Requirements: AC-08_
  - **Verification**: `uv run devkit sync --check` and `uv run devkit rules check --ci --base main`
