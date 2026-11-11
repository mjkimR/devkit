---
id: TASKS-small-helper-consolidations
spec: SPEC-small-helper-consolidations
plan: PLAN-small-helper-consolidations
---

# Task Breakdown: `SPEC-small-helper-consolidations` Consolidate the remaining duplicated runtime helpers

## Phase 1: Implementation

- [x] **Task 1.1**: Public `devkit_cli.utf8_output`, re-exported by `devkit_dist.adapters.cli` and used by `devkit host hook`, with tests and quick references
  - **_Boundary**: `packages/devkit-cli/src/devkit_cli/`, `packages/devkit-cli/tests/`, `packages/devkit-dist/src/devkit_dist/adapters/cli.py`, `packages/devkit-dist/src/devkit_dist/features/host/cli.py`, `packages/devkit-dist/tests/integration/adapters/test_cli.py`, `docs/capabilities/cli/CAP-CLI-agent-cli-toolkit.md`, `docs/development/reference/core.md`, `packages/devkit-cli/README.md` `(scope extension: the package README lists the devkit_cli public names that CAP-CLI-agent-cli-toolkit section 4 owns)`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `uv run pytest packages/devkit-cli/tests packages/devkit-dist/tests/integration/adapters/test_cli.py packages/devkit-dist/tests/integration/features/host/test_hooks.py`

- [x] **Task 1.2**: `frontmatter.scalar` quoting options and subagent projection quoting through it, with tests
  - **_Boundary**: `packages/devkit-core/src/devkit_core/core/frontmatter.py`, `packages/devkit-core/tests/unit/core/test_frontmatter.py`, `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/subagents.py`, `packages/devkit-dist/tests/integration/features/distribution/test_subagent_contracts.py`, `docs/development/reference/core.md`
  - _Requirements: AC-03, AC-04, AC-05_
  - **Verification**: `uv run pytest packages/devkit-core/tests/unit/core/test_frontmatter.py packages/devkit-dist/tests/integration/features/distribution/test_subagent_contracts.py`; `uv run devkit sync --check`

- [x] **Task 1.3**: `devkit_core.core.git.tracked_paths`/`ignored_paths` and the five devkit-dist probe sites on them, with tests
  - **_Boundary**: `packages/devkit-core/src/devkit_core/core/git.py`, `packages/devkit-core/tests/integration/core/test_git_helpers.py`, `packages/devkit-dist/src/devkit_dist/features/host/usecases/registrations.py`, `packages/devkit-dist/src/devkit_dist/features/shared/repositories/local.py`, `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/local_render.py`, `packages/devkit-dist/src/devkit_dist/features/distribution/repositories/projection_git.py`, `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/sync.py`, `packages/devkit-dist/tests/integration/features/distribution/test_projection_git.py`, `packages/devkit-dist/tests/integration/features/host/test_mcp_onboarding.py`, `docs/development/reference/core.md`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `uv run pytest packages/devkit-core/tests/integration/core/test_git_helpers.py packages/devkit-dist/tests`
