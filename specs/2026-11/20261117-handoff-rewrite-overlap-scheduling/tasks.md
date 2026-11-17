---
id: TASKS-handoff-rewrite-overlap-scheduling
spec: SPEC-handoff-rewrite-overlap-scheduling
plan: PLAN-handoff-rewrite-overlap-scheduling
---

# Task Breakdown: `SPEC-handoff-rewrite-overlap-scheduling` Handoff rewrites as integration evidence in scope scheduling

- [ ] **Task 1**: Amend the spec-orchestrate scheduling bullet and mirror it in the Living Spec
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `specs/2026-11/feedback/20261116-handoff-reference-overlap-serializes-workers.md`
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run devkit generated check`, `uv run devkit rules check --ci --base main`, `just test-affected --base main`
