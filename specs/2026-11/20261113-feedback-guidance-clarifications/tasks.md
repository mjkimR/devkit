---
id: TASKS-feedback-guidance-clarifications
spec: SPEC-feedback-guidance-clarifications
plan: PLAN-feedback-guidance-clarifications
---

# Task Breakdown: `SPEC-feedback-guidance-clarifications`

## Phase 1: Implementation

- [x] **Task 1**: Clarify reconcile closure and check provenance with instruction-contract regressions
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/envelope.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/review-loop.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_feedback_guidance.py`, `.devkit/installation.json` (sync output), `specs/2026-11/feedback/20261113-reconcile-check-no-per-finding-closure.md`, `specs/2026-11/feedback/20261113-envelope-check-status-vocabulary.md`
  - _Requirements: AC-01, AC-02_
  - **Verification**: Relevant spec bundle integration tests and the baseline/head probe.

- [x] **Task 2**: Clarify draft commit sequence and implementer UX closure with instruction-contract regressions
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-specify/SKILL.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-specify/references/screens.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-ux-review/SKILL.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_feedback_guidance.py`, `docs/capabilities/delivery/CAP-DLV-delivery-workflows.md`, `docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md`, `docs/development/reference/workflow.md`, `specs/2026-11/feedback/20261113-specify-task-coverage-before-tasks.md`, `specs/2026-11/feedback/20261113-ux-review-closure-stage-unnamed.md`
  - _Requirements: AC-03, AC-04_
  - **Verification**: Relevant spec bundle integration tests, native checks and cumulative document rules.

- [x] **Task 3**: Clarify the project style source fallback with instruction-contract regressions
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/ux-writing.md`, `packages/devkit-docs/tests/integration/bundles/docs/test_style_source_guidance.py`, `specs/2026-11/feedback/20261113-ux-writing-missing-style-file.md`
  - _Requirements: AC-05_
  - **Verification**: Relevant docs bundle integration tests, native checks and the baseline/head probe.

## Verification evidence

The five-scenario source probe reads the accepted base with git show: baseline 0/5, working source 5/5.
`just test devkit-spec integration/bundles/spec`: 685 passed; docs counterpart: 9 passed.
Lint/format and type checks passed for both packages. The initial spec suite found one wording-sensitive existing
assertion; retaining its two-round phrase while naming independent reviewers fixed it without weakening the test.
The tracked output of `devkit sync` is `.devkit/installation.json`; managed/projection outputs are ignored.
The required affected selector (`--base 021ad3c06c5ac0b3fffd8dad2fe931c2687db48e --tier all`) selected 163 paths
in partial mode and passed 2664 tests, including selected E2E. Source identity is the source-stage commit containing
these exact files; later record-only changes reuse these results. The selector's full fallback remains enabled.
