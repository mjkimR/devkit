---
id: TASKS-bundle-templates
spec: SPEC-bundle-templates
plan: PLAN-bundle-templates
---

# Tasks: Configurable bundle templates

- [ ] **Task 1**: Add template declarations, configuration validation, rendering and inventory integration with tests.
  - **_Boundary**: packages/devkit/src/devkit/distribution/, packages/devkit/tests/, packages/devkit/pyproject.toml, uv.lock
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
- [ ] **Task 2**: Add configurable response-style catalog content and consumer coverage.
  - **_Boundary**: packages/devkit-catalog/, guides/install/bundle-recommendations.md
  - _Requirements: AC-05_
- [ ] **Task 3**: Verify package checks and consumer behavior.
  - **_Boundary**: packages/devkit/tests/, packages/devkit-catalog/tests/, scripts/smoke.sh
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
