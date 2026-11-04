---
id: TASKS-namespace-steering-registers
spec: SPEC-namespace-steering-registers
plan: PLAN-namespace-steering-registers
---

# Task Breakdown: `SPEC-namespace-steering-registers`

## Implementation

- [x] **Task 1**: Permit canonical namespace registers and validate glossary references with migration regressions.
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/`, `packages/devkit-docs/tests/integration/features/governance/`, `packages/devkit-docs/tests/integration/features/documents/test_namespaces.py`
  - _Requirements: AC-01, AC-05_
  - **Verification**: deployed steering_documents and document_reference rule tests after sync.
- [x] **Task 2**: Expand search from the existing namespace selection with exact-file error targets.
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/documents/`, `packages/devkit-docs/tests/integration/features/documents/`
  - _Requirements: AC-02, AC-03, AC-04_
  - **Verification**: selected/cwd/global/all/absent/invalid/unregistered search regressions.
- [x] **Task 3**: Align docs/spec writing, drafting, review and sync guidance and record the accepted decision.
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/`, `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/seed/docs/ux/README.md`, `packages/devkit-docs/tests/integration/bundles/docs/test_steering_guidance.py`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-ux-review/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-specify/`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/references/payload.md`, `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`, `packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py`, `docs/decisions/2026-11/20261104-namespace-steering-registers.md`, `docs/decisions/2026-11/20261104-namespace-steering-directories.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-06_
  - **Verification**: guidance integration tests; agent asset wording checks.
