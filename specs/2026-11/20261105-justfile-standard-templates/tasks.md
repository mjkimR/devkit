---
id: TASKS-justfile-standard-templates
spec: SPEC-justfile-standard-templates
plan: PLAN-justfile-standard-templates
---

# Task Breakdown: SPEC-justfile-standard-templates

- [ ] **Task 1**: Ship the opt-in creation instruction and validate selection/discovery.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/command_design/`, `packages/devkit-catalog/pyproject.toml`, `packages/devkit-catalog/tests/integration/bundles/test_bundles.py`, `packages/devkit-catalog/README.md`, `docs/capabilities/distribution/CAP-DIST-content-packages.md`, `docs/capabilities/harness/CAP-HARN-command-design.md`, `docs/usecases/UC-design-command-entrypoints.md`, `uv.lock`
  - _Requirements: AC-01, AC-02_
  - **Verification**: catalog manifest/deployment tests and scenario review, lint/types and rules.
- [ ] **Task 2**: Add concrete native command reuse and optional recipe examples.
  - **_Boundary**: `guides/install/existing-repository.md`, `guides/install/new-repository.md`, `guides/install/bundle-recommendations.md`
  - _Requirements: AC-03_
  - **Verification**: temporary Node fixture, guide walkthrough and document rules.
