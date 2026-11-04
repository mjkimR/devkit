---
id: TASKS-namespace-roadmap
spec: SPEC-namespace-roadmap
plan: PLAN-namespace-roadmap
---

# Task Breakdown: `SPEC-namespace-roadmap` Per-namespace milestones under the namespace docs root

## Phase 1: Rules and kind table (devkit-docs)

- [ ] **Task 1.1**: Make `RULE-id-convention` validate milestone placement through `living_path` for every docs root,
  name both roots in its remediations, and add the namespace fixtures
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/governance/usecases/id_convention.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/id_convention/tests/test_rule.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/id_convention/guide.md`
  - _Requirements: AC-01, AC-02, AC-08_
  - **Verification**: `just test devkit-docs packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/id_convention/tests`
- [ ] **Task 1.2**: Set the `MILESTONE` kind row to `FormatScope.EVERY_ROOT`, guard the milestone checks of
  `RULE-spec-format` with `living_path`, and add the namespace fixtures
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/features/documents/models/kinds.py`,
    `packages/devkit-docs/src/devkit_docs/features/governance/usecases/spec_format.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/spec_format/tests/test_rule.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/spec_format/guide.md`
  - _Requirements: AC-03, AC-08_
  - **Verification**: `just test devkit-docs packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/spec_format/tests`
- [ ] **Task 1.3**: Pin `devkit docs list milestone` selection from a package directory and with `--all-namespaces`,
  and the monorepo fixture with a cross-namespace `depends_on` edge passing the three rules
  - **_Boundary**: `packages/devkit-docs/tests/integration/features/documents/test_namespaces.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests/test_rule.py`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/id_convention/tests/test_rule.py`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `just test devkit-docs tests/integration/features/documents/test_namespaces.py packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/document_reference/tests packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/rules/id_convention/tests`
- [ ] **Task 1.4**: Generalize the `docs` bundle's milestone template placement sentence and the seeded roadmap
  sentence to the milestone's roadmap root
  - **_Boundary**: `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/milestone.md`,
    `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/seed/docs/architecture/ARCH-01-introduction-and-goals.md`
  - _Requirements: AC-08_
  - **Verification**: `rg -n "docs/roadmap" packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/templates/milestone.md packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/seed/docs/architecture/ARCH-01-introduction-and-goals.md` shows the two-root wording

## Phase 2: Proposal membership and guidance (devkit-spec)

- [ ] **Task 2.1**: Accept `--milestone` naming a milestone at the global or a namespace roadmap root, with the
  two-root error message and fix, and the namespace fixtures
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/roadmap.py`,
    `packages/devkit-spec/tests/integration/features/proposals/test_roadmap.py`
  - _Requirements: AC-04, AC-05_
  - **Verification**: `just test devkit-spec tests/integration/features/proposals/test_roadmap.py`
- [ ] **Task 2.2**: Name the milestone's roadmap root in the `spec` skill references and update the guidance test
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/backlog.md.jinja`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/roadmap-catalog.md`,
    `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/milestone-completion.md`,
    `packages/devkit-spec/tests/integration/bundles/spec/test_milestone_archive_guidance.py`
  - _Requirements: AC-08_
  - **Verification**: `just test devkit-spec tests/integration/bundles/spec/test_milestone_archive_guidance.py`

## Phase 3: Regenerated copies and full checks

- [ ] **Task 3.1**: Regenerate the deployed copies of the edited bundle text and run the affected suite, lint and
  type checks
  - **_Boundary**: `.devkit/managed/`, `.devkit/installation.json`, `.claude/`
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07, AC-08_
  - **Verification**: `uv run devkit sync`; `uv run devkit generated check`; `just test-affected`; `just lint-check devkit-docs devkit-spec`; `just check devkit-docs devkit-spec`
