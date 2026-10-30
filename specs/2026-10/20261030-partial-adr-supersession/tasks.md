---
id: TASKS-partial-adr-supersession
spec: SPEC-partial-adr-supersession
plan: PLAN-partial-adr-supersession
---

# Task Breakdown: `SPEC-partial-adr-supersession` Keep partially superseded ADRs accepted and searchable

## Implementation

- [x] **Task 1**: State whole and partial supersession in the decision format, with guidance and rule tests
  - **_Boundary**: `docs/capabilities/documents/CAP-DOCS-document-model.md`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/decision-writing.md`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/seed/docs/decisions/README.md`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`, `docs/decisions/README.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/adr-compaction/SKILL.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test devkit-spec bundles/spec`, `just test devkit-docs bundles/docs`, `uv run devkit sync --check`

- [x] **Task 2**: Offer `supersedes` in the PADR scaffold and document it, with scaffold and handoff tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`, `packages/devkit-spec/tests/integration/features/proposals/test_proposal_scaffold.py`, `packages/devkit-spec/tests/integration/features/proposals/test_proposal_handoff.py`, `docs/capabilities/delivery/CAP-DLV-proposal-planning.md`
  - _Requirements: AC-03_
  - **Verification**: `just test devkit-spec features/proposals`, `just lint-check devkit-spec`, `just check devkit-spec`

- [x] **Task 3**: Correct the decision ledger
  - **_Boundary**: `docs/decisions/2026-10/` (status, `superseded_by`, body status lines and "Superseded in part by" lines of the ADRs in `PLAN-partial-adr-supersession` section 4; never `ADR-moved-target-merge`)
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit docs search "Local and Pull Request Integration"`, `uv run devkit docs list decision --status superseded -n 0`, `uv run devkit rules check`
