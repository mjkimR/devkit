---
id: TASKS-guidance-followups
spec: SPEC-guidance-followups
plan: PLAN-guidance-followups
---

# Task Breakdown: `SPEC-guidance-followups` Align milestone tone, role shell notes and traceability follow-ups

## Phase 1: Living Spec

- [ ] **Task 1.1**: Milestone granularity as a recommendation in the agent guidance capability
  - **_Boundary**: `docs/capabilities/harness/CAP-HARN-agent-guidance.md`
  - _Requirements: AC-01_
  - **Verification**: `rg -n "SHOULD" docs/capabilities | rg -i milestone` prints nothing; `uv run devkit rules check`
- [ ] **Task 1.2**: Traceability link between the integration use case and the runtime registration capability
  - **_Boundary**: `docs/usecases/delivery/UC-drive-development-to-integration.md`, `docs/capabilities/mcp/CAP-MCP-runtime-registration.md`
  - _Requirements: AC-03_
  - **Verification**: `uv run devkit rules check`

## Phase 2: Spec bundle guidance

- [ ] **Task 2.1**: Drop the stale no-shell note and name the reconcile-check command, with guidance tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/SKILL.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_role_shell_guidance.py`, `.devkit/managed/`, `.claude/`
  - _Requirements: AC-02, AC-04_
  - **Verification**: `just test-affected`, `uv run devkit sync --check`
