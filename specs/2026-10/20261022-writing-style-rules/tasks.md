---
id: TASKS-writing-style-rules
spec: SPEC-writing-style-rules
plan: PLAN-writing-style-rules
---

# Task Breakdown: `SPEC-writing-style-rules` Writing style rules and layout-free guidance tests

- [x] **Task 1**: `RULE-agent-asset-wording` with its guide and tests
  - **_Boundary**: `packages/devkit/src/devkit_agt/bundles/authoring/bundle/rules/agent_asset_wording/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit packages/devkit/src/devkit_agt/bundles/authoring/bundle/rules/agent_asset_wording`
- [x] **Task 2**: Ship the rule in the `skill-authoring` preset and document it
  - **_Boundary**: `packages/devkit/src/devkit_agt/bundles/authoring/bundle/bundle.toml`,
    `packages/devkit/src/devkit_agt/bundles/authoring/bundle/instructions/agent-asset-writing.md`,
    `packages/devkit/src/devkit_agt/bundles/authoring/bundle/playbooks/skill-authoring/SKILL.md`,
    `packages/devkit/tests/integration/bundles/authoring/test_bundle.py`, `docs/development/reference/rules.md`,
    `docs/architecture/ARCH-08-2-resource-taxonomy.md`, `.devkit/`, `.claude/`, `.agents/`, `AGENTS.md`
  - _Requirements: AC-06_
  - **Verification**: `uv run devkit sync && uv run devkit rules check --phase hygiene`
- [x] **Task 3**: Shared bundle text reader for the spec bundle guidance tests
  - **_Boundary**: `packages/devkit-spec/tests/support/spec_support/bundle_text.py`,
    `packages/devkit-spec/tests/integration/bundles/spec/`
  - _Requirements: AC-07_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec`
