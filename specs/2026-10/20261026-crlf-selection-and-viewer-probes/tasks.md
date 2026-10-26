---
id: TASKS-crlf-selection-and-viewer-probes
spec: SPEC-crlf-selection-and-viewer-probes
plan: PLAN-crlf-selection-and-viewer-probes
---

# Task Breakdown: `SPEC-crlf-selection-and-viewer-probes` CRLF-preserving selection edits and viewer probe test runs

## Phase 1: Implementation

- [x] **Task 1**: CRLF-preserving selection edits, red then green
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config.py`, `packages/devkit-dist/tests/integration/features/distribution/test_config_template.py`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `specs/2026-10/20261026-approval-mode-and-crlf-template/feedback/selection-edits-rewrite-crlf-line-endings.md`
  - _Requirements: AC-01, AC-02_
  - **Verification**: `just test devkit-dist packages/devkit-dist/tests/integration/features/distribution/test_config_template.py`

- [x] **Task 2**: Viewer probe action and its guidance, synchronized
  - **_Boundary**: `scripts/viewer.sh`, `docs/development/reference/viewer.md`, `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/subagents/code-reviewer.md`, `packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`, `.devkit/installation.json` (the tracked output `uv run devkit sync` writes), `specs/2026-10/20261026-viewer-handbook-first-knowledge/feedback/viewer-review-probes-outside-vitest-include.md`
  - _Requirements: AC-03, AC-04, AC-05_
  - **Verification**: `just viewer probe <worktree>/scratch/probe-check-02` exits 0; `just test devkit-spec packages/devkit-spec/tests/integration/bundles/spec/test_delegation_sandbox_guidance.py`; `uv run devkit sync --check`
