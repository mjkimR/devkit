---
id: TASKS-nightly-ci-verification
spec: SPEC-nightly-ci-verification
plan: PLAN-nightly-ci-verification
---

# Task Breakdown: `SPEC-nightly-ci-verification`

- [ ] **Task 1**: Schedule full CI with successful-head gating and regression checks
  - **_Boundary**: `.github/workflows/nightly.yml`, `.github/workflows/ci.yml`, `.github/scripts/nightly-ci.cjs`, `.github/scripts/nightly-ci.test.cjs`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `node --test .github/scripts/nightly-ci.test.cjs`
- [ ] **Task 2**: Align local verification, review and integration policy
  - **_Boundary**: `AGENTS.md`, `docs/development/ci-cd.md`, `docs/development/workflow.md`, `docs/development/setup.md`,
    `docs/decisions/2026-10/20261019-nightly-ci-verification.md`,
    `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-plan/SKILL.md`,
    `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-review/SKILL.md`,
    `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-integrate/SKILL.md`, `scripts/affected_tests.py`
  - _Requirements: AC-04_
  - **Verification**: `just test-affected`, `just lint-check`, `just check`, `just rules-check`
