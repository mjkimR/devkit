---
id: PLAN-standalone-devkit-mcp
spec: SPEC-standalone-devkit-mcp
---
<!-- devkit:skeleton -->

# Technical Plan: `SPEC-standalone-devkit-mcp` Independent devkit-mcp runtime and default approval integration

## 1. Architecture Overview & Impact
- Target Area: host/
- Target Docs Blueprint: `PROP-standalone-devkit-mcp-target` (Living Spec targets for this plan and reconcile.md)

## 2. Component Breakdown & Interface Contracts

### Planned Boundaries:
- `packages/`
- `pyproject.toml`
- `uv.lock`
- `justfile`
- `AGENTS.md`
- `.github/workflows/`
- `docs/architecture/`
- `docs/development/`
- `docs/decisions/`
- `packages/devkit-dist/src/devkit/core/`
- `packages/devkit-dist/src/devkit/host/`
- `packages/devkit-dist/src/devkit/distribution/`
- `packages/devkit/src/devkit/integration/`
- `packages/devkit-spec/src/devkit_spec/handoff_mcp.py`
- `packages/devkit-spec/src/devkit_spec/bundle/skills/spec/`
- `scripts/`
- `guides/install/`
- `docs/capabilities/host/`
- `docs/capabilities/integration/`
- `docs/capabilities/delivery/`
- `docs/capabilities/worktree/`

### Excluded Boundaries:
- `packages/devkit-advisory/`
- `packages/devkit-spec/src/devkit_spec/scope/`

## 3. Verification & Test Plan
- <commands and checks that verify the acceptance criteria>
