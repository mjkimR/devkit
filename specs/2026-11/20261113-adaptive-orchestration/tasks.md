---
id: TASKS-adaptive-orchestration
spec: SPEC-adaptive-orchestration
plan: PLAN-adaptive-orchestration
---

# Task Breakdown: `SPEC-adaptive-orchestration`

- [x] **Task 1**: Update guidance and assignment ancestry validation with regression tests.
  - **_Boundary**: `packages/devkit-adaptive/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: adaptive package tests, bundle projection/validation, lint and type checks.
- [x] **Task 2**: Reflect the changed delegation contract and retired depth refusal in current documents.
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-adaptive-development.md`, `docs/capabilities/delivery/CAP-DLV-adaptive-assignments.md`, `docs/usecases/delivery/UC-advance-an-idea.md`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `docs/development/reference/adaptive.md`, `docs/decisions/2026-11/20261113-coordinator-led-adaptive-delegation.md`, `docs/decisions/2026-11/20261106-skill-local-swarm-roles.md`, `specs/2026-11/20261113-adaptive-orchestration/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: document rules, source/contract reconciliation and affected tests.
