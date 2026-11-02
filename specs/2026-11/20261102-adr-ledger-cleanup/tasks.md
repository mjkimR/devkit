---
id: TASKS-adr-ledger-cleanup
spec: SPEC-adr-ledger-cleanup
plan: PLAN-adr-ledger-cleanup
---

# Task Breakdown: `SPEC-adr-ledger-cleanup` Topic compaction groups and retired stale ADR clauses

## Phase 1: Implementation

- [x] **Task 1.1**: Topic grouping ADR, capability rule, playbook and test
  - **_Boundary**: `docs/decisions/2026-11/20261102-group-compaction-by-topic.md`,
    `docs/decisions/2026-11/20261102-decision-ledger.md`, `docs/capabilities/documents/CAP-DOCS-document-model.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/adr-compaction/SKILL.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_playbook_discovery_guidance.py`
  - _Requirements: AC-01_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_playbook_discovery_guidance.py`
- [x] **Task 1.2**: Retiring ADR and pointer lines
  - **_Boundary**: `docs/decisions/2026-11/20261102-retire-native-approval-and-moved-ownership-clauses.md`,
    `docs/decisions/2026-10/20261022-proposal-acceptance.md`,
    `docs/decisions/2026-10/20261022-mcp-runtime-and-shared-artifacts.md`,
    `docs/decisions/2026-11/20261102-document-system.md`, `docs/decisions/2026-11/20261102-steering-documents.md`
  - _Requirements: AC-02_
  - **Verification**: `uv run devkit rules check docs/decisions`
- [x] **Task 1.3**: Feedback dispositions and checks
  - **_Boundary**: `specs/2026-11/feedback/`
  - _Requirements: AC-03_
  - **Verification**: `uv run devkit rules check`; `just test-affected`
