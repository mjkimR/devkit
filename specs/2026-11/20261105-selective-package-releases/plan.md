---
id: PLAN-selective-package-releases
spec: SPEC-selective-package-releases
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-selective-package-releases` Selective package releases under a shared release version

## 1. Architecture Overview & Impact
- Target Area: docs/capabilities/distribution/
- Target Docs Blueprint: `PROP-selective-package-releases-target` (Living Spec targets for this plan and reconcile.md)

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `scripts/`
- `.github/workflows/release.yml`
- `VERSION`
- `pyproject.toml`
- `uv.lock`
- `packages/`
- `tools/`
- `docs/architecture/`
- `docs/capabilities/distribution/`
- `docs/decisions/`
- `docs/development/reference/`
- `guides/`
- `README.md`
- `justfile`
- `.devkit/installation.json`

### Excluded Boundaries:
- `models/`
- `handbook/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
