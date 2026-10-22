---
id: TASKS-writing-guidance-rollout
spec: SPEC-writing-guidance-rollout
plan: PLAN-writing-guidance-rollout
---

# Task Breakdown: `SPEC-writing-guidance-rollout` Roll out agent-asset-writing to bundle assets

## Phase 1: Rewrite batches

- [ ] **Task 1.1**: `spec` skill and its references backlog, branches, classification, completion
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/SKILL.md.jinja`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/backlog.md.jinja`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/branches.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/classification.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja`
  - _Requirements: AC-01, AC-02_
- [ ] **Task 1.2**: `spec` skill references effort through worktree
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/effort.md.jinja`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/envelope.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/feedback-retirement.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/git-policy.md.jinja`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/milestone-completion.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/planning.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/review-loop.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worker-records.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/worktree.md.jinja`
  - _Requirements: AC-01, AC-02_
- [ ] **Task 1.3**: `spec-delegate`, `spec-integrate`, `spec-orchestrate`, `spec-review-proposal`
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-delegate/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-integrate/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review-proposal/`
  - _Requirements: AC-01, AC-02_
- [ ] **Task 1.4**: `spec-next`, `spec-specify`, `spec-sync`, `spec-tasks`, `spec-review`, `spec-entrypoints`
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-specify/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-sync/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-tasks/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-review/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-entrypoints/`
  - _Requirements: AC-01, AC-02_
- [ ] **Task 1.5**: `spec-feedback`, `spec-rule` and the spec playbooks
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-feedback/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-rule/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/`
  - _Requirements: AC-01, AC-02_
- [ ] **Task 1.6**: Role contracts and the spec instructions `contract-authoring`, `living-spec-writing`
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/contract-authoring.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/living-spec-writing.md`
  - _Requirements: AC-01, AC-02_
- [ ] **Task 1.7**: devkit-dist, devkit, devkit-catalog and devkit-starter assets
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/bundles/`,
    `packages/devkit/src/devkit_agt/bundles/harness/bundle/instructions/`,
    `packages/devkit/src/devkit_agt/bundles/authoring/bundle/playbooks/agent-guide-authoring/`,
    `packages/devkit/src/devkit_agt/bundles/authoring/bundle/playbooks/skill-authoring/references/scripts.md`,
    `packages/devkit-catalog/src/devkit_catalog/`, `packages/devkit-starter/src/devkit_starter/bundle/`
  - _Requirements: AC-01, AC-02_

## Phase 2: Integration checks

- [ ] **Task 2.1**: Sync projections and run the checks
  - **_Boundary**: `.devkit/installation.json`
  - _Requirements: AC-03_
  - **Verification**: `uv run devkit sync && just test-affected && just lint-check`
