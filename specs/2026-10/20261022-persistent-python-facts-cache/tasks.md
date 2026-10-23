---
id: TASKS-persistent-python-facts-cache
spec: SPEC-persistent-python-facts-cache
plan: PLAN-persistent-python-facts-cache
---

# Task Breakdown: `SPEC-persistent-python-facts-cache`

## Phase 1: Implementation and Verification

- [x] **Task 1**: Baseline and reproducible fresh-process measurement harness
  - **_Boundary**: docs/materials/2026-10/20261022-persistent-python-facts-cache/, packages/devkit/tests/
  - _Requirements: AC-07_
  - **Verification**: `uv run python docs/materials/2026-10/20261022-persistent-python-facts-cache/benchmark.py --output /tmp/facts-results.json`

- [x] **Task 2**: Typed descriptor, safe store, cache identity and invalidation with engine tests
  - **_Boundary**: packages/devkit/src/devkit_agt/features/rules/__init__.py, packages/devkit/src/devkit_agt/features/rules/models/file_facts.py, packages/devkit/src/devkit_agt/features/rules/repositories/workspace/cache.py, packages/devkit/src/devkit_agt/features/rules/repositories/workspace/facts.py, packages/devkit/src/devkit_agt/features/rules/repositories/workspace/file_facts.py, packages/devkit/tests/integration/features/rules/workspace/test_file_facts.py
  - _Requirements: AC-02, AC-03, AC-04, AC-06_
  - **Verification**: `just test agt rules`

- [x] **Task 3**: Architecture rule syntax records, codec and equivalence tests
  - **_Boundary**: tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `uv run devkit rules test RULE-architecture`

- [x] **Task 4**: Advisory rule syntax records, codec and equivalence tests
  - **_Boundary**: packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/rule.py, packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/index.py, packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/facts.py, packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/tests/, packages/devkit-dist/src/devkit_dist/bundles/advisory/bundle/rules/unique_code/guide.md
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `uv run devkit rules test RULE-advisory-unique-code`

- [x] **Task 5**: Usecase rule syntax records, codec and equivalence tests
  - **_Boundary**: tools/devkit-dev/src/devkit_dev/bundle/rules/usecase-boundaries/
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `uv run devkit rules test RULE-usecase-boundaries`

- [x] **Task 6**: Project writer and read-only snapshot integration with isolation tests
  - **_Boundary**: packages/devkit/src/devkit_agt/features/rules/usecases/project.py, packages/devkit/tests/integration/features/rules/engine/test_project.py
  - _Requirements: AC-04, AC-05, AC-06_
  - **Verification**: `just test-affected --base main`

- [x] **Task 7**: Performance validation and complete regression verification
  - **_Boundary**: docs/materials/2026-10/20261022-persistent-python-facts-cache/, packages/devkit/tests/
  - _Requirements: AC-01, AC-03, AC-05, AC-07_
  - **Verification**: `just test-affected --base main`
