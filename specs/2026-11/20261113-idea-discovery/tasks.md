---
id: TASKS-idea-discovery
spec: SPEC-idea-discovery
plan: PLAN-idea-discovery
---

# Task Breakdown: `SPEC-idea-discovery`

- [x] **Task 1**: Add the discovery router, conditional execution/retention references and local roles.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/deep_research/bundle/`
  - _Requirements: AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: Skill validation, behavioral exercise and independent semantic review.
- [x] **Task 2**: Deploy discovery additively and verify upgrade, host projection and installed packaging.
  - **_Boundary**: `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py`, `packages/devkit-catalog/tests/e2e/bundles/deep_research/test_installed_consumer.py`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/SKILL.md.jinja`
  - _Requirements: AC-01, AC-05, AC-06_
  - **Verification**: Affected tests and selective wheel E2E.
- [x] **Task 3**: Document invocation, routing and the boundaries with research and solution exploration.
  - **_Boundary**: `packages/devkit-catalog/README.md`, `guides/install/bundle-recommendations.md`, `guides/INSTALL_GUIDE.md`, `guides/install/existing-repository.md`, `docs/capabilities/delivery/CAP-DLV-idea-discovery.md`, `docs/capabilities/delivery/CAP-DLV-deep-research.md`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/usecases/delivery/UC-discover-and-refine-an-idea.md`, `docs/steering/glossary.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: Rules, reference resolution and reconciliation review.
