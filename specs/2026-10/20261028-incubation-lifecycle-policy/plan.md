---
id: PLAN-incubation-lifecycle-policy
spec: SPEC-incubation-lifecycle-policy
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-incubation-lifecycle-policy` Apply explicit development approach policy across lifecycle consumers

## 1. Architecture Overview & Impact
- Target Area: delivery/
- Target Docs Blueprint: `PROP-incubation-lifecycle-policy-target` (Living Spec targets for this plan and reconcile.md)

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit-dist/`
- `packages/devkit/`
- `packages/devkit-spec/`
- `packages/devkit-docs/`
- `docs/capabilities/`
- `docs/usecases/`
- `docs/architecture/`
- `docs/decisions/`
- `docs/steering/glossary.md`
- `guides/`
- `tests/e2e/smoke.sh`
- `.devkit/config.toml`
- `.devkit/installation.json`
- `AGENTS.md`

### Excluded Boundaries:
- `packages/devkit-core/`
- `packages/devkit-advisory/`
- `packages/devkit-cli/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
