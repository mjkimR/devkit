---
id: PLAN-milestone-non-binding
spec: SPEC-milestone-non-binding
---

# Technical Plan: `SPEC-milestone-non-binding` Non-binding milestone guidance

## 1. Architecture Overview & Impact
- Target Area: spec bundle guidance assets (`packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/`) and
  `CAP-HARN-agent-guidance`. No code change.

## 2. Component Breakdown & Interface Contracts
- `templates/milestone.md`: one guidance sentence under `Goal` stating the boundary.
- `skills/spec/references/backlog.md.jinja`: one bullet in `## Milestones`.
- `CAP-HARN-agent-guidance`: one sentence in the milestone paragraph.
- Run `devkit sync` to refresh the managed and projected copies and the receipt.

## 3. Verification & Test Plan
- `uv run devkit sync --check`, `just rules-check`, `just test-affected`, `git diff --check`.
