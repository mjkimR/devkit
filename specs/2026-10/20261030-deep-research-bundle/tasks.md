---
id: TASKS-deep-research-bundle
spec: SPEC-deep-research-bundle
plan: PLAN-deep-research-bundle
---

# Task Breakdown: `SPEC-deep-research-bundle` Split explicit deep research into an approach-neutral bundle

## Phase 1: Bundle split

- [ ] **Task 1.1**: Create the deep-research bundle, register it and move the research entry and roles out of the incubation bundle, with integration tests
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/`, `packages/devkit-catalog/pyproject.toml`, `packages/devkit-catalog/tests/integration/bundles/`, `.devkit/architecture.toml`, `uv.lock`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07_
  - **Verification**: `just test devkit-catalog tests/integration/bundles`
- [ ] **Task 1.2**: Installed-consumer e2e test for deep-research; incubation e2e test without the moved assets
  - **_Boundary**: `packages/devkit-catalog/tests/e2e/bundles/`
  - _Requirements: AC-08_
  - **Verification**: `just test devkit-catalog tests/e2e/bundles`

## Phase 2: Guidance and packaging

- [ ] **Task 2.1**: Spec intake exemption and MAT citation line, synced into this repository
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/`, `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py`, `.devkit/installation.json` (sync output), `AGENTS.md` (sync output)
  - _Requirements: AC-10_
  - **Verification**: `just test devkit-catalog tests/integration/bundles/test_deep_research.py`, `just test devkit-spec tests/integration/bundles/spec`, `uv run devkit sync --check`
- [ ] **Task 2.2**: Remove suggestion wording from the guides and the catalog README, add the bundle row and migration steps, with text checks
  - **_Boundary**: `guides/`, `packages/devkit-catalog/README.md`, `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py`
  - _Requirements: AC-09, AC-11_
  - **Verification**: `just test devkit-catalog tests/integration/bundles/test_deep_research.py`
- [ ] **Task 2.3**: Consumer smoke test includes the new bundle
  - **_Boundary**: `tests/e2e/smoke.sh`
  - _Requirements: AC-12_
  - **Verification**: `just smoke`
