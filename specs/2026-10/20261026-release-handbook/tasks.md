---
id: TASKS-release-handbook
spec: SPEC-release-handbook
plan: PLAN-release-handbook
---

# Task Breakdown: `SPEC-release-handbook` Release-bound Multilingual Handbook

## Phase 1: Tooling

- [ ] **Task 1.1**: Handbook script (`status`, `stamp`, `generate`, `verify`) with fixture tests and the `justfile` recipe
  - **_Boundary**: `scripts/handbook.py`, `scripts/affected_tests.py`, `justfile`, `tools/devkit-dev/tests/integration/test_handbook_script.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: `just test devkit-dev`
- [ ] **Task 1.2**: Release check (`release-check`) wired into `scripts/release.sh`, with tests
  - **_Boundary**: `scripts/handbook.py`, `scripts/release.sh`, `scripts/affected_tests.py`, `tools/devkit-dev/tests/integration/test_release_handbook_check.py`
  - _Requirements: AC-08_
  - **Verification**: `just test devkit-dev`
- [ ] **Task 1.3**: `RULE-cli-contract` exclusion for `handbook/**` and the `handbook` preset selection, with a test
  - **_Boundary**: `.devkit/config.toml`, `tools/devkit-dev/tests/integration/test_handbook_script.py`
  - _Requirements: AC-09_
  - **Verification**: `just test devkit-dev`, `just rules-check`

## Phase 2: Playbook and documents

- [ ] **Task 2.1**: Handbook playbook in the `devkit-dev` bundle with its preset and resource test
  - **_Boundary**: `tools/devkit-dev/src/devkit_dev/bundle/`, `tools/devkit-dev/tests/integration/test_resources.py`, `tools/devkit-dev/README.md`
  - _Requirements: AC-10_
  - **Verification**: `just test devkit-dev`
- [ ] **Task 2.2**: Language exception in `AGENTS.md` and the handbook pointer in `README.md`
  - **_Boundary**: `AGENTS.md`, `README.md`
  - _Requirements: AC-11_
  - **Verification**: `just rules-check`
