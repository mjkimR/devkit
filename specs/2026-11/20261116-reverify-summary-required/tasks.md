---
id: TASKS-reverify-summary-required
spec: SPEC-reverify-summary-required
plan: PLAN-reverify-summary-required
---

# Task Breakdown: `SPEC-reverify-summary-required` envelope reverify requires a summary that envelope commit accepts

- [ ] **Task 1**: Reproduction tests for the reverify writer and the commit refusal, kept as regression tests
  - **_Boundary**: `packages/devkit/tests/integration/features/workflow/test_envelope_commit.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-05_
  - **Verification**: `uv run pytest packages/devkit/tests/integration/features/workflow/test_envelope_commit.py` fails on the
    characterized defect before Task 2 and passes after it.

- [ ] **Task 2**: Writer refusal of a missing reverify summary and a commit refusal naming the failing field and flag
  - **_Boundary**: `packages/devkit/src/devkit_agt/features/workflow/services/envelope/authoring.py`, `packages/devkit/src/devkit_agt/features/workflow/services/envelope/commit.py`, `packages/devkit/src/devkit_agt/features/workflow/usecases/commit_envelope.py`, `packages/devkit/src/devkit_agt/features/workflow/models/envelope.py`, `packages/devkit/src/devkit_agt/features/workflow/cli/envelope.py`, `packages/devkit/tests/integration/features/workflow/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test-affected --base 22b28c936`; lint and pyright.

- [ ] **Task 3**: Agent-facing contract, reference and skill examples name `--summary` on `envelope reverify`
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-cli-and-output.md`, `docs/development/reference/workflow.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/SKILL.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run devkit rules check --ci --base main`; `uv run devkit sync --check` after `devkit sync`.
