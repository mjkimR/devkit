---
id: PLAN-rule-shared-python-ast
spec: SPEC-rule-shared-python-ast
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-rule-shared-python-ast` Parse each Python file once per rules run

## 1. Architecture Overview & Impact
- Target Area: governance/

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit/src/devkit_agt/features/rules/`
- `packages/devkit/tests/integration/features/rules/`
- `tools/devkit-dev/src/devkit_dev/bundle/rules/`
- `packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/`
- `packages/devkit-catalog/src/devkit_catalog/cli_tool/bundle/rules/`
- `docs/capabilities/governance/`
- `.devkit/installation.json`

### Excluded Boundaries:
- `docs/decisions/`
- `packages/devkit/src/devkit_agt/features/workflow/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
