---
id: TASKS-feedback-guidance-clarifications
spec: SPEC-feedback-guidance-clarifications
plan: PLAN-feedback-guidance-clarifications
---

# Task Breakdown: `SPEC-feedback-guidance-clarifications`

## Phase 1: Implementation

- [ ] **Task 1**: Clarify reconcile closure and check provenance with instruction-contract regressions
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/envelope.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/review-loop.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_feedback_guidance.py`, `specs/2026-11/feedback/20261113-reconcile-check-no-per-finding-closure.md`, `specs/2026-11/feedback/20261113-envelope-check-status-vocabulary.md`
  - _Requirements: AC-01, AC-02_
  - **Verification**: Relevant spec bundle integration tests and the baseline/head probe.

- [ ] **Task 2**: Clarify draft commit sequence and implementer UX closure with instruction-contract regressions
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-specify/SKILL.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-specify/references/screens.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-ux-review/SKILL.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_feedback_guidance.py`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md`, `docs/development/reference/workflow.md`, `specs/2026-11/feedback/20261113-specify-task-coverage-before-tasks.md`, `specs/2026-11/feedback/20261113-ux-review-closure-stage-unnamed.md`
  - _Requirements: AC-03, AC-04_
  - **Verification**: Relevant spec bundle integration tests, native checks and cumulative document rules.

- [ ] **Task 3**: Clarify the project style source fallback with instruction-contract regressions
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/ux-writing.md`, `packages/devkit-docs/tests/integration/bundles/docs/test_style_source_guidance.py`, `specs/2026-11/feedback/20261113-ux-writing-missing-style-file.md`
  - _Requirements: AC-05_
  - **Verification**: Relevant docs bundle integration tests, native checks and the baseline/head probe.
