---
id: TASKS-terminology-authoring-guidance
spec: SPEC-terminology-authoring-guidance
plan: PLAN-terminology-authoring-guidance
---

# Task Breakdown: `SPEC-terminology-authoring-guidance` Terminology authoring guidance and a glossary that agents read

- [ ] **Task 1**: Terminology rules in the `living-spec-writing` Glossary section, with a content test
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/instructions/living-spec-writing.md,
    packages/devkit-spec/tests/test_terminology_guidance.py
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `just test devkit-spec tests/test_terminology_guidance.py`; `git diff --numstat c0a37b07e18cde2dfdac37e9620d09d73b44dd6c -- packages/devkit-spec/src/devkit_spec/bundle/instructions/living-spec-writing.md` reports at most 30 added lines
- [ ] **Task 2**: Five-column seeded glossary with the avoided generic nouns section, and the docs-skeleton test
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/seed/docs/glossary.md,
    packages/devkit-spec/tests/test_terminology_guidance.py, packages/devkit-spec/tests/test_package.py
  - _Requirements: AC-04, AC-05_
  - **Verification**: `just test devkit-spec tests/test_terminology_guidance.py tests/test_package.py`
- [ ] **Task 3**: The glossary question in `spec-sync` Step 1
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/skills/spec-sync/SKILL.md,
    packages/devkit-spec/tests/test_terminology_guidance.py
  - _Requirements: AC-06_
  - **Verification**: `just test devkit-spec tests/test_terminology_guidance.py tests/test_bundle_budgets.py`
- [ ] **Task 4**: devkit's own `docs/glossary.md` migrated to the five columns
  - **_Boundary**: docs/glossary.md
  - _Requirements: AC-07_
  - **Verification**: `rg -c "Defined in" docs/glossary.md` finds nothing; `devkit rules check docs/glossary.md` passes
