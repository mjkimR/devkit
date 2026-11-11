---
id: TASKS-remove-unused-cli-options
spec: SPEC-remove-unused-cli-options
plan: PLAN-remove-unused-cli-options
---

# Task Breakdown: `SPEC-remove-unused-cli-options` Remove unused CLI options

## Phase 1: Decision

- [x] **Task 1.1**: Record `ADR-remove-unused-cli-options-without-shims`, superseding in part the `--local-only`
  clause and follow-up of `ADR-single-local-landing-route`
  - **_Boundary**: `docs/decisions/2026-11/20261111-remove-unused-cli-options-without-shims.md`, `docs/decisions/2026-11/20261111-single-local-landing-route.md`
  - _Requirements: AC-03_
  - **Verification**: `uv run devkit rules check docs/decisions/2026-11/`

## Phase 2: Implementation

- [ ] **Task 2.1**: Remove `worktree finish --local-only`, with tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/worktree/cli.py`, `packages/devkit/tests/integration/features/worktree/test_cli.py`, `packages/devkit/tests/e2e/features/worktree/test_lifecycle.py`
  - _Requirements: AC-01_
  - **Verification**: `just test devkit tests/integration/features/worktree/test_cli.py tests/e2e/features/worktree/test_lifecycle.py`
- [ ] **Task 2.2**: Spec bundle guidance and Living Spec name plain `finish` for the remaining cleanup
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-integrate/SKILL.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worktree.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/references/git-operator-operations.md`, `docs/development/reference/integration.md`, `docs/development/reference/worktree.md`, `docs/capabilities/worktree/CAP-WT-task-worktrees.md`, `docs/capabilities/integration/CAP-INT-mcp-services.md`, `docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`
  - _Requirements: AC-02_
  - **Verification**: `uv run devkit sync --check` and the AC-02 `git grep`
- [ ] **Task 2.3**: Remove `host status --host`, with tests and the host reference
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/host/cli.py`, `packages/devkit-dist/tests/integration/features/host/test_hooks.py`, `docs/development/reference/host.md`
  - _Requirements: AC-04_
  - **Verification**: `just test devkit-dist tests/integration/features/host`
- [ ] **Task 2.4**: Remove `rules check|fix --summary-only`, with tests and the rules reference
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/rules/cli/commands.py`, `packages/devkit/src/devkit_agt/features/rules/cli/output.py`, `packages/devkit/tests/integration/features/rules/cli/test_commands.py`, `docs/development/reference/rules.md`
  - _Requirements: AC-05_
  - **Verification**: `just test devkit tests/integration/features/rules/cli`
- [ ] **Task 2.5**: Remove `workflow next --workflow` and `workflow handoff --date` with the use case parameters, with tests and the delivery contracts
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/workflow/cli/run.py`, `packages/devkit/src/devkit_agt/features/workflow/usecases/operations.py`, `packages/devkit/tests/integration/features/workflow/`, `docs/capabilities/delivery/CAP-DLV-cli-and-output.md`, `docs/capabilities/delivery/CAP-DLV-workflow-definitions.md`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `just test devkit tests/integration/features/workflow`
- [ ] **Task 2.6**: Remove `docs list --query` and the use case parameter, with tests and `CAP-DOCS-document-lookup`
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/documents/cli/commands.py`, `packages/devkit-docs/src/devkit_docs/features/documents/usecases/browse.py`, `packages/devkit-docs/tests/integration/features/documents/test_cli_documents.py`, `docs/capabilities/documents/CAP-DOCS-document-lookup.md`
  - _Requirements: AC-08_
  - **Verification**: `just test devkit-docs tests/integration/features/documents`
