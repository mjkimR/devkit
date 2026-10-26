---
id: TASKS-living-spec-consistency-sweep
spec: SPEC-living-spec-consistency-sweep
plan: PLAN-living-spec-consistency-sweep
---

# Task Breakdown: `SPEC-living-spec-consistency-sweep` Living Spec consistency sweep

## Phase 1: Implementation

- [ ] **Task 1**: Delivery documents (items 1-6)
  - **_Boundary**: `docs/capabilities/delivery/`, `docs/usecases/delivery/UC-incubate-and-hand-off-a-proposal.md`,
    `docs/capabilities/integration/CAP-INT-mcp-services.md`, `docs/capabilities/worktree/CAP-WT-task-worktrees.md`
  - _Requirements: AC-01_
  - **Verification**: `rg -n "specrig|publish source-bound|Native MCP confirmation" docs/capabilities docs/usecases`
    returns no hit; `uv run devkit rules check docs`

- [ ] **Task 2**: Integration, MCP, host and viewer documents (items 7-11)
  - **_Boundary**: `docs/capabilities/integration/`, `docs/capabilities/mcp/`, `docs/capabilities/host/`,
    `docs/capabilities/viewer/`, `docs/development/reference/host.md`
  - _Requirements: AC-02_
  - **Verification**: `rg -n "remains authoritative|sweep-plan|integration MCP tools" docs/capabilities` returns no
    hit; `uv run devkit rules check docs`

- [ ] **Task 3**: Worktree, document, generated and distribution contracts and help text (items 12-16)
  - **_Boundary**: `docs/capabilities/worktree/`, `docs/capabilities/documents/`, `docs/capabilities/generated/`,
    `docs/capabilities/distribution/`, `docs/capabilities/mcp/`,
    `packages/devkit/src/devkit_agt/features/worktree/cli.py`,
    `packages/devkit-spec/src/devkit_spec/features/documents/cli/commands.py`
  - _Requirements: AC-03_
  - **Verification**: `uv run devkit spec list --help` names `milestone`; `just lint devkit`, `just lint devkit-spec`,
    `just test-affected`

- [ ] **Task 4**: Governance and advisory documents (items 17-18)
  - **_Boundary**: `docs/capabilities/advisory/`, `docs/capabilities/governance/CAP-GOV-rules-engine.md`,
    `docs/development/reference/rules.md`
  - _Requirements: AC-04_
  - **Verification**: `rg -n "rules.phases" docs` returns no hit; `uv run devkit rules check docs`

- [ ] **Task 5**: Citations and the glossary (items 19-20)
  - **_Boundary**: `docs/architecture/ARCH-01-introduction-and-goals.md`, `docs/architecture/ARCH-05-1-containers.md`,
    `docs/capabilities/viewer/`, `docs/capabilities/distribution/CAP-DIST-content-packages.md`,
    `docs/capabilities/delivery/CAP-DLV-project-policy.md`, `docs/glossary.md`
  - _Requirements: AC-05_
  - **Verification**: the duplicate-citation `rg` patterns of `plan.md` §4 return no hit; `uv run devkit rules check docs`

- [ ] **Task 6**: Source feedback fixes and resolution (items 21-22)
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/cli/output.py`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/classification.md`,
    `.devkit/installation.json`, `specs/2026-10/20261026-review-refactor/feedback/`
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit sync --help` shows the shared `-w` text; `uv run devkit sync --check`;
    `just lint devkit-dist`, `just test-affected`
