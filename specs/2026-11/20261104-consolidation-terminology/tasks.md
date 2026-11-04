---
id: TASKS-consolidation-terminology
spec: SPEC-consolidation-terminology
plan: PLAN-consolidation-terminology
---

# Task Breakdown: `SPEC-consolidation-terminology` Rename record compaction to consolidation

## Phase 1: Bundle

- [x] **Task 1**: Rename the two playbooks with aliases, reword their bodies and the bundle guidance, and update the bundle tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/`, `packages/devkit-spec/tests/integration/bundles/spec/`
  - _Requirements: AC-01, AC-02, AC-05_
  - **Verification**: `just test devkit-spec bundles`; `uv run devkit playbook get spec/adr-compaction`

## Phase 2: Records and Living Spec

- [x] **Task 2**: Rename the feedback records with their old IDs as aliases and rewrite references
  - **_Boundary**: `specs/2026-10/feedback/`, `specs/2026-11/feedback/`, current documents `devkit rules fix` rewrites
  - _Requirements: AC-03_
  - **Verification**: `uv run devkit docs resolve FB-compacted-delivery-promoted`; `uv run devkit rules check`
- [x] **Task 3**: Reword the capabilities, the ledger ADRs and the glossary, and write the rename ADR
  - **_Boundary**: `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/capabilities/documents/CAP-DOCS-document-model.md`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/decisions/2026-11/`, `docs/steering/glossary.md`
  - _Requirements: AC-04, AC-05_
  - **Verification**: the AC-04 and AC-05 `rg` lines; `uv run devkit rules check docs/`
- [x] **Task 4**: Regenerate the managed copies and the receipt
  - **_Boundary**: `.devkit/installation.json`, `.devkit/managed/` (regenerated), `.claude/` (projected)
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit sync --check`; `uv run devkit generated check`
