---
id: TASKS-repository-viewer
spec: SPEC-repository-viewer
plan: PLAN-repository-viewer
---

# Task Breakdown: `SPEC-repository-viewer` Local multi-repository SDD viewer owned by devkit

## Phase 1: Python distribution and server

- [x] **Task 1.1**: `devkit-viewer` distribution skeleton, workspace wiring and the mounted `viewer` group with
  `--version`
  - **_Boundary**: `packages/devkit-viewer/pyproject.toml`, `packages/devkit-viewer/README.md`,
    `packages/devkit-viewer/src/devkit_viewer/__init__.py`, `packages/devkit-viewer/src/devkit_viewer/cli.py`,
    `packages/devkit-viewer/tests/test_cli.py`, `packages/devkit-viewer/tests/test_imports.py`, `pyproject.toml`,
    `uv.lock`, `scripts/_lib.sh`, `.devkit/installation.json`
  - _Requirements: AC-16_
  - **Verification**: `just test viewer`
- [x] **Task 1.2**: Git reads at a ref: tree, blob, branches, ref and path refusals
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/git.py`, `packages/devkit-viewer/src/devkit_viewer/errors.py`,
    `packages/devkit-viewer/tests/conftest.py`, `packages/devkit-viewer/tests/test_git.py`
  - _Requirements: AC-04, AC-05, AC-06, AC-07_
- [x] **Task 1.3**: Repository registration: `--repo`, `--scan`, the current project, refusals
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/repositories.py`,
    `packages/devkit-viewer/src/devkit_viewer/errors.py`, `packages/devkit-viewer/tests/test_repositories.py`
  - _Requirements: AC-02, AC-03_
- [ ] **Task 1.4**: HTTP server: API routes, JSON errors, Host check, GET only, static files
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/server.py`, `packages/devkit-viewer/tests/test_server.py`
  - _Requirements: AC-01, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09_
- [x] **Task 1.5**: `devkit viewer serve`: the sentinel line, stop on a signal, port refusal
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/cli.py`, `packages/devkit-viewer/tests/test_cli.py`
  - _Requirements: AC-01, AC-03_

## Phase 2: Frontend

- [ ] **Task 2.1**: Frontend project and the viewer moved from autohub as a library, with document indexing tests
  - **_Boundary**: `packages/devkit-viewer/frontend/package.json`, `packages/devkit-viewer/frontend/package-lock.json`,
    `packages/devkit-viewer/frontend/*.config.*`, `packages/devkit-viewer/frontend/tsconfig.json`,
    `packages/devkit-viewer/frontend/.prettier*`, `packages/devkit-viewer/frontend/src/lib/`, `.gitignore`
  - _Requirements: AC-13, AC-14_
  - **Verification**: `just viewer test`, `just viewer pack`
- [ ] **Task 2.2**: Roadmap model and view: status order, readiness, members across branches
  - **_Boundary**: `packages/devkit-viewer/frontend/src/lib/roadmap.ts`,
    `packages/devkit-viewer/frontend/src/lib/roadmap.test.ts`,
    `packages/devkit-viewer/frontend/src/lib/RoadmapView.svelte`,
    `packages/devkit-viewer/frontend/src/lib/SddViewer.svelte`, `packages/devkit-viewer/frontend/src/lib/repository.ts`
  - _Requirements: AC-11, AC-12_
- [ ] **Task 2.3**: The served app: repository and branch switch
  - **_Boundary**: `packages/devkit-viewer/frontend/index.html`, `packages/devkit-viewer/frontend/src/app/`
  - _Requirements: AC-10_

## Phase 3: Build, packaging and automation

- [ ] **Task 3.1**: Committed app build as a tracked generated artifact, reproducible from the lockfile
  - **_Boundary**: `packages/devkit-viewer/src/devkit_viewer/static/`, `.devkit/generated.toml`
  - _Requirements: AC-09, AC-15_
  - **Verification**: `uv run devkit generated check viewer-assets`
- [ ] **Task 3.2**: Frontend commands, CI job, smoke and release wiring
  - **_Boundary**: `scripts/viewer.sh`, `justfile`, `scripts/smoke.sh`, `scripts/release.sh`, `.github/workflows/ci.yml`
  - _Requirements: AC-09, AC-14, AC-15, AC-16_
  - **Verification**: `just viewer lint`, `just viewer check`, `just smoke`
