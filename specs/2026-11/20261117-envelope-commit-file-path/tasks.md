---
id: TASKS-envelope-commit-file-path
spec: SPEC-envelope-commit-file-path
plan: PLAN-envelope-commit-file-path
---

# [TASKS-envelope-commit-file-path] Envelope commit accepts a workspace-relative --file path

- [ ] **Task 1**: Regression tests reproducing the doubled path and the repeating fix
  - **_Boundary**: `packages/devkit/tests/integration/features/workflow/test_envelope_commit.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run pytest packages/devkit/tests/integration/features/workflow/test_envelope_commit.py`
- [ ] **Task 2**: Normalize a workspace-relative `--file` inside the Unit and name the Unit-relative form in the fix
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/workflow/usecases/commit_envelope.py`, `docs/capabilities/delivery/CAP-DLV-workflow-envelopes.md`, `docs/capabilities/delivery/CAP-DLV-cli-and-output.md`, `specs/2026-11/20261117-viewer-adr-summary-wording/feedback/envelope-commit-file-path-doubled.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run pytest packages/devkit/tests/integration/features/workflow/test_envelope_commit.py`, `just test-affected --base main`
