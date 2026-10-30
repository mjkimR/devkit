---
id: PLAN-git-operator-result-readiness
spec: SPEC-git-operator-result-readiness
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-git-operator-result-readiness` Separate effect, readiness, permission and next actor in git-operator results

## 1. Architecture Overview & Impact
- Target Area: capabilities/delivery/

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/git-operator.md`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/references/`
- `packages/devkit-spec/src/devkit_spec/features/delivery/`
- `packages/devkit-spec/src/devkit_spec/features/proposals/`
- `packages/devkit-spec/src/devkit_spec/base/`
- `packages/devkit-spec/tests/`
- `docs/capabilities/delivery/`
- `docs/usecases/delivery/`

### Excluded Boundaries:
- `.devkit/managed/`
- `packages/devkit-core/`
- `docs/capabilities/worktree/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
