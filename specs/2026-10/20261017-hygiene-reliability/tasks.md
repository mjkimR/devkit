---
id: TASKS-hygiene-reliability
spec: SPEC-hygiene-reliability
plan: PLAN-hygiene-reliability
---

# Task Breakdown: Hygiene reliability

- [x] **Task 1**: Preserve automatic hook fallbacks with regression coverage.
  - **_Boundary**: `packages/devkit/src/devkit/gate/hooks/hooks.py`, `packages/devkit/src/devkit/gate/hooks/local_config.py`, `packages/devkit/tests/gate/test_sync_interpreters.py`, `specs/2026-10/feedback/20261015-worktree-sync-repoints-the-hook-interpreter.md`
  - _Requirements: AC-01, AC-02_
- [x] **Task 2**: Resolve scope revisions before writing envelopes, with CLI regression coverage.
  - **_Boundary**: `packages/devkit/src/devkit/workflow/cli/envelope.py`, `packages/devkit/tests/workflow/test_hygiene_authoring.py`, `specs/2026-10/20261015-handoff-unit-records/feedback/envelope-head-accepts-unknown-commit.md`
  - _Requirements: AC-03, AC-04_
- [x] **Task 3**: Preserve optional finding severity with round-trip and invalid-input tests.
  - **_Boundary**: `packages/devkit/src/devkit/workflow/unit/envelope/model.py`, `packages/devkit/src/devkit/workflow/unit/envelope/authoring.py`, `packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/envelope.md`, `packages/devkit/tests/workflow/test_hygiene_authoring.py`, `specs/2026-10/20261016-planning-effort-safeguards/feedback/envelope-findings-reject-severity.md`
  - _Requirements: AC-05_
- [x] **Task 4**: Split the library reference and repair inbound links.
  - **_Boundary**: `docs/development/reference/rules.md`, `docs/development/reference/rules-library.md`, `docs/capabilities/governance/CAP-GOV-rule-authoring.md`, `packages/devkit/tests/rules/test_docs.py`
  - _Requirements: AC-06_
