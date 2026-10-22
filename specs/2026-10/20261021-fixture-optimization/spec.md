---
id: SPEC-fixture-optimization
title: Optimize slowest test fixtures via seed caching
summary: Optimize Worktree and PlanAccept test setup by reusing prepared repository templates.
status: completed
created: 2026-10-21
related_capabilities:
  - CAP-WT-task-worktrees
  - CAP-DLV-delivery-workflows
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-fixture-optimization] Optimize slowest test fixtures via seed caching

## 1. Problem Statement & Motivation

In the devkit test suite, E2E tests for Worktree lifecycle (`packages/devkit/tests/e2e/features/worktree/test_lifecycle.py`) and PlanAccept MCP tools (`packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_mcp.py`) are the primary latency bottlenecks:
- In `test_lifecycle.py`, 4 tests consume 24.7s out of 32.3s because of repeated calls to `synchronized(repo)`, which invokes `subprocess.run([sys.executable, "-m", "devkit_dist", "add", "authoring"])` for every test.
- In `test_plan_accept_mcp.py`, 33 test cases take over 2 minutes because `pending` runs `_make_synced_repo`, `_cli(repo, "sync")`, `_start_worktree`, `_cli proposal new`, `_cli workflow answer`, `_cli workflow envelope new`, and multiple Git commits for every single test case.

By introducing module-scoped seed repository templates and fast local copy (`shutil.copytree`), test setup time can be reduced by 50-70% while maintaining 100% test isolation and real Git execution.

## 2. User Stories

- **US-1**: As a developer running E2E tests, I want `synchronized` worktree tests to reuse a module-scoped template with the `authoring` bundle pre-installed, so that `test_lifecycle.py` completes in under 20 seconds.
- **US-2**: As a developer running delivery tests, I want `pending` proposal fixtures in `test_plan_accept_mcp.py` to reuse an initialized repository seed containing a completed proposal commit, so that the 33 test cases complete in seconds rather than minutes.

## 3. Non-Goals

1. **No Assertion Modifications**: Do not weaken, mock, or alter the underlying assertions of the test suites.
2. **No Mutable Shared State**: Never share active mutable Git refs, index, or worktree directories between test cases; each test must operate on its own independent `tmp_path` copy.
3. **No Linked-Worktree Absolute Path Retention**: Do not copy `.git/worktrees` with stale absolute path references; worktrees must be attached cleanly in the test copy or repaired.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Worktree synchronized seed template
- **Given** tests in `packages/devkit/tests/e2e/features/worktree/test_lifecycle.py` requiring a synchronized devkit project with the `authoring` bundle.
- **When** the tests execute `synchronized(repo)` or access the synchronized fixture.
- **Then** a module-scoped template repository with `authoring` pre-installed is reused via fast directory copy (`shutil.copytree`), avoiding redundant `python -m devkit_dist add authoring` subprocesses.

### [AC-02] PlanAccept proposal seed template
- **Given** tests in `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_mcp.py` requiring a proposal in `reviewing` status with an accepted plan-intent answer and feedback envelope.
- **When** the `pending` fixture runs for each test case.
- **Then** a module-scoped base repository seed containing the completed proposal commit is cloned into `tmp_path`, and only the test-specific worktree is attached, eliminating repeated `_cli(repo, "sync")`, `proposal new`, `answer`, and `envelope new` subprocess invocations.

### [AC-03] Test Isolation and Verification
- **Given** both fixture optimizations are in place.
- **When** the full test suites for `packages/devkit/tests/e2e/features/worktree/test_lifecycle.py` (46 tests) and `packages/devkit-spec/tests/e2e/features/delivery/test_plan_accept_mcp.py` (33 tests) are executed.
- **Then** 100% of tests pass, all linting and type checks pass, and test execution time is measurably reduced.
