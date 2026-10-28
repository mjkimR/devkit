---
id: PLAN-document-bundle-split
spec: SPEC-document-bundle-split
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-document-bundle-split` Install the document system without SDD

## 1. Architecture Overview & Impact
- Target Area: packages/devkit-docs/
- Target Docs Blueprint: `PROP-document-bundle-split-target` (Living Spec targets for this plan and reconcile.md)

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit-docs/`
- `packages/devkit-spec/`
- `guides/`
- `docs/capabilities/documents/`
- `docs/capabilities/delivery/`
- `docs/capabilities/governance/`
- `docs/architecture/`
- `docs/decisions/`
- `docs/steering/glossary.md`
- `.devkit/config.toml`
- `.devkit/installation.json`
- `AGENTS.md`
- `pyproject.toml`
- `uv.lock`
- `scripts/affected_tests.py`

### Excluded Boundaries:
- `packages/devkit-dist/src/`
- `packages/devkit/src/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
