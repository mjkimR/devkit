---
id: TASKS-milestone-non-binding
spec: SPEC-milestone-non-binding
plan: PLAN-milestone-non-binding
---

# Task Breakdown: `SPEC-milestone-non-binding`

- [x] **Task 1**: State the non-binding milestone boundary in the template, the Backlog reference and the capability, then synchronize.
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/templates/milestone.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/backlog.md.jinja`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `.devkit/`, `.claude/skills/spec/references/backlog.md`, `.agents/skills/spec/references/backlog.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run devkit sync --check`, `just rules-check`, `just test-affected`.
