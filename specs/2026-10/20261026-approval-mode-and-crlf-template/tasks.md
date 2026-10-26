---
id: TASKS-approval-mode-and-crlf-template
spec: SPEC-approval-mode-and-crlf-template
plan: PLAN-approval-mode-and-crlf-template
---

# Task Breakdown: `SPEC-approval-mode-and-crlf-template` Approval refusal mode, completion report wording and CRLF-preserving config template

## Phase 1: Implementation

- [x] **Task 1**: Approval refusal modes, red then green, with the error table
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py`, `packages/devkit-spec/tests/integration/features/delivery/test_approval_error_modes.py`, `docs/capabilities/delivery/CAP-DLV-proposal-incubation.md`, `specs/2026-10/20261026-handoff-modes-and-template-report/feedback/approval-refusals-emit-maintenance.md`
  - _Requirements: AC-01, AC-02, AC-03, AC-04_
  - **Verification**: `just test devkit-spec packages/devkit-spec/tests/integration/features/delivery/test_approval_error_modes.py`; `rg -n "PROPOSAL_APPROVAL_" docs/capabilities/delivery/CAP-DLV-proposal-incubation.md` shows a mode in each row

- [x] **Task 2**: Completion reference without report wording, synchronized
  - **_Boundary**: `packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja`, `packages/devkit-spec/tests/integration/bundles/spec/test_proposal_review_report_guidance.py`, `.devkit/installation.json` (the tracked output `uv run devkit sync` writes), `specs/2026-10/20261026-handoff-modes-and-template-report/feedback/completion-guidance-report-uri.md`
  - _Requirements: AC-05_
  - **Verification**: `rg -n "report URI" packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/skills/spec/references/completion.md.jinja` prints nothing; `uv run devkit sync --check`

- [x] **Task 3**: CRLF-preserving config template, red then green
  - **_Boundary**: `packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/config.py`, `packages/devkit-dist/tests/integration/features/distribution/test_config_template.py`, `docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md`, `docs/development/reference/distribution.md`, `specs/2026-10/20261026-handoff-modes-and-template-report/feedback/config-template-rewrites-crlf-line-endings.md`
  - _Requirements: AC-06, AC-07_
  - **Verification**: `just test devkit-dist packages/devkit-dist/tests/integration/features/distribution/test_config_template.py`
