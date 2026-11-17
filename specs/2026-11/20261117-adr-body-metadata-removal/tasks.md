---
id: TASKS-adr-body-metadata-removal
spec: SPEC-adr-body-metadata-removal
plan: PLAN-adr-body-metadata-removal
---

# Task Breakdown: `SPEC-adr-body-metadata-removal` Remove the ADR body metadata block and trim the ADR template

## Phase 1: Template, scaffold and handoff

- [x] **Task 1.1**: Trim the decision template and state the frontmatter-only status in decision-writing, with a template test
  - **_Boundary**: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/decision.md, packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/decision-writing.md, packages/devkit-docs/tests/integration/bundles/docs/, .devkit/installation.json (sync output)
  - _Requirements: AC-01, AC-02_
  - **Verification**: `uv run pytest packages/devkit-docs/tests/integration/bundles/docs packages/devkit-spec/tests/integration/bundles/spec`
- [x] **Task 1.2**: Stop the PADR scaffold writing the block and replace the handoff body rewrite with the legacy-block deletion
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/proposals/, packages/devkit-spec/tests/integration/features/proposals/
  - _Requirements: AC-03, AC-04_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/integration/features/proposals`

## Phase 2: Living Spec

- [x] **Task 2.1**: Remove the block from the existing ADRs, keeping reference edges and the named exceptions
  - **_Boundary**: docs/decisions/
  - _Requirements: AC-05_
  - **Verification**: the `rg` command of AC-05; `uv run devkit rules check docs/decisions`
- [x] **Task 2.2**: Restate the PADR body and promotion in the capabilities and the design's observed-run row
  - **_Boundary**: docs/capabilities/delivery/CAP-DLV-proposal-planning.md, docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md, docs/designs/delivery/DESIGN-proposal-handoff/design.md
  - _Requirements: AC-06_
  - **Verification**: the `rg` command of AC-06; `uv run devkit rules check docs/capabilities/delivery docs/designs/delivery`
- [ ] **Task 2.3**: Run the full verification set
  - **_Boundary**: .devkit/installation.json (sync output)
  - _Requirements: AC-07_
  - **Verification**: `just lint-check`; `uv run devkit generated check`; `uv run devkit rules check --ci --base main`; `just test-affected --base main`
