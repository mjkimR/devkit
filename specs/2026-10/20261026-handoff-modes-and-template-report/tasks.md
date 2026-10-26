---
id: TASKS-handoff-modes-and-template-report
spec: SPEC-handoff-modes-and-template-report
plan: PLAN-handoff-modes-and-template-report
---

# Task Breakdown: `SPEC-handoff-modes-and-template-report` Handoff refusal modes, reviewer probes, plain handoff role and template change report

## Phase 1: Implementation

- [ ] **Task 1**: Handoff refusal modes and fix texts, red then green, with the error table
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/base/errors.py`, `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py`, `packages/devkit-spec/tests/integration/features/delivery/test_handoff_error_modes.py`, `packages/devkit-spec/tests/e2e/features/delivery/test_integration.py`, `docs/capabilities/delivery/CAP-DLV-proposal-incubation.md`, `specs/2026-10/20261026-feedback-guidance-and-scope/feedback/handoff-refusals-emit-maintenance.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/delivery/test_handoff_error_modes.py`; `rg -n "report URI" docs/capabilities/delivery/CAP-DLV-proposal-incubation.md packages/devkit-spec/src` prints nothing

- [ ] **Task 2**: Code-reviewer probes in a per-round subdirectory, left for worktree removal
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/code-reviewer.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, the tracked outputs `devkit sync --check` lists, `specs/2026-10/20261026-feedback-guidance-and-scope/feedback/code-reviewer-probe-deletion.md`
  - _Requirements: AC-06_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`; `uv run devkit sync --check`

- [ ] **Task 3**: The plain handoff stated as the Host-run step after the decision
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-proposal-incubation.md`, `docs/capabilities/delivery/CAP-DLV-project-policy.md`, `specs/2026-10/20261026-living-spec-consistency-sweep/feedback/plain-handoff-skips-proposal-handoff-policy.md`
  - _Requirements: AC-07_
  - **Verification**: `rg -n "Host-run step" docs/capabilities/delivery/CAP-DLV-proposal-incubation.md docs/capabilities/delivery/CAP-DLV-project-policy.md` prints a line in each

- [ ] **Task 4**: config template change report pinned and stated
  - **_Boundary**: `packages/devkit-dist/tests/integration/features/distribution/test_config_template.py`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `docs/development/reference/distribution.md`, `specs/2026-10/20261026-living-spec-consistency-sweep/feedback/config-template-reports-unchanged-after-writing.md`
  - _Requirements: AC-08, AC-09_
  - **Verification**: `just test devkit-dist packages/devkit-dist/tests/integration/features/distribution/test_config_template.py`
