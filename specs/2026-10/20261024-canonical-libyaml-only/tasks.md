---
id: TASKS-canonical-libyaml-only
spec: SPEC-canonical-libyaml-only
plan: PLAN-canonical-libyaml-only
---

# Task Breakdown: `SPEC-canonical-libyaml-only` Require libyaml for consistent YAML parsing

## Phase 1: Shared parser and frontmatter

- [x] **Task 1**: Add the shared LibYAML safe parser, distinct dependency error, and frontmatter integration
  - **_Boundary**: `packages/devkit-core/src/devkit_core/core/yaml.py`, `packages/devkit-core/src/devkit_core/core/frontmatter.py`, `packages/devkit-core/src/devkit_core/core/__init__.py`, `packages/devkit-core/src/devkit_core/base/errors.py`, `packages/devkit-core/tests/unit/core/`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test devkit-core unit/core`

## Phase 2: Document and governance readers

- [x] **Task 2**: Migrate document index, memo, and spec-governance value and node readers
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/documents/`, `packages/devkit-spec/src/devkit_spec/features/governance/usecases/code_entrypoints.py`, `packages/devkit-spec/src/devkit_spec/features/governance/usecases/proposal_boundaries.py`, `packages/devkit-spec/src/devkit_spec/features/governance/usecases/traceability_link.py`, `packages/devkit-spec/src/devkit_spec/features/governance/usecases/spec_format.py`, `packages/devkit-spec/tests/unit/features/documents/`, `packages/devkit-spec/tests/unit/features/governance/`, `packages/devkit-spec/tests/integration/features/documents/`, `packages/devkit-spec/tests/integration/features/entrypoints/`, `packages/devkit-spec/tests/integration/features/governance/`
  - _Requirements: AC-01, AC-02, AC-03, AC-05, AC-06_
  - **Verification**: `just test devkit-spec unit/features/documents unit/features/governance` and `just test devkit-spec integration/features/documents integration/features/entrypoints integration/features/governance`

## Phase 3: Standalone application readers

- [x] **Task 3**: Migrate proposal report, distribution invocation, and workflow YAML readers with error propagation
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/report.py`, `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/invocation.py`, `packages/devkit/src/devkit_agt/features/workflow/repositories/unit/decisions.py`, `packages/devkit/src/devkit_agt/features/workflow/services/envelope/authoring.py`, `packages/devkit/src/devkit_agt/features/workflow/services/envelope/model.py`, `packages/devkit-spec/tests/integration/features/proposals/`, `packages/devkit-dist/tests/integration/features/distribution/test_skill_invocation.py`, `packages/devkit/tests/integration/features/workflow/`
  - _Requirements: AC-01, AC-02, AC-04_
  - **Verification**: `just test devkit-spec integration/features/proposals`; `just test devkit-dist integration/features/distribution`; `just test devkit integration/features/workflow`

## Phase 4: Installation, guidance, and consumer verification

- [x] **Task 4**: Document the parser prerequisite and verify installed consumers and source guidance
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/document-writing.md`, `packages/devkit-core/README.md`, `guides/INSTALL_GUIDE.md`, `guides/install/`, `tests/e2e/smoke.sh`, `.devkit/installation.json`
  - _Requirements: AC-01, AC-07_
  - **Verification**: `just smoke`; `just test-e2e`

