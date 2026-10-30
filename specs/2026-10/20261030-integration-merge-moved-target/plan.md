---
id: PLAN-integration-merge-moved-target
spec: SPEC-integration-merge-moved-target
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-integration-merge-moved-target` Integrate a conflict-free moved target without requiring the source to contain it

## 1. Architecture Overview & Impact
- Target Area: capabilities/worktree/

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit/src/devkit_agt/features/worktree/`
- `packages/devkit/src/devkit_agt/features/integration/`
- `packages/devkit/tests/`
- `packages/devkit-spec/src/devkit_spec/features/delivery/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-integrate/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/`
- `packages/devkit-spec/tests/`
- `docs/capabilities/worktree/`
- `docs/capabilities/integration/`
- `docs/capabilities/delivery/`
- `docs/capabilities/harness/CAP-HARN-agent-guidance.md`
- `docs/usecases/delivery/UC-drive-development-to-integration.md`
- `docs/decisions/2026-10/20261022-local-and-pull-request-integration.md`
- `docs/decisions/2026-10/20261022-test-selection-and-ci.md`
- `docs/development/`
- `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/`
- `guides/INSTALL_GUIDE.md`
- `AGENTS.md`

### Excluded Boundaries:
- `.devkit/managed/`
- `packages/devkit-core/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
