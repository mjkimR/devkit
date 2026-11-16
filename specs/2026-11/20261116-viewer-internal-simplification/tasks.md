---
id: TASKS-viewer-internal-simplification
spec: SPEC-viewer-internal-simplification
plan: PLAN-viewer-internal-simplification
---

# Task Breakdown: `SPEC-viewer-internal-simplification` Viewer as an internal tool: drop the library surface and trim unused features

## Phase 1: Library surface and source layout

- [x] **Task 1.1**: Remove the npm library packaging, the `pack` action, its CI step and `FRONTEND_CHECK` entry,
  with the two devkit tests updated
  - **_Boundary**: `packages/devkit-viewer/frontend/package.json`, `packages/devkit-viewer/frontend/package-lock.json`,
    `scripts/viewer.sh`, `justfile`, `.github/workflows/ci.yml`, `scripts/affected_tests.py`,
    `packages/devkit/tests/integration/package/test_viewer_script.py`,
    `packages/devkit/tests/e2e/package/test_affected_tests.py`
  - _Requirements: AC-01_
  - **Verification**: `uv run --no-active pytest packages/devkit/tests/integration/package/test_viewer_script.py packages/devkit/tests/e2e/package/test_affected_tests.py`
- [x] **Task 1.2**: Collapse `frontend/src/lib/` and `frontend/src/app/` into one source tree without the barrel,
  shims or wrappers
  - **_Boundary**: `packages/devkit-viewer/frontend/src/`, `packages/devkit-viewer/frontend/index.html`
  - _Requirements: AC-03_
  - **Verification**: `just viewer check && just viewer test`
- [x] **Task 1.3**: Make the local data-source members required and remove `refs`, the `ref` argument and the
  presence checks
  - **_Boundary**: `packages/devkit-viewer/frontend/src/`
  - _Requirements: AC-02_
  - **Verification**: `just viewer check && just viewer test`

## Phase 2: Trims

- [x] **Task 2.1**: Remove the Shared tab, the `/review` page and the shared API with their codes and tests, and the
  `browse` edge to `devkit_dist.features.shared`
  - **_Boundary**: `packages/devkit-viewer/frontend/src/`, `packages/devkit-viewer/src/devkit_viewer/`,
    `packages/devkit-viewer/tests/`, `.devkit/architecture.toml`
  - _Requirements: AC-04, AC-05_
  - **Verification**: `just test devkit-viewer` and `just viewer test`
- [x] **Task 2.2**: Load every eligible dashboard card after one listing, keep failed reads visible and counted, and
  remove paging and the dashboard caches
  - **_Boundary**: `packages/devkit-viewer/frontend/src/features/dashboard/`
  - _Requirements: AC-06, AC-07, AC-08_
  - **Verification**: `just viewer test`
- [x] **Task 2.3**: Limit Planning sources to worktrees and local branches and ask for the overlay on each load
  without caching or seeding
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/features/browse/repositories/planning.py`,
    `packages/devkit-viewer/tests/integration/features/browse/test_planning.py`,
    `packages/devkit-viewer/frontend/src/`
  - _Requirements: AC-09, AC-10_
  - **Verification**: `just test devkit-viewer` and `just viewer test`
- [x] **Task 2.4**: Remove the host props and events and keep the book request internal
  - **_Boundary**: `packages/devkit-viewer/frontend/src/`
  - _Requirements: AC-11_
  - **Verification**: `just viewer test`

## Phase 3: Generated build, records and documents

- [x] **Task 3.1**: Rebuild the committed page and set the ADR supersession status and repaired Confirmation paths
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/static/`, `docs/decisions/`
  - _Requirements: AC-12_
  - **Verification**: `uv run devkit generated check viewer-assets` and `uv run devkit rules check --ci`
- [x] **Task 3.2**: Describe only the internal viewer in its capability, use cases, architecture, development
  documents and READMEs
  - **_Boundary**: `docs/capabilities/viewer/`, `docs/usecases/viewer/`, `docs/architecture/ARCH-05-1-containers.md`,
    `docs/architecture/ARCH-07-deployment.md`, `docs/development/reference/viewer.md`, `docs/development/setup.md`,
    `docs/development/ci-cd.md`, `packages/devkit-viewer/README.md`, `packages/devkit-viewer/frontend/README.md`
  - _Requirements: AC-13_
  - **Verification**: the `rg` commands of AC-03 and AC-13 print nothing
