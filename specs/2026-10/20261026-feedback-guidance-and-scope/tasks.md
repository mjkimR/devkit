---
id: TASKS-feedback-guidance-and-scope
spec: SPEC-feedback-guidance-and-scope
plan: PLAN-feedback-guidance-and-scope
---

# Task Breakdown: `SPEC-feedback-guidance-and-scope` Scratch cleanup guidance, merge-conflict interaction and declared feedback scope

## Phase 1: Implementation

- [x] **Task 1**: Scratch cleanup guidance in the worker contracts and payload reference, with guidance tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/planning-worker.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_role_contracts.py`, `packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`, `packages/devkit-spec/tests/integration/bundles/spec/test_scratch_cleanup_guidance.py`, `.devkit/installation.json` (the tracked `devkit sync` output), `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `specs/2026-10/20261026-review-refactor/feedback/fixture-removal-denied.md`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec`

- [x] **Task 2**: A materials merge conflict raises `SPEC_PROPOSAL_TARGET_EXISTS` as `INTERACTION`, with tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/handoff.py`, `packages/devkit-spec/src/devkit_spec/base/errors.py`, `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff_merge.py`, `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff.py`, `docs/capabilities/delivery/CAP-DLV-proposal-incubation.md`, `specs/2026-10/20261026-merge-proposal-materials-at-handoff/feedback/merge-conflict-guardrail-action.md`
  - _Requirements: AC-03, AC-04_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/proposals`

- [x] **Task 3**: Declared feedback files of other spec bundles enter the scope, with tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/entrypoints/services/derive.py`, `packages/devkit-spec/src/devkit_spec/features/entrypoints/__init__.py`, `packages/devkit-spec/src/devkit_spec/features/scope/usecases/inputs.py`, `packages/devkit-spec/tests/integration/features/scope/test_inputs.py`, `packages/devkit-spec/tests/integration/features/entrypoints/test_derive.py`, `docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md`, `docs/capabilities/traceability/CAP-TRACE-code-entrypoints.md`, `specs/2026-10/20261024-canonical-libyaml-only/feedback/scope-external-feedback-target.md`
  - _Requirements: AC-05, AC-06, AC-07_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/scope packages/devkit-spec/tests/integration/features/entrypoints`

- [x] **Task 4**: Living Spec and guide corrections for items 4-8
  - **_Boundary**: `packages/devkit-spec/README.md`, `guides/install/mcp.md`, `docs/glossary.md`, `docs/architecture/ARCH-04-1-ecosystem-boundaries.md`, `docs/capabilities/worktree/CAP-WT-task-worktrees.md`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `specs/2026-10/20261026-living-spec-consistency-sweep/feedback/handoff-error-modes-documented-differently.md`, `specs/2026-10/20261026-living-spec-consistency-sweep/feedback/spec-readme-and-mcp-guide-native-handoff.md`, `specs/2026-10/20261026-living-spec-consistency-sweep/feedback/integration-mcp-glossary-and-actor-row.md`, `specs/2026-10/20261026-living-spec-consistency-sweep/feedback/worktree-module-layout-stale.md`, `specs/2026-10/20261026-living-spec-consistency-sweep/feedback/sync-config-template-example-stale.md`, `specs/2026-10/20261026-feedback-guidance-and-scope/feedback/`
  - _Requirements: AC-08_
  - **Verification**: `uv run devkit rules check --ci --base f35e2b8e`; `rg -n "native handoff|\*\*Integration MCP|via MCP|worktree = true" packages/devkit-spec/README.md guides/install/mcp.md docs/glossary.md docs/architecture/ARCH-04-1-ecosystem-boundaries.md docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md` prints nothing
