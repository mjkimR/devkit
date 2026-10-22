---
id: PLAN-lint-clean-target-scoped-rules
spec: SPEC-lint-clean-target-scoped-rules
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-lint-clean-target-scoped-rules` Scope target runs to the rules their targets can affect

## 1. Architecture Overview & Impact
- Target Area: governance/

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit/src/devkit_agt/features/rules/`
- `packages/devkit/tests/`
- `tools/devkit-dev/src/devkit_dev/bundle/rules/`
- `packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-rule/`
- `.devkit/installation.json`
- `docs/capabilities/governance/`
- `docs/development/reference/`

### Excluded Boundaries:
- `docs/decisions/`
- `packages/devkit/src/devkit_agt/features/workflow/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
