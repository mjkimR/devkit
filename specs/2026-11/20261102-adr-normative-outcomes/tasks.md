---
id: TASKS-adr-normative-outcomes
spec: SPEC-adr-normative-outcomes
plan: PLAN-adr-normative-outcomes
---

# Task Breakdown: `SPEC-adr-normative-outcomes` ADR normative outcomes and Living Spec restatement

## Phase 1: Authoring rule

- [x] **Task 1.1**: Decision Outcome clause format in decision-writing, the decision template and the completion
  classification, with guidance tests; `CAP-HARN-agent-guidance` row and its two ADR-only clauses
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/decision-writing.md`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py`,
    `docs/capabilities/harness/CAP-HARN-agent-guidance.md`,
    `docs/decisions/2026-10/*roadmap-and-milestones.md`, `docs/decisions/2026-10/*writing-and-terminology-guidance.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_writing_guidance.py`;
    `uv run devkit rules check --phase hygiene <edited bundle files>`

## Phase 2: Restatements (disjoint document scopes)

- [x] **Task 2.1**: Governance: snapshot-gate fix and read-only shared `DocumentIndex`
  - **_Boundary**: `docs/capabilities/governance/CAP-GOV-rule-authoring.md`,
    `docs/decisions/2026-10/*share-document-index-and-defer-catalog-build-in-rules-run.md`
  - _Requirements: AC-04, AC-05_
  - **Verification**: `uv run devkit rules check docs/capabilities/governance docs/decisions`
- [x] **Task 2.2**: Document model: kind-table accessor and editable ADR records
  - **_Boundary**: `docs/capabilities/documents/CAP-DOCS-document-model.md`,
    `docs/decisions/2026-10/*kind-definition-table-keyed-on-the-declared-kind-enum.md`,
    `docs/decisions/2026-10/*immutable-decisions-editable-records.md`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit rules check docs/capabilities/documents docs/decisions`
- [x] **Task 2.3**: Delivery: adaptive-dev naming and helper autonomy with escalation triggers
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-adaptive-development.md`,
    `docs/capabilities/delivery/CAP-DLV-project-policy.md`,
    `docs/decisions/2026-10/*adaptive-dev-approach-name.md`, `docs/decisions/2026-10/*delivery-decision-boundaries.md`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit rules check docs/capabilities/delivery docs/decisions`
- [x] **Task 2.4**: Distribution: response-style limits, approval and cloud/local text, `uv run devkit` invocation
  - **_Boundary**: `docs/capabilities/distribution/CAP-DIST-content-packages.md`,
    `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`,
    `docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md`,
    `docs/decisions/2026-10/*response-style.md`, `docs/decisions/2026-10/*configuration-language-and-rendering.md`,
    `docs/decisions/2026-10/*keep-uv-run-as-the-agent-facing-devkit-invocation.md`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit rules check docs/capabilities/distribution docs/decisions`
- [x] **Task 2.5**: Integration: GitHub adapter limits and the checks-pending flow
  - **_Boundary**: `docs/capabilities/integration/CAP-INT-mcp-services.md`,
    `docs/decisions/2026-10/*local-and-pull-request-integration.md`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit rules check docs/capabilities/integration docs/decisions`
- [x] **Task 2.6**: Architecture: generic-first and test-selection graph rules
  - **_Boundary**: `docs/architecture/ARCH-05-1-containers.md`, `docs/architecture/ARCH-07-deployment.md`,
    `docs/decisions/2026-10/*spec-package-on-devkit.md`, `docs/decisions/2026-10/*test-selection-and-ci.md`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit rules check docs/architecture docs/decisions`

## Phase 3: Integration checks

- [x] **Task 3.1**: Whole-change checks
  - **_Boundary**: `specs/2026-11/20261102-adr-normative-outcomes/`
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit rules check`; `uv run devkit rules check --phase hygiene`; `just test-affected`
