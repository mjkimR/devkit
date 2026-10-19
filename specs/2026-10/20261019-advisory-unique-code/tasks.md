---
id: TASKS-advisory-unique-code
spec: SPEC-advisory-unique-code
plan: PLAN-advisory-unique-code
---

# Task Breakdown: `SPEC-advisory-unique-code` Advisory code uniqueness rule

- [x] **Task 1**: Static module index and the rule, with its guide and tests
  - **_Boundary**: `packages/devkit/src/devkit/advisory_guide/bundle/rules/unique_code/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08, AC-09_
  - **Verification**: `uv run devkit rules test RULE-advisory-unique-code`
- [x] **Task 2**: Ship the rule in the `python` preset, open the layering and select it in this repository
  - **_Boundary**: `packages/devkit/src/devkit/advisory_guide/bundle/bundle.toml`,
    `packages/devkit/src/devkit/advisory_guide/__init__.py`, `packages/devkit/tests/test_layering.py`,
    `.devkit/config.toml`, `.devkit/installation.json`, `AGENTS.md`, `packages/devkit/README.md`
  - _Requirements: AC-10_
  - **Verification**: `uv run devkit sync && uv run devkit rules check && just test devkit`
- [x] **Task 3**: Reference documentation and the consumer-facing instruction name the rule
  - **_Boundary**: `docs/development/reference/advisory.md`, `docs/development/reference/rules.md`,
    `docs/development/reference/distribution.md`,
    `packages/devkit/src/devkit/advisory_guide/bundle/instructions/agent-advisory-python.md`
  - _Requirements: AC-10_
- [x] **Task 4**: Review fixes: function-scoped lazy imports, call-site owners never cover class-body owners, factory
  calls on external bases, annotated constants, call-line reporting and the guide's per-file settings
  - **_Boundary**: `packages/devkit/src/devkit/advisory_guide/bundle/rules/unique_code/`,
    `packages/devkit/src/devkit/advisory_guide/bundle/instructions/agent-advisory-python.md`,
    `packages/devkit/src/devkit/advisory_guide/bundle/bundle.toml`, `docs/development/reference/rules.md`
  - _Requirements: AC-03, AC-11, AC-12, AC-13_
  - **Verification**: `uv run devkit rules test RULE-advisory-unique-code`
