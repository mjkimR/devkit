---
id: PLAN-fixture-optimization
spec: SPEC-fixture-optimization
---

# Technical Plan: `SPEC-fixture-optimization` Optimize slowest test fixtures via seed caching

## 1. Architecture Overview & Impact
- **Target Areas**:
  - `packages/devkit/tests/e2e/features/worktree/test_lifecycle.py` (Worktree lifecycle test suite)
  - `packages/devkit-spec/tests/support/spec_support/delivery.py` and `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_mcp.py` (PlanAccept & Delivery MCP test suite)
- **Impact**:
  - Zero production code impact (only test support helpers and test fixtures modified).
  - Preserves full isolation: each test executes against an independent `tmp_path` copy.

## 2. Component Breakdown & Implementation Details

### 2.1 Worktree `synchronized_template` Caching
- **Implementation**:
  - Introduce a `@pytest.fixture(scope="module")` named `synchronized_template(tmp_path_factory)` in `test_lifecycle.py`.
  - Create the template repository once per module using `init_repo()`, invoke `python -m devkit_dist add authoring -w <path>` once, commit `devkit_dist`, and cache the path.
  - Refactor `synchronized(repo: Path, template: Path)` or the test fixture to copy files/git metadata from `synchronized_template` using `shutil.copytree`, replacing repeated 3-second subprocess executions with sub-100ms filesystem copies.

### 2.2 PlanAccept / Delivery Proposal Seed Caching
- **Implementation**:
  - In `delivery.py` / `test_plan_accept_mcp.py`, establish a module-scoped fixture `proposal_seed_template(synced_template, tmp_path_factory)`:
    - Pre-builds a repository with the proposal unit created, answered, envelope created, and proposal commit recorded on `plan-idea`.
    - Avoids copying `.git/worktrees` with stale absolute paths: store the seed repository at the commit state ready for worktree creation.
  - In `pending(tmp_path, request)`:
    - Fast-copy the seed repository to `tmp_path / "repo"`.
    - Inject test-specific approval policies into `.devkit/config.toml` if requested by `request.param`.
    - Attach the test worktree via `_start_worktree(repo, "plan-idea", tmp_path / "planning")`.
    - Publish the shared report artifact and return `(repo, wt, artifact_uri)`.
  - Eliminates 4 CLI subprocesses and 5 Git commits per test case across 33 tests.

## 3. Verification & Test Plan
- `uv run --no-active pytest packages/devkit/tests/e2e/features/worktree/test_lifecycle.py` (all 46 tests pass, elapsed time verified).
- `uv run --no-active pytest packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_mcp.py` (all 33 tests pass, elapsed time verified).
- `just lint-check` across workspace.
- `just check` across workspace.
