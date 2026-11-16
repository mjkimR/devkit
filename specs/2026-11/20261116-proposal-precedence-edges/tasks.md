---
id: TASKS-proposal-precedence-edges
spec: SPEC-proposal-precedence-edges
plan: PLAN-proposal-precedence-edges
---

# Task Breakdown: `SPEC-proposal-precedence-edges` Ordering claims between proposals checked when made

- [x] **Task 1**: Bundle-text and branch-check tests for the ordering-claim guidance
  - **_Boundary**: `packages/devkit-spec/tests/integration/bundles/spec/test_ordering_claim_guidance.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/integration/bundles/spec/test_ordering_claim_guidance.py`
    fails on the guidance clauses before Task 2 and passes after it.

- [x] **Task 2**: Backlog and Planning references check named proposals' handoff state
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/backlog.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02, AC-05_
  - **Verification**: the Task 1 test and `test_bundle_budgets.py`; `uv run devkit sync --check` after `devkit sync`.

- [x] **Task 3**: Capability statement owns the two checks
  - **_Boundary**: `docs/capabilities/harness/CAP-HARN-agent-guidance.md`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit rules check --ci --base main`.
