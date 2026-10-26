---
id: TASKS-review-refactor
spec: SPEC-review-refactor
plan: PLAN-review-refactor
---

# Task Breakdown: `SPEC-review-refactor` Maintenance review and refactoring playbook

## Phase 1: Playbook and packaging

- [x] **Task 1.1**: Playbook asset, manifest presets and bundle tests
  - **_Boundary**: `packages/devkit-catalog/src/devkit_catalog/maintenance/`, `packages/devkit-catalog/tests/integration/bundles/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit-catalog`; `uv run devkit rules check --phase hygiene packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor`
- [x] **Task 1.2**: Spec-review checklist mapping the agreed design to playbook sections
  - **_Boundary**: `specs/2026-10/20261026-review-refactor/materials/checklist.md`
  - _Requirements: AC-05_
  - **Verification**: every row names a file and section that exists in the playbook

## Phase 2: Documentation

- [x] **Task 2.1**: Capability, use case, content-packages entry, README and install recommendation
  - **_Boundary**: `docs/capabilities/delivery/`, `docs/capabilities/distribution/`, `docs/usecases/governance/`, `packages/devkit-catalog/README.md`, `guides/install/`
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit rules check`

## Phase 3: Manual evidence

- [x] **Task 3.1**: Real read-only sweep stopped at its decision round, with findings as feedback follow-ups
  - **_Boundary**: `specs/2026-10/20261026-review-refactor/materials/sweep.md`, `specs/2026-10/20261026-review-refactor/feedback/`
  - _Requirements: AC-07_
  - **Verification**: the record names intake, coverage, findings, gaps and a pending decision round; `git status` shows no source change
- [x] **Task 3.2**: Disposable fixture exercise of direct-mode application
  - **_Boundary**: `scratch/`, `specs/2026-10/20261026-review-refactor/materials/`
  - **Note**: `scratch/` is ignored; the fixture's removal was denied and is left for the Host
  - _Requirements: AC-08_
  - **Verification**: the record holds three change records with patches, fixture commits and before-and-after output
