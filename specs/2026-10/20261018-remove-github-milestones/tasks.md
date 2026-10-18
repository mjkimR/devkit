---
id: TASKS-remove-github-milestones
spec: SPEC-remove-github-milestones
plan: PLAN-remove-github-milestones
---

# Tasks: Remove GitHub milestone guidance

- [x] **Task 1**: Remove the catalog resource module and registration; preserve catalog smoke coverage.
  - **_Boundary**: `packages/devkit-catalog/pyproject.toml`, `packages/devkit-catalog/src/devkit_catalog/github_milestones/`, `scripts/smoke.sh`
  - _Requirements: AC-01, AC-02_
- [x] **Task 2**: Update current consumer guidance and catalog documentation.
  - **_Boundary**: `README.md`, `packages/devkit-catalog/README.md`, `guides/install/bundle-recommendations.md`, `guides/install/new-repository.md`, `guides/install/existing-repository.md`, `docs/architecture/ARCH-05-1-containers.md`
  - _Requirements: AC-02_
- [x] **Task 3**: Verify catalog packaging and preserved document milestones.
  - **_Boundary**: `packages/devkit-catalog/`, `scripts/smoke.sh`
  - _Requirements: AC-01, AC-02, AC-03_
