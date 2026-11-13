---
id: PLAN-linter-change-notices
spec: SPEC-linter-change-notices
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-linter-change-notices` Non-blocking rule notices for changed code

## 1. Architecture Overview & Impact
- Target Area: governance/
- Target Docs Blueprint: `PROP-linter-change-notices-target` (Living Spec targets for this plan and reconcile.md)

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit/src/devkit_agt/features/rules/`
- `packages/devkit/src/devkit_agt/features/gate/usecases/gates/rules.py`
- `packages/devkit/src/devkit_agt/features/gate/models/errors.py`
- `packages/devkit/tests/unit/features/rules/`
- `packages/devkit/tests/integration/features/rules/`
- `packages/devkit/tests/integration/features/gate/`
- `packages/devkit/tests/integration/features/workflow/`
- `packages/devkit/tests/e2e/features/gate/`
- `packages/devkit/README.md`
- `docs/capabilities/governance/CAP-GOV-rules-engine.md`
- `docs/capabilities/governance/CAP-GOV-evaluation-lifecycle.md`
- `docs/capabilities/governance/CAP-GOV-rule-authoring.md`
- `docs/capabilities/gate/CAP-GATE-commit-gates.md`
- `docs/development/reference/rules.md`
- `docs/decisions/`

### Excluded Boundaries:
- `packages/devkit-dist/`
- `packages/devkit-mcp/`
- `packages/devkit-spec/`
- `packages/devkit/src/devkit_agt/features/workflow/`
- `packages/devkit/src/devkit_agt/features/rules/services/builtins/secret_leak/`
- `.devkit/architecture.toml`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
