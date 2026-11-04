---
id: PLAN-post-merge-verification
spec: SPEC-post-merge-verification
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-post-merge-verification` Verify integration after merging with the resulting runtime

## 1. Architecture Overview & Impact
- Target Area: integration/
- Target Docs Blueprint: `PROP-post-merge-verification-target` (Living Spec targets for this plan and reconcile.md)

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit/src/devkit_agt/features/integration/`
- `packages/devkit/src/devkit_agt/features/worktree/`
- `packages/devkit/pyproject.toml`
- `packages/devkit/tests/`
- `packages/devkit-spec/src/devkit_spec/`
- `packages/devkit-spec/pyproject.toml`
- `packages/devkit-spec/tests/`
- `docs/capabilities/integration/`
- `docs/capabilities/delivery/`
- `docs/capabilities/governance/`
- `docs/capabilities/worktree/`
- `docs/capabilities/harness/`
- `docs/usecases/`
- `docs/architecture/`
- `docs/decisions/`
- `docs/development/`
- `AGENTS.md`
- `.devkit/config.toml`
- `guides/`

### Excluded Boundaries:
- `packages/devkit-dist/src/`
- `packages/devkit-mcp/src/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
