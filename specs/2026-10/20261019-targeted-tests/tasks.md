---
id: TASKS-targeted-tests
spec: SPEC-targeted-tests
plan: PLAN-targeted-tests
---

# Task Breakdown: `SPEC-targeted-tests` Targeted and affected test runs

- [x] **Task 1**: Area and path selectors for `just test` and `just test-cov` on a single module, with script tests
  - **_Boundary**: `scripts/module.sh`, `justfile`, `packages/devkit/tests/test_module_script.py`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05_
  - **Verification**: `just test devkit packages/devkit/tests/test_module_script.py`
- [x] **Task 2**: Change collection, dependency scan and selection in `scripts/affected_tests.py`, with unit tests
  against the real tree and a temporary repository
  - **_Boundary**: `scripts/affected_tests.py`, `packages/devkit/tests/test_affected_tests.py`
  - _Requirements: AC-06, AC-07, AC-08, AC-09, AC-10, AC-11, AC-14_
  - **Verification**: `just test devkit packages/devkit/tests/test_affected_tests.py`
- [x] **Task 3**: `just test-affected` command: output, `--list`, pytest pass-through and hand-off to `module.sh`
  - **_Boundary**: `scripts/affected_tests.py`, `justfile`, `packages/devkit/tests/test_affected_tests.py`
  - _Requirements: AC-12, AC-13, AC-14_
  - **Verification**: `just test-affected --list`
- [x] **Task 4**: Agent guidance and development docs for targeted runs and the single full run before integration
  - **_Boundary**: `AGENTS.md`, `README.md`, `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-review/SKILL.md`,
    `packages/devkit-spec/src/devkit_spec/bundle/skills/spec-plan/SKILL.md`, `.claude/skills/`, `.agents/skills/`,
    `.devkit/installation.json`, `docs/development/ci-cd.md`, `docs/development/setup.md`,
    `docs/development/workflow.md`
  - _Requirements: AC-15_
  - **Verification**: `just rules-check`
