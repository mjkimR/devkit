---
id: TASKS-scope-activity-write-evidence
spec: SPEC-scope-activity-write-evidence
plan: PLAN-scope-activity-write-evidence
---

# Task Breakdown: `SPEC-scope-activity-write-evidence`

## Implementation

- [x] **Task 1**: Horizon labels, pair and summary counts in `collect` JSON and text, with integration tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/scope/services/collection.py`, `packages/devkit-spec/src/devkit_spec/features/scope/services/observation.py`, `packages/devkit-spec/src/devkit_spec/features/scope/cli/collection_output.py`, `packages/devkit-spec/tests/integration/features/scope/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/scope/`

- [x] **Task 2**: Coverage problem `inputs` and the self-base guard, with integration tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/scope/services/collection.py`, `packages/devkit-spec/src/devkit_spec/features/scope/services/observation.py`, `packages/devkit-spec/tests/integration/features/scope/`
  - _Requirements: AC-05, AC-06, AC-07_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/scope/`

- [x] **Task 3**: Host scheduling text and the Living Spec contract
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/SKILL.md.jinja`, `docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/usecases/collaboration/UC-run-parallel-work-safely.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-08_
  - **Verification**: `uv run devkit sync --check`, `just rules-check`
