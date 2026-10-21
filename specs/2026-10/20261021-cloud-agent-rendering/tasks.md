---
id: TASKS-cloud-agent-rendering
spec: SPEC-cloud-agent-rendering
plan: PLAN-cloud-agent-rendering
---

# Task Breakdown: `SPEC-cloud-agent-rendering`

- [x] **Task 1**: Execution-aware canonical planning, typed receipt and personal/context evidence with regression tests.
  - **_Boundary**: packages/devkit-dist/src/devkit/distribution/, packages/devkit-dist/src/devkit/core/receipt.py, packages/devkit-dist/tests/
  - _Requirements: AC-02, AC-04_
- [x] **Task 2**: Constitution and common subagent templates with validation and projection tests.
  - **_Boundary**: packages/devkit-dist/src/devkit/distribution/, packages/devkit-dist/tests/
  - _Requirements: AC-03_
- [x] **Task 3**: Maintained guidance templates, complete corpus audit, packaging tests and installation guidance.
  - **_Boundary**: packages/devkit-spec/src/devkit_spec/bundle/, packages/devkit-spec/tests/, packages/devkit/src/devkit/rules/rules/markdown_link/rule.py, packages/devkit/src/devkit/rules/rules/markdown_link/tests/test_rule.py, packages/devkit/src/devkit/rules/rules/markdown_link/guide.md, packages/devkit-dist/src/devkit/distribution/guide/, packages/devkit-dist/tests/, guides/INSTALL_GUIDE.md, guides/install/new-repository.md, guides/install/existing-repository.md, guides/install/mcp.md
  - _Requirements: AC-01, AC-05_
