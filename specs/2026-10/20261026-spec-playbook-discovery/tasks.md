---
id: TASKS-spec-playbook-discovery
spec: SPEC-spec-playbook-discovery
plan: PLAN-spec-playbook-discovery
---

# Task Breakdown: `SPEC-spec-playbook-discovery` Task-aware playbook discovery through spec

## Phase 1: Spec intake

- [ ] **Task 1.1**: `spec` skill intake step, `references/playbooks.md`, guidance pointer clause and spec-side
  wording, with text-contract tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/guidance/spec-pointer.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/bundle.toml`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/seed/docs/README.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-next/SKILL.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_playbook_discovery_guidance.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-08_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec`

- [ ] **Task 1.2**: Playbook entry conditions "invoked or confirmed" in the `spec` and `maintenance` playbooks and
  the catalog README, with tests
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/`,
    `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/`, `packages/devkit-catalog/README.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_playbook_discovery_guidance.py`
  - _Requirements: AC-07_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec`

## Phase 2: Generic entry

- [ ] **Task 2.1**: Spec-neutral generated `devkit-playbook` skill, guidance line, CLI help and `devkit`
  constitution, with tests
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/playbook_skill.py`,
    `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/guidance_block.py`,
    `packages/devkit-dist/src/devkit_dist/features/distribution/cli/playbooks.py`,
    `packages/devkit-dist/src/devkit_dist/bundles/devkit/bundle/AGENTS.md`,
    `packages/devkit-dist/tests/integration/features/distribution/`, `AGENTS.md`, `.devkit/installation.json`
  - _Requirements: AC-06_
  - **Verification**: `just test devkit-dist packages/devkit-dist/tests/integration/features/distribution` and
    `just test-dist`

## Phase 3: Manual evidence

- [ ] **Task 3.1**: Recorded manual intake run with `maintenance` synchronized in a scratch consumer
  - **_Boundary**: `specs/2026-10/20261026-spec-playbook-discovery/materials/manual-run.md`
  - _Requirements: AC-09_
  - **Verification**: the run's table shows 0 offers for the 16 ordinary intents, one named offer per positive
    control and at most one offer line per intake
