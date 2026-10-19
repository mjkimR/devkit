---
id: TASKS-high-effort-review-loop
spec: SPEC-high-effort-review-loop
plan: PLAN-high-effort-review-loop
---

# Task Breakdown: `SPEC-high-effort-review-loop` Bounded high-effort review procedure

Bundle paths are under `packages/devkit-spec/src/devkit_spec/bundle/`; tests under `packages/devkit-spec/tests/`.

- [ ] **Task 1**: The `high` loop reference and the effort rules, with their tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/review-loop.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/effort.md,
    packages/devkit-spec/tests/test_effort_procedure.py
  - _Requirements: AC-01, AC-02, AC-03, AC-05, AC-06_
  - **Verification**: `uv run pytest packages/devkit-spec/tests/test_effort_procedure.py packages/devkit-spec/tests/test_bundle_budgets.py`
- [ ] **Task 2**: Severity levels in the envelope reference, `spec-review` and the three reviewer contracts, and the
  reviewer round inputs in the payload table
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/envelope.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec-review/SKILL.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/references/payload.md,
    packages/devkit-spec/src/devkit_spec/bundle/subagents/code-reviewer.md,
    packages/devkit-spec/src/devkit_spec/bundle/subagents/reconcile-reviewer.md,
    packages/devkit-spec/src/devkit_spec/bundle/subagents/challenger.md,
    packages/devkit-spec/src/devkit_spec/bundle/subagents/scout.md,
    packages/devkit-spec/tests/test_effort_procedure.py
  - _Requirements: AC-04, AC-08_
- [ ] **Task 3**: Every other restatement of `high` cites the loop: workflow bodies, worker contracts, `spec-delegate`,
  `spec-sync`, `spec-orchestrate`, completion reference
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/workflows/,
    packages/devkit-spec/src/devkit_spec/bundle/subagents/development-worker.md,
    packages/devkit-spec/src/devkit_spec/bundle/subagents/planning-worker.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec-delegate/SKILL.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec-sync/SKILL.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec-orchestrate/SKILL.md,
    packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/completion.md,
    packages/devkit-spec/tests/test_effort_procedure.py, packages/devkit-spec/tests/test_role_contracts.py,
    .devkit/installation.json
  - _Requirements: AC-03, AC-05, AC-07, AC-09_
  - **Verification**: `uv run devkit workflow validate` and `uv run pytest packages/devkit-spec/tests`
