---
id: PLAN-worker-shared-state-mcp
spec: SPEC-worker-shared-state-mcp
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-worker-shared-state-mcp` Shared state and workspace across worktrees and cloud agents

## 1. Architecture Overview & Impact
- Target Area: capabilities/collaboration/

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/devkit-dist/src/devkit/`
- `packages/devkit-dist/tests/`
- `packages/devkit-dist/pyproject.toml`
- `packages/devkit-dist/README.md`
- `packages/devkit-mcp/src/devkit_mcp/`
- `packages/devkit-mcp/tests/`
- `packages/devkit-mcp/README.md`
- `docs/capabilities/collaboration/`
- `docs/capabilities/mcp/`
- `docs/capabilities/harness/`
- `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-orchestrate/`
- `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/references/hosts.md`
- `packages/devkit-spec/tests/entrypoints/test_bundle.py`
- `docs/architecture/`
- `docs/development/reference/`

### Excluded Boundaries:
- `docs/decisions/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
