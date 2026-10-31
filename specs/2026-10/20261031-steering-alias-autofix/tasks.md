---
id: TASKS-steering-alias-autofix
spec: SPEC-steering-alias-autofix
plan: PLAN-steering-alias-autofix
---

# Task Breakdown: `SPEC-steering-alias-autofix`

## Phase 1: Implementation

- [x] **Task 1**: Add steering and glossary Owner alias autofix with deployed regression tests.
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/usecases/document_reference.py`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/`, `docs/capabilities/governance/CAP-GOV-spec-rules.md`, `specs/2026-10/20261030-alias-references-in-quick-references/feedback/steering-citations-not-fixable.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `uv run devkit rules test RULE-document-reference`, `just lint-check docs`, `just check docs`, `just test-affected`
