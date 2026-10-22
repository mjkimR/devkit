---
id: TASKS-cli-toolkit
spec: SPEC-cli-toolkit
plan: PLAN-cli-toolkit
---

# Task Breakdown: `SPEC-cli-toolkit` Agent-first CLI toolkit package and catalog bundle

## Phase 1: Library

- [x] **Task 1.1**: Add `ArgumentError` to `devkit.advisory` and derive the devkit-core class from it
  - **_Boundary**: `packages/devkit-advisory/`, `packages/devkit-core/src/devkit_core/base/errors.py`, their tests
  - _Requirements: AC-09_
  - **Verification**: `just test advisory`, `just test core`
- [x] **Task 1.2**: Create `devkit-cli` with the boundary, output helpers, lazy group and testing helper
  - **_Boundary**: `packages/devkit-cli/`, root `pyproject.toml`, `uv.lock`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: `just test cli`, `just check cli`

## Phase 2: devkit on the toolkit

- [x] **Task 2.1**: Rebuild `devkit_dist.adapters.cli` and the root lazy group on `devkit_cli`
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/adapters/cli.py`, `packages/devkit-dist/src/devkit_dist/cli.py`,
    `packages/devkit-dist/pyproject.toml`, `packages/devkit-dist/tests/`
  - _Requirements: AC-10_
  - **Verification**: `just test-affected`, `just test-dist`
- [x] **Task 2.2**: Wire packaging and release
  - **_Boundary**: `scripts/`, `tests/e2e/`, `packages/devkit/tests/integration/package/`, `README.md`, `guides/`,
    package READMEs
  - _Requirements: AC-11_
  - **Verification**: `just test devkit package`, `just smoke`

## Phase 3: Catalog bundle

- [x] **Task 3.1**: Add the `cli-tool` bundle with the instruction and the three rules
  - **_Boundary**: `packages/devkit-catalog/`
  - _Requirements: AC-12, AC-13, AC-14, AC-15_
  - **Verification**: `just test catalog`, `just rules-check`

## Phase 4: Living Spec

- [x] **Task 4.1**: Document the capability and update architecture, references and guides
  - **_Boundary**: `docs/`, `AGENTS.md`, `README.md`, `packages/*/README.md`
  - _Requirements: AC-01, AC-09, AC-11, AC-12_
  - **Verification**: `just rules-check`
