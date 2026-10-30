---
id: FB-handoff-refusals-emit-maintenance
title: Composed handoff refusals the caller can fix emit MAINTENANCE
scope: repo
kind: change-request
category: tool-error
target: packages/devkit-spec/src/devkit_spec/base/errors.py (HandoffNotReadyError, HandoffReplyError)
origin: agent
severity: workaround
recurring: false
status: resolved
created_at: 2026-10-26
---

# [FB-handoff-refusals-emit-maintenance] Composed handoff refusals the caller can fix emit MAINTENANCE

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `HandoffNotReadyError` (`SPEC_HANDOFF_NOT_READY`) and `HandoffReplyError`
  (`SPEC_HANDOFF_REPLY_INVALID`) inherit `SpecError` and set only `code` and `fix`, so they derive mode
  `MAINTENANCE` ("a codebase defect or tool failure occurred ... repairing the code/tool is a separate task").
  They refuse on prerequisites and input the caller controls: an uncommitted base checkout, an unaccepted proposal,
  an incomplete Planning workflow, a missing or invalid `--effort`. `CAP-DLV-proposal-planning` §4.12 documents
  them as `BLOCKED` and `INPUT_ERROR`.
- **Proposed Procedure**: give `HandoffReplyError` `input_error = True` (`INPUT_ERROR`), and give
  `HandoffNotReadyError` the mode its prerequisites need (the documented `BLOCKED`, or `INTERACTION` with
  `actor = Actor.USER` when the user resolves the prerequisite), then pin the modes in tests. Decide at the same time
  whether `HandoffStaleError` (`MAINTENANCE`, documented so) should stay a tool failure when only the base moved.
- **Expected Benefit**: an agent that hits an unmet handoff prerequisite resolves it or asks the user instead of
  reporting a tool defect and stopping.
- **Cost & Risk**: two class attributes and their tests; the rendered `[ACTION]` of these codes changes.
- **Attempted**: not changed: `SPEC-feedback-guidance-and-scope` (item 4) settles the documented-versus-emitted
  mismatch of `FB-handoff-error-modes-documented-differently` without redesigning modes, so the §4.12 rows keep the
  documented modes and this feedback carries the code change.

## Diagnostic Details

- **Reproduction**: `uv run python -c "from devkit_spec.base.errors import HandoffNotReadyError as E; print(E('x').to_dict()['advisory']['mode'])"`.
- **Expected / Actual**: `BLOCKED` (and `INPUT_ERROR` for `HandoffReplyError`) / `MAINTENANCE` for both.
- **Versions**: worktree head of `dev-feedback-guidance-and-scope`.
- **Conditions**: every raise in `features/delivery/usecases/native_handoff.py`.
- **Workarounds Attempted**: not applicable.
- **Related Assets**: `CAP-DLV-proposal-planning`, `CAP-ADV-agent-advisory-protocol`.

## Evidence

```text
SPEC_HANDOFF_NOT_READY MAINTENANCE
SPEC_HANDOFF_REPLY_INVALID MAINTENANCE
SPEC_HANDOFF_STALE MAINTENANCE
native_handoff.py: HandoffNotReadyError("the base checkout has uncommitted changes; commit or resolve them before review")
native_handoff.py: HandoffReplyError("choose low, medium or high Development effort")
```

## Related stale fix text

`HandoffNotReadyError.fix` and the `SPEC_HANDOFF_NOT_READY` row of `CAP-DLV-proposal-planning` still say to rerun
"with the current report URI", although acceptance and handoff no longer take or need a published report. Fix the
text together with the mode change.

## Disposition

Resolved by `SPEC-handoff-modes-and-template-report` (decision 1): `HandoffNotReadyError` sets `guardrail = True` and renders `BLOCKED`, `HandoffReplyError` sets `input_error = True` and renders `INPUT_ERROR`, and `HandoffStaleError` stays `MAINTENANCE`, as its `CAP-DLV-proposal-planning` row documents. The fixes of `SPEC_HANDOFF_NOT_READY`, `SPEC_HANDOFF_STALE`, `PROPOSAL_APPROVAL_STALE` and `PROPOSAL_APPROVAL_NOT_READY` and the `SPEC_HANDOFF_NOT_READY` row no longer ask for a report. Verified by `test_handoff_error_modes.py` (red on the base) and a composed CLI test that renders `[ACTION] BLOCKED` for an untracked base file.
