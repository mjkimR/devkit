---
id: TASKS-rename-incubation-to-adaptive-dev
spec: SPEC-rename-incubation-to-adaptive-dev
plan: PLAN-rename-incubation-to-adaptive-dev
---

# Task Breakdown: `SPEC-rename-incubation-to-adaptive-dev` Rename incubation to adaptive-dev and disambiguate proposal terms

## Phase 1: Code and bundles

- [x] **Task 1.1**: Approach value `adaptive-dev` in the parser, its readers and their tests
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/`, `packages/devkit-dist/tests/`, `packages/devkit-dist/README.md`, `packages/devkit-spec/src/devkit_spec/features/`, `packages/devkit-spec/tests/`, `packages/devkit-spec/README.md`, `packages/devkit/src/devkit_agt/features/integration/`, `packages/devkit/tests/`, `packages/devkit/README.md`
  - _Requirements: AC-02, AC-03_
  - **Verification**: `just test devkit-dist tests/integration/features/project`, `just test devkit-spec`, `just test devkit tests/integration/features/integration`
- [x] **Task 1.2**: Rename the catalog bundle to `adaptive-dev`, with its entry point, data root and tests
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/`, `packages/devkit-catalog/tests/`, `packages/devkit-catalog/README.md`, `packages/devkit-catalog/pyproject.toml`, `packages/devkit-docs/tests/`, `.devkit/architecture.toml`
  - _Requirements: AC-04_
  - **Verification**: `just test devkit-catalog tests/integration/bundles tests/e2e/bundles`
- [x] **Task 1.3**: Spec bundle text and proposal CLI help use the new names, synced into this repository
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`, `packages/devkit-spec/src/devkit_spec/features/delivery/cli/`, `packages/devkit-spec/tests/`, `AGENTS.md` (sync output), `.devkit/installation.json` (sync output)
  - _Requirements: AC-07_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec tests/e2e/bundles/spec`, `uv run devkit sync --check`
- [x] **Task 1.4**: Consumer smoke test lists the renamed bundle
  - **_Boundary**: `tests/e2e/smoke.sh`
  - _Requirements: AC-05_
  - **Verification**: `just smoke`

## Phase 2: Living Spec and guides

- [x] **Task 2.1**: Rename the six documents with aliases, rewrite alias references and add the ADR pointers
  - **_Boundary**: `docs/capabilities/`, `docs/usecases/`, `docs/architecture/`, `docs/development/`, `docs/README.md`, `docs/proposals/README.md`, `docs/decisions/`, `docs/steering/glossary.md`, `docs/steering/glossary.yaml`, `specs/2026-10/20261015-orchestration-mode/feedback/`, `specs/2026-10/20261020-draft-direct-acceptance/feedback/`, `specs/2026-10/20261020-language-setting-coverage/feedback/`, `specs/2026-10/20261022-document-id-aliases-and-compaction/feedback/`, `specs/2026-10/20261026-feedback-guidance-and-scope/feedback/`, `specs/2026-10/20261026-handoff-modes-and-template-report/feedback/`, `specs/2026-10/20261026-living-spec-consistency-sweep/feedback/`, `specs/2026-10/20261026-merge-proposal-materials-at-handoff/feedback/`, `specs/2026-10/20261028-incubation-development-guidance/feedback/`, `specs/2026-10/feedback/`, `specs/2026-10/20261030-rename-incubation-to-adaptive-dev/`
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit docs resolve <old ID>` for each old ID, `just rules-check`
- [x] **Task 2.2**: Guides describe only the adaptive-dev bundle and approach
  - **_Boundary**: `guides/`
  - _Requirements: AC-01_
  - **Verification**: `just test devkit-catalog tests/integration/bundles`, `git diff --check`
- [x] **Task 2.3**: Allowlisted acceptance check over tracked files
  - **_Boundary**: `.devkit/transient/probe/` (ignored scratch, not committed)
  - _Requirements: AC-01_
  - **Verification**: `git ls-files -z | xargs -0 rg --hidden -i -n incubat` classified by `.devkit/transient/probe/allowlist.py`: zero unclassified lines
