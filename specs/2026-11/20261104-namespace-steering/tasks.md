---
id: TASKS-namespace-steering
spec: SPEC-namespace-steering
plan: PLAN-namespace-steering
---

# Task Breakdown: `SPEC-namespace-steering` Namespace steering documents checked and listed beside the global ones

## Phase 1: Rules (devkit-docs)

- [ ] **Task 1.1**: `RULE-steering-documents` checks every registered namespace steering directory per directory,
  with glossary findings, and its guide names both directories
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/usecases/steering_documents.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/steering_documents/guide.md`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/steering_documents/tests/test_rule.py`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run devkit sync && just rules-test RULE-steering-documents`
- [ ] **Task 1.2**: `RULE-document-reference` resolves and fixes the IDs cited in namespace steering files
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/usecases/document_reference.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/guide.md`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`
  - _Requirements: AC-04_
  - **Verification**: `uv run devkit sync && just rules-test RULE-document-reference`

## Phase 2: Context assembly (devkit-dist)

- [ ] **Task 2.1**: Provider loading, merged listing, `documents_elsewhere`, `notices` and `--for`
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/context_documents.py`,
    `packages/devkit-dist/src/devkit_dist/features/distribution/models/results.py`,
    `packages/devkit-dist/src/devkit_dist/features/distribution/models/errors.py`,
    `packages/devkit-dist/src/devkit_dist/features/distribution/usecases/context.py`,
    `packages/devkit-dist/src/devkit_dist/features/distribution/cli/context.py`,
    `packages/devkit-dist/tests/integration/features/distribution/test_context_documents.py`,
    `packages/devkit-dist/tests/integration/features/distribution/test_context.py`
  - _Requirements: AC-05, AC-06, AC-07_
  - **Verification**: `just test devkit-dist tests/integration/features/distribution/test_context_documents.py tests/integration/features/distribution/test_context.py && just test-dist`

## Phase 3: Provider and guidance (devkit-docs)

- [ ] **Task 3.1**: The `devkit.context_documents` provider of `devkit-docs` and its registration, with provider and
  monorepo end-to-end tests
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/documents/services/context_documents.py`,
    `packages/devkit-docs/pyproject.toml`, `packages/devkit-docs/tests/integration/test_context_documents.py`,
    `packages/devkit-docs/README.md`
  - _Requirements: AC-08, AC-09_
  - **Verification**: `uv sync && just test devkit-docs tests/integration/test_context_documents.py`
- [ ] **Task 3.2**: The `docs` bundle guidance names the namespace directory, `documents_elsewhere` and `--for`
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/AGENTS.md`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md`,
    `packages/devkit-docs/tests/integration/bundles/`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_steering_guidance.py`
  - _Requirements: AC-10_
  - **Verification**: `just test devkit-docs tests/integration/bundles && just test devkit-spec tests/integration/bundles/spec/test_steering_guidance.py`
