---
id: SPEC-affected-frontend
title: Frontend changes in affected test selection
summary: just test-affected stops sending devkit-viewer frontend changes to the full pytest suite and instead names the frontend checks the change needs.
status: in-progress
created: 2026-10-19
related_capabilities: []
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-affected-frontend] Frontend changes in affected test selection

## 1. Problem Statement & Motivation

`just test-affected` (`SPEC-targeted-tests`) maps no rule to `packages/devkit-viewer/frontend/` or
`scripts/viewer.sh`, so a frontend change falls back to the full pytest suite. pytest does not exercise the frontend:
the run takes about 40 seconds and still leaves the checks the change needs (prettier, svelte-check, vitest and the
rebuilt committed page, all behind `just viewer`) to the agent's memory. Frontend changes are rare, so the selection
should say exactly which frontend checks to run instead of running unrelated Python tests.

## 2. User Stories

- **US-1**: As a coding agent that changed the viewer frontend, I want `just test-affected` to name the frontend checks
  and skip the unrelated pytest suite, so that I verify the change with the right tools in the time it needs.

## 3. Non-Goals

1. **Scope Excluded**: Running the frontend checks from `just test-affected`.
   - **Rationale**: They need Node and npm; Python test runs must keep working without them
     (`docs/development/setup.md`).
   - **When to Reconsider**: The frontend checks become part of `just test` or Node becomes a workspace requirement.
2. **Scope Excluded**: Selecting individual frontend test files.
3. **Scope Excluded**: Changing `just viewer`, `just test` or CI.

## 4. Acceptance Criteria & Behavioral Contracts

The frontend paths are those under `packages/devkit-viewer/frontend/` and `scripts/viewer.sh`. The frontend line is
exactly `[FRONTEND_CHECK: just viewer install && just viewer lint && just viewer check && just viewer test && just
viewer pack && just viewer build]`, the checks of the CI viewer job.

### [AC-01] A frontend-only change runs no pytest
- **Given** a branch whose only changes are frontend paths
- **When** `just test-affected` runs
- **Then** stdout is the line `[TEST_SELECTION: mode=none base=main changed=<n> paths=0 reason=frontend]` followed by
  the frontend line, pytest is not started and the exit code is `0`

### [AC-02] A mixed change keeps the other selection
- **Given** a branch that changes a frontend path and a file under `packages/devkit/src/devkit/gate/`
- **When** `just test-affected --list` runs
- **Then** the selection is the one the gate change alone selects, the `reason=` lists `frontend` among its causes,
  and the frontend line follows the `[TEST_SELECTION: ...]` line before the `[TEST_PATH: ...]` lines

### [AC-03] A full-suite change still names the frontend checks
- **Given** a branch that changes a frontend path and `uv.lock`
- **When** `just test-affected --list` runs
- **Then** stdout reports `mode=full reason=uv.lock` followed by the frontend line

### [AC-04] The viewer script counts as frontend
- **Given** a branch whose only change is `scripts/viewer.sh`
- **When** `just test-affected` runs
- **Then** the output is that of AC-01

### [AC-05] Other changes print no frontend line
- **Given** a branch with no frontend path among its changes
- **When** `just test-affected` runs
- **Then** stdout carries no `[FRONTEND_CHECK: ...]` line and the selection is unchanged from `SPEC-targeted-tests`

### [AC-06] The rebuilt page still selects the viewer tests
- **Given** a branch whose only change is under `packages/devkit-viewer/src/devkit_viewer/static/`
- **When** `just test-affected --list` runs
- **Then** the selection contains `packages/devkit-viewer/tests` and stdout carries no frontend line

### [AC-07] Guidance names the frontend line
- **Given** `docs/development/ci-cd.md` §2 and `AGENTS.md`
- **When** an agent reads the `just test-affected` rules
- **Then** both state that frontend changes select no pytest and that the agent runs the command the
  `[FRONTEND_CHECK: ...]` line names, and `just rules-check` passes

## 5. Assumptions

- The frontend line includes `just viewer pack`, which CI runs to check the library tarball and its exports, so a
  packaging break is found locally (review finding, inside the agreed goal of naming the checks a change needs).
- The frontend line always lists `just viewer build`: a frontend source change must rebuild the committed page
  (`viewer-assets` in `.devkit/generated.toml`), and rebuilding unchanged sources leaves it unchanged. `just viewer
  install` comes first because a new worktree has no `node_modules`.
- The line is printed in run and `--list` modes alike, before any `[TEST_PATH: ...]` line and before pytest starts.
