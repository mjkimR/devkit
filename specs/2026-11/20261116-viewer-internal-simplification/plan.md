---
id: PLAN-viewer-internal-simplification
spec: SPEC-viewer-internal-simplification
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-viewer-internal-simplification` Viewer as an internal tool: drop the library surface and trim unused features

## 1. Architecture Overview & Impact
- Target Area: viewer/

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit-viewer/`
- `packages/devkit/tests/integration/package/test_viewer_script.py`
- `packages/devkit/tests/e2e/package/test_affected_tests.py`
- `docs/capabilities/viewer/`
- `docs/usecases/viewer/`
- `docs/architecture/ARCH-05-1-containers.md`
- `docs/architecture/ARCH-07-deployment.md`
- `docs/decisions/`
- `docs/development/reference/viewer.md`
- `docs/development/setup.md`
- `docs/development/ci-cd.md`
- `scripts/viewer.sh`
- `scripts/affected_tests.py`
- `.github/workflows/ci.yml`
- `justfile`
- `.devkit/architecture.toml`

### Excluded Boundaries:
- `handbook/`
- `packages/devkit-dist/`
- `docs/capabilities/collaboration/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
