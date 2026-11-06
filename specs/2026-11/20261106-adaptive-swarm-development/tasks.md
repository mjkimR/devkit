---
id: TASKS-adaptive-swarm-development
spec: SPEC-adaptive-swarm-development
plan: PLAN-adaptive-swarm-development
---

# Task Breakdown: Reusable Adaptive Subagents

- [ ] **Task 1**: Ship reusable archetypes, presets and bounded orchestration with real projection/consumer tests and semantic evidence.
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/adaptive_dev/`, `packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py`, `packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/`, `specs/2026-11/20261106-adaptive-swarm-development/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10_
  - **Verification**: bundle validate/plan, catalog integration, installed-consumer E2E, bounded semantic exercises, lint, types and affected checks.

- [ ] **Task 2**: Restate retained behavior and promoted decisions in Living Spec with traceability.
  - **_Boundary**: `docs/capabilities/delivery/CAP-DLV-adaptive-development.md`, `docs/usecases/delivery/UC-advance-an-idea.md`, `docs/architecture/ARCH-05-2-components.md`, `docs/decisions/2026-11/20261102-adaptive-development-and-research.md`, `docs/decisions/2026-11/20261106-skill-local-swarm-roles.md`, `docs/decisions/2026-11/20261106-worktree-isolated-parallel-workers.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09, AC-10_
  - **Verification**: rules check and independent reconcile verification against actual assets and evidence.
