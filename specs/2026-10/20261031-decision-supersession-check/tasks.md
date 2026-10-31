---
id: TASKS-decision-supersession-check
spec: SPEC-decision-supersession-check
plan: PLAN-decision-supersession-check
---

# Task Breakdown: `SPEC-decision-supersession-check`

- [x] **Task 1**: Add and deploy the report-only decision supersession rule with behavioral tests and guidance.
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/usecases/decision_supersession.py`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/decision_supersession/`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/bundle.toml`, `docs/capabilities/documents/CAP-DOCS-document-model.md`, `docs/capabilities/governance/CAP-GOV-spec-rules.md`, `specs/2026-10/20261030-partial-adr-supersession/feedback/decision-supersession-consistency-unchecked.md`
  - **_Boundary**: `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `uv run devkit rules test RULE-decision-supersession`, `just test-affected`, `just lint-check docs`, `just check docs`.
