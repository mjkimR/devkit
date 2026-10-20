---
id: TASKS-shared-checkout-session-isolation
spec: SPEC-shared-checkout-session-isolation
plan: PLAN-shared-checkout-session-isolation
---

# Task Breakdown: `SPEC-shared-checkout-session-isolation` Non-blocking guidance for session branches in a shared checkout

## Phase 1: Implementation
- [x] **Task 1.1**: Clarify shared branch state and coordination in four documents
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/git-policy.md, packages/devkit-spec/src/devkit_spec/bundle/skills/spec/references/branches.md, docs/capabilities/delivery/CAP-DLV-project-policy.md, docs/capabilities/worktree/CAP-WT-task-worktrees.md
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: Review AC-01–AC-03; run targeted rules, lint/type checks and `just test-affected --base main` (AC-04).
