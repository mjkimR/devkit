---
id: PLAN-consolidated-record-length
spec: SPEC-consolidated-record-length
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-consolidated-record-length` Line budgets for consolidated records

## 1. Architecture Overview & Impact
- Target Area: governance/

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit/src/devkit_agt/features/rules/services/builtins/file_length/`
- `packages/devkit/tests/unit/features/rules/`
- `packages/devkit/tests/integration/features/rules/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/adr-consolidation/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/feedback-consolidation/`
- `packages/devkit-spec/tests/integration/bundles/spec/`
- `docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md`
- `docs/development/reference/rules.md`
- `.devkit/config.toml`

### Excluded Boundaries:
- `docs/decisions/`
- `.devkit/managed/`
- `docs/capabilities/documents/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
