---
id: TASKS-justfile-standard-templates
spec: SPEC-justfile-standard-templates
plan: PLAN-justfile-standard-templates
---

# Task Breakdown: SPEC-justfile-standard-templates

- [x] **Task 1**: Ship the opt-in creation instruction and validate selection/discovery.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/command_design/`, `packages/devkit-catalog/pyproject.toml`, `packages/devkit-catalog/tests/integration/bundles/test_bundles.py`, `packages/devkit-catalog/README.md`, `docs/capabilities/distribution/CAP-DIST-content-packages.md`, `docs/capabilities/harness/CAP-HARN-command-design.md`, `docs/usecases/harness/UC-design-command-entrypoints.md`, `uv.lock`, `docs/proposals/PROP-multi-runtime-project-harness/proposal.md`, `docs/proposals/PROP-multi-runtime-project-harness/target-docs.md`, `.devkit/architecture.toml`
  - _Requirements: AC-01, AC-02_
  - **Verification**: catalog manifest/deployment tests and scenario review, lint/types and rules.
- [x] **Task 2**: Add concrete native command reuse and optional recipe examples.
  - **_Boundary**: `guides/install/existing-repository.md`, `guides/install/new-repository.md`, `guides/install/bundle-recommendations.md`
  - _Requirements: AC-03_
  - **Verification**: temporary Node fixture, guide walkthrough and document rules.

## Host-authorized boundary additions

The Host admits `.devkit/architecture.toml` solely to register the new content root required by
ARCH-05-2-components; no import exceptions or feature edges change. The two deferred proposal files are
link-repair-only scope: the handed-off onboarding work now resolves as SPEC-justfile-standard-templates.
These are explicit direct-mode Host scope choices within the approved bundle delivery, not worker self-admission.
