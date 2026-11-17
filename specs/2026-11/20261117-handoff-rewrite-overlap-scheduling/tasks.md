---
id: TASKS-handoff-rewrite-overlap-scheduling
spec: SPEC-handoff-rewrite-overlap-scheduling
plan: PLAN-handoff-rewrite-overlap-scheduling
---

# Task Breakdown: `SPEC-handoff-rewrite-overlap-scheduling` Handoff rewrites as integration evidence in scope scheduling

- [x] **Task 1**: Amend the spec-orchestrate scheduling bullet and mirror it in the Living Spec
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec-orchestrate/`, `docs/capabilities/harness/CAP-HARN-agent-guidance.md`, `specs/2026-11/feedback/20261116-handoff-reference-overlap-serializes-workers.md`, `.devkit/installation.json` (sync output)
  - _Requirements: AC-01, AC-02, AC-03_
  - **Verification**: `uv run devkit generated check`, `uv run devkit rules check --ci --base main`, `just test-affected --base main`
- [x] **Task 2**: Widen the `ProposalReferencesRewrittenNotice` docstring to the alias rewrites and resolve its feedback
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/base/errors.py` (scope extension: Host-authorized, FB-refs-rewritten-notice-docstring docstring drift after SPEC-handoff-sibling-alias-rewrite), `specs/2026-11/20261117-handoff-sibling-alias-rewrite/feedback/refs-rewritten-notice-docstring.md` (scope extension: Host-authorized, resolves FB-refs-rewritten-notice-docstring)
  - _Requirements: AC-04_
  - **Verification**: `just lint-check`, `uv run pyright packages/devkit-spec/src/devkit_spec/base/errors.py`
