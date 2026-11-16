---
id: TASKS-viewer-internal-simplification
spec: SPEC-viewer-internal-simplification
plan: PLAN-viewer-internal-simplification
---
<!-- devkit:skeleton -->

# Task Breakdown: `SPEC-viewer-internal-simplification` Viewer as an internal tool: drop the library surface and trim unused features

## Phase 1: Implementation
- [ ] **Task 1.1**: Core Implementation
  - **_Boundary**: packages/devkit-viewer/, packages/devkit/tests/integration/package/test_viewer_script.py, packages/devkit/tests/e2e/package/test_affected_tests.py, docs/capabilities/viewer/, docs/usecases/viewer/, docs/architecture/ARCH-05-1-containers.md, docs/architecture/ARCH-07-deployment.md, docs/decisions/, docs/development/reference/viewer.md, docs/development/setup.md, docs/development/ci-cd.md, scripts/viewer.sh, scripts/affected_tests.py, .github/workflows/ci.yml, justfile, .devkit/architecture.toml
  - _Requirements: AC-01_
  - **Verification**: <command that verifies the task>
