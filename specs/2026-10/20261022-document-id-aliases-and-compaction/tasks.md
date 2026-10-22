---
id: TASKS-document-id-aliases-and-compaction
spec: SPEC-document-id-aliases-and-compaction
plan: PLAN-document-id-aliases-and-compaction
---

# Task Breakdown: `SPEC-document-id-aliases-and-compaction` Document and Playbook ID Aliases

## Phase 1: Document aliases

- [x] **Task 1.1**: Alias parsing, shared legacy predicate and the canonical mapping of `DocumentIndex`, with unit tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/documents/, packages/devkit-spec/tests/unit/features/documents/,
    packages/devkit-spec/src/devkit_spec/features/governance/usecases/id_convention.py
  - _Requirements: AC-01, AC-02_
- [x] **Task 1.2**: `RULE-document-reference` alias identity checks, fixable alias references, exemptions, glossary,
  cycles and canonical handed-off targets, with the rule's tests and guide
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/governance/usecases/document_reference.py,
    packages/devkit-spec/src/devkit_spec/features/documents/services/dependencies.py,
    packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/rules/document_reference/
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
- [x] **Task 1.3**: Traceability, hygiene and roadmap through the canonical mapping, with tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/governance/usecases/traceability_link.py,
    packages/devkit-spec/src/devkit_spec/features/governance/usecases/hygiene.py,
    packages/devkit-spec/src/devkit_spec/features/proposals/usecases/roadmap.py, packages/devkit-spec/tests/integration/features/governance/
  - _Requirements: AC-06_
- [x] **Task 1.4**: `devkit spec resolve`, `refs`, `search` and entrypoints `--target` with aliases, with CLI tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/documents/usecases/, packages/devkit-spec/src/devkit_spec/features/documents/cli/,
    packages/devkit-spec/tests/integration/features/documents/, packages/devkit-spec/tests/integration/features/entrypoints/
  - _Requirements: AC-07_
- [x] **Task 1.5**: Handoff alias carriage, translation, rewrite and clash refusal; scaffolding alias checks, with tests
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/features/proposals/, packages/devkit-spec/tests/integration/features/proposals/
  - _Requirements: AC-08, AC-09_

## Phase 2: Playbook aliases

- [x] **Task 2.1**: Playbook alias validation, search without aliases and `playbook get` alias resolution, with tests
  - **_Boundary**: packages/devkit-dist/src/devkit_dist/features/distribution/, packages/devkit-dist/src/devkit_dist/features/search/services/index.py,
    packages/devkit-dist/tests/
  - _Requirements: AC-10, AC-11, AC-12_
- [x] **Task 2.2**: Bundled playbooks drop keyword aliases; sync the repository's projections
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/playbooks/, packages/devkit/src/devkit_agt/bundles/authoring/bundle/playbooks/,
    packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/, packages/devkit-starter/src/devkit_starter/bundle/playbooks/,
    .devkit/installation.json
  - _Requirements: AC-13_
  - **Verification**: `uv run devkit sync` then `uv run devkit status`

## Phase 3: Contracts

- [x] **Task 3.1**: Instructions and capability contracts describe aliases (document model, lookup, search, spec rules,
  proposal incubation, playbooks, search metadata, resource taxonomy, distribution reference)
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/instructions/living-spec-writing.md, docs/capabilities/documents/,
    docs/capabilities/governance/, docs/capabilities/delivery/CAP-DLV-proposal-incubation.md,
    docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md, docs/development/reference/distribution.md,
    docs/capabilities/search/CAP-SRCH-document-search.md, docs/architecture/ARCH-08-2-resource-taxonomy.md
  - _Requirements: AC-13_
  - **Verification**: `just rules-check`
