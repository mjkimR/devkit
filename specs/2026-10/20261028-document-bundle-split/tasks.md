---
id: TASKS-document-bundle-split
spec: SPEC-document-bundle-split
plan: PLAN-document-bundle-split
---

# Task Breakdown: Document bundle split

- [ ] **Task 1**: Split bundle ownership, shared guidance and references, with distribution and guidance regression tests.
  - **_Boundary**: packages/devkit-docs/, packages/devkit-spec/, .devkit/config.toml, .devkit/installation.json, AGENTS.md, pyproject.toml, uv.lock, scripts/affected_tests.py
  - _Requirements: AC-01, AC-02, AC-03, AC-04, AC-05, AC-06_
  - **Verification**: package bundle tests; isolated built-wheel installation smoke; sync --check; affected tests; lint and types.
- [ ] **Task 2**: Reflect document ownership and installation choices in current contracts and guides.
  - **_Boundary**: guides/, docs/capabilities/documents/, docs/capabilities/delivery/, docs/capabilities/governance/, docs/architecture/, docs/decisions/, docs/steering/glossary.md
  - _Requirements: AC-02, AC-03, AC-05, AC-06_
  - **Verification**: governance checks, citation inventory and semantic comparison against AC-01 through AC-06.
