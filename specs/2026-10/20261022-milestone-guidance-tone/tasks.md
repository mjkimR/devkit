---
id: TASKS-milestone-guidance-tone
spec: SPEC-milestone-guidance-tone
plan: PLAN-milestone-guidance-tone
---

# Task Breakdown: `SPEC-milestone-guidance-tone` Recommend coarse milestones and allow merging small ones

## Phase 1: Decision

- [x] **Task 1.1**: New ADR for milestone merging with the partial-supersession pointer on the roadmap ADR
  - **_Boundary**: `docs/decisions/2026-10/20261022-milestone-merging.md`, `docs/decisions/2026-10/20261022-roadmap-and-milestones.md`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit spec resolve ADR-milestone-merging`, `uv run devkit rules check`

## Phase 2: Guidance

- [x] **Task 2.1**: Recommendation wording and merge procedure in the roadmap READMEs, milestone template and spec skill references, with guidance tests
  - **_Boundary**: `docs/roadmap/README.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/seed/docs/roadmap/README.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/templates/milestone.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/backlog.md.jinja`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/milestone-completion.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_milestone_completion_guidance.py`, `.devkit/managed/`, `.claude/`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test-affected`, `uv run devkit sync --check`
