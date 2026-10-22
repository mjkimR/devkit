---
id: TASKS-writing-guidance-layers
spec: SPEC-writing-guidance-layers
plan: PLAN-writing-guidance-layers
---

# Task Breakdown: `SPEC-writing-guidance-layers` Layered writing guidance for documents and agent assets

## Phase 1: Spec bundle guidance

- [x] **Task 1.1**: Common baseline `document-writing` and deduplicated `contract-authoring` and `living-spec-writing`
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/document-writing.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/contract-authoring.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/living-spec-writing.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml`
  - _Requirements: AC-01, AC-02_
- [x] **Task 1.2**: Per-type guides and template changes, PADR Confirmation section
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/decision-writing.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/capability-writing.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/story-writing.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/architecture-writing.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/templates/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml`,
    `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/scaffold.py`
  - _Requirements: AC-01, AC-03, AC-04, AC-05_
- [x] **Task 1.3**: Spec bundle writing-guidance tests
  - **_Boundary**: `packages/devkit-spec/tests/integration/bundles/spec/test_writing_guidance.py`,
    `packages/devkit-spec/tests/integration/features/proposals/`
  - _Requirements: AC-01, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec tests/integration/features/proposals`

## Phase 2: Authoring bundle

- [x] **Task 2.1**: `agent-asset-writing` instruction, procedure-only `skill-authoring` playbook, bundle test
  - **_Boundary**: `packages/devkit/src/devkit_agt/bundles/authoring/bundle/`,
    `packages/devkit/tests/integration/bundles/authoring/test_bundle.py`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `just test devkit tests/integration/bundles/authoring`

## Phase 3: Pilot

- [ ] **Task 3.1**: Rewrite `spec-plan` under `agent-asset-writing` with the constraint mapping table
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-plan/SKILL.md`,
    `specs/2026-10/20261022-writing-guidance-layers/pilot.md`
  - _Requirements: AC-08_
- [ ] **Task 3.2**: Run the three dry-run scenarios against the old and new text and record the results
  - **_Boundary**: `specs/2026-10/20261022-writing-guidance-layers/pilot.md`
  - _Requirements: AC-09_

## Phase 4: Integration checks

- [ ] **Task 4.1**: Sync projections, ADR and reference documents, run the checks
  - **_Boundary**: `.devkit/`, `.claude/`, `.agents/`, `AGENTS.md`, `CLAUDE.md`,
    `docs/decisions/2026-10/20261022-layered-writing-guidance.md`, `docs/development/reference/rules.md`,
    `docs/development/reference/distribution.md`, `guides/install/bundle-recommendations.md`,
    `packages/devkit/README.md`
  - _Requirements: AC-10_
  - **Verification**: `uv run devkit sync && just rules-check && just test-affected`
