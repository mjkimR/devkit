---
id: TASKS-response-style-skill
spec: SPEC-response-style-skill
plan: PLAN-response-style-skill
---

# Tasks

- [x] **Task 1**: Support and validate templated skill entries and Markdown projections, including overrides.
  - **_Boundary**: `packages/devkit/src/devkit/distribution/bundles/`, `packages/devkit/src/devkit/distribution/installation/inventory.py`, `packages/devkit/src/devkit/distribution/installation/overrides.py`, `packages/devkit/tests/distribution/test_templates.py`
  - _Requirements: AC-01, AC-02, AC-03_
- [x] **Task 2**: Render response-style language inside its skill and synchronize the repository.
  - **_Boundary**: `packages/devkit-catalog/`, `guides/install/bundle-recommendations.md`, `AGENTS.md`, `.devkit/installation.json`
  - _Requirements: AC-04_
