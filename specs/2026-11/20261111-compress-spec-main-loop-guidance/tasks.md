---
id: TASKS-compress-spec-main-loop-guidance
spec: SPEC-compress-spec-main-loop-guidance
plan: PLAN-compress-spec-main-loop-guidance
---

# Task Breakdown: `SPEC-compress-spec-main-loop-guidance` Compress the spec guidance of the main development loop

## Phase 1: Policy pass
- [ ] **Task 1.1**: Group A (constitution, `spec` skill and its envelope, worker-records and completion references)
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/AGENTS.md.jinja, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test-affected --base <base>`
- [ ] **Task 1.2**: Group B (`sdd-spec-feature` and the specify, plan, tasks, review and sync skills)
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/workflows/sdd-spec-feature.md, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test-affected --base <base>`
- [ ] **Task 1.3**: Group C (development-worker contract, delegate, orchestrate and integrate skills, isolated-execution)
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/development-worker.md.jinja, packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test-affected --base <base>`

## Phase 2: Projection and checks
- [ ] **Task 2.1**: Run `devkit sync`, commit the projections and run the full check set
  - **_Boundary**: .devkit/installation.json, packages/devkit-spec/tests/
  - _Requirements: AC-03_
  - **Verification**: `uv run devkit rules check --ci --base <base>`; `uv run devkit sync --check`
