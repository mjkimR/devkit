---
id: FB-approval-refusals-emit-maintenance
title: Proposal acceptance refusals the caller can fix emit MAINTENANCE
scope: repo
kind: change-request
category: tool-error
target: packages/devkit-spec/src/devkit_spec/features/delivery/usecases/native_plan_accept.py (ProposalApprovalNotReadyError)
origin: agent
severity: noise
recurring: false
status: open
created_at: 2026-10-26
---

# [FB-approval-refusals-emit-maintenance] Proposal acceptance refusals the caller can fix emit MAINTENANCE

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `ProposalApprovalNotReadyError` (`PROPOSAL_APPROVAL_NOT_READY`) inherits `SpecError` with
  only `code` and `fix`, so it derives `MAINTENANCE` ("a codebase defect or tool failure occurred"), although it
  refuses on Planning or worktree prerequisites the caller resolves. `CAP-DLV-proposal-incubation` documents no mode
  for the `PROPOSAL_APPROVAL_*` codes.
- **Proposed Procedure**: give it the mode its prerequisites need (`BLOCKED` with `guardrail = True`, as
  `SPEC_HANDOFF_NOT_READY` now has), document the modes of the `PROPOSAL_APPROVAL_*` rows and pin them in tests.
- **Expected Benefit**: the same directive for the same kind of refusal across `accept` and `handoff --effort`.
- **Cost & Risk**: one class attribute, a table column and tests; the rendered `[ACTION]` changes.
- **Attempted**: `SPEC-handoff-modes-and-template-report` changed only the fix text of these errors; their modes
  were outside decision 1.

## Diagnostic Details

- **Reproduction**: `uv run python -c "from devkit_spec.features.delivery.usecases.native_plan_accept import ProposalApprovalNotReadyError as E; print(E('x').to_dict()['advisory']['mode'])"`.
- **Expected / Actual**: `BLOCKED` / `MAINTENANCE`.
- **Versions**: `dev-handoff-modes-and-template-report`.
- **Conditions**: every refusal of `devkit spec proposal accept` on an unmet prerequisite.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `CAP-DLV-proposal-incubation`, `FB-handoff-refusals-emit-maintenance`.
