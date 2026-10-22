---
id: TASKS-single-release-version
spec: SPEC-single-release-version
plan: PLAN-single-release-version
---

# Task Breakdown: `SPEC-single-release-version`

- [x] **Task 1**: Add one version source, synchronization, release validation and regression checks.
  - **_Boundary**: `VERSION`, `scripts/version.py`, `scripts/release.sh`, `justfile`, `packages/*/pyproject.toml`, `tools/*/pyproject.toml`, `uv.lock`, `packages/*/src/**/bundle.toml`, `tools/*/src/**/bundle.toml`, `packages/devkit/tests/integration/package/test_lockstep.py`, `packages/devkit/tests/integration/package/test_version_script.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just lint-check`, `just check`, `just test-affected`, `just version-check`, `uv lock --check`, `just release-build v0.1.2`.
