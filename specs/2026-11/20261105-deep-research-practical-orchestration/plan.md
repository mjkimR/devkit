---
id: PLAN-deep-research-practical-orchestration
spec: SPEC-deep-research-practical-orchestration
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-deep-research-practical-orchestration` Make deep-research deliverable-driven and proportionate

## 1. Architecture Overview & Impact
- Target Area: capabilities/delivery/
- Target Docs Blueprint: `PROP-deep-research-practical-orchestration-target` (Living Spec targets for this plan and reconcile.md)

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/`
- `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py`
- `packages/devkit-catalog/tests/e2e/bundles/deep_research/`
- `docs/capabilities/delivery/CAP-DLV-deep-research.md`
- `docs/usecases/delivery/UC-research-an-idea-and-shape-a-roadmap.md`
- `docs/decisions/`

### Excluded Boundaries:
- `packages/devkit/src/`
- `packages/devkit-dist/src/`
- `packages/devkit-spec/src/`
- `.devkit/managed/`
- `.agents/skills/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
