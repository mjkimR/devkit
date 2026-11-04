---
id: TASKS-role-authoring-guidance
spec: SPEC-role-authoring-guidance
plan: PLAN-role-authoring-guidance
---

# Task Breakdown

- [ ] **Task 1**: Add shared role-placement guidance and conditional playbook routing
  - **_Boundary**: `packages/devkit/src/devkit_agt/bundles/authoring/bundle/instructions/agent-asset-writing.md`, `packages/devkit/src/devkit_agt/bundles/authoring/bundle/playbooks/skill-authoring/SKILL.md`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/decisions/2026-11/20261104-shared-role-authoring.md`, `specs/2026-11/20261104-research-local-roles/feedback/skill-local-role-authoring.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test-affected`, authoring hygiene, synchronization and independent review.
