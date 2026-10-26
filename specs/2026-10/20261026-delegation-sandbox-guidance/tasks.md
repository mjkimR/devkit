---
id: TASKS-delegation-sandbox-guidance
spec: SPEC-delegation-sandbox-guidance
plan: PLAN-delegation-sandbox-guidance
---

# Task Breakdown: `SPEC-delegation-sandbox-guidance` Delegation scope and sandbox guidance fixes

## Phase 1: Implementation

- [ ] **Task 1.1**: Delegated write scope and baselines: payload, planning reference and development-worker contract, with guidance tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja`, `packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec`
- [ ] **Task 1.2**: Code-reviewer probe tests in an ignored path, with guidance tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/code-reviewer.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`
  - _Requirements: AC-03_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec`
- [ ] **Task 1.3**: Sandbox-safe worktree and Git metadata route in the worktree procedure, with guidance tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worktree.md.jinja`, `packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`
  - _Requirements: AC-04_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec`
- [ ] **Task 1.4**: Sync the bundle and resolve the five source feedback files
  - **_Boundary**: `.devkit/installation.json`, `AGENTS.md`, `specs/2026-10/20261026-release-handbook/feedback/bundle-change-needs-sync-scope.md`, `specs/2026-10/20261022-lint-clean-target-scoped-rules/feedback/base-measurement-outside-worker-git.md`, `specs/2026-10/20261026-viewer-planning-proposal-overlay/feedback/reviewer-probe-tests.md`, `specs/2026-10/20261024-proposal-review-auto-write/feedback/worktree-sandbox-location.md`, `specs/2026-10/20261023-cli-host-lifecycle/feedback/git-metadata-sandbox-boundary.md`
  - _Requirements: AC-05_
  - **Verification**: `uv run devkit sync --check` reports no change; `just rules-check`
