---
id: PLAN-adr-body-metadata-removal
spec: SPEC-adr-body-metadata-removal
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-adr-body-metadata-removal` Remove the ADR body metadata block and trim the ADR template

## 1. Architecture Overview & Impact
- Target Area: documents/

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md`
- `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/decision-writing.md`
- `packages/devkit-spec/src/devkit_spec/features/proposals/`
- `packages/devkit-spec/tests/integration/features/proposals/`
- `packages/devkit-docs/tests/integration/bundles/docs/`
- `docs/decisions/`
- `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`
- `docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md`
- `docs/designs/delivery/DESIGN-proposal-handoff/design.md`

### Excluded Boundaries:
- `handbook/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
