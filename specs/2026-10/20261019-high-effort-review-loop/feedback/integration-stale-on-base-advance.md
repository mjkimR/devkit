---
id: FB-integration-stale-on-base-advance
title: Local integration is refused whenever the base advances during approval
scope: repo
kind: change-request
category: redundant-step
target: packages/devkit/src/devkit/integration/service.py
skill: spec-integrate
agent: claude-code
origin: user
severity: workaround
recurring: false
status: promoted
created_at: 2026-10-19
---

# [FB-integration-stale-on-base-advance] Local integration is refused whenever the base advances during approval

## 2. Suggestion / Change Request (suggestion, change-request)

- **Current Procedure**: `integration_integrate` binds the approval to the source and target SHAs and to a digest of
  the base checkout's `.devkit/config.toml` and `.devkit/installation.json`, and merges `ff-only`. Any commit that
  lands on the base while the confirmation is open blocks the run with `INTEGRATION_REQUEST_STALE` (a guardrail);
  the only recovery is to integrate the base into the branch again and ask for a new confirmation. With several
  activities merging into one base, this repeats.
- **Proposed Procedure**: tolerate a base advance that does not touch the approved scope: after confirmation,
  integrate the new base into the source (or merge with a merge commit) when it applies cleanly and the readiness
  check still passes on the result, and refuse only on a conflict, a changed policy file in the source's own diff,
  or failed readiness. Compare the policy digest of the merged result rather than the base's receipt alone.
- **Expected Benefit**: one confirmation per integration, independent of unrelated activities landing on the base.
- **Cost & Risk**: the approved `(source_sha, target_sha)` binding loosens to "source plus whatever the base gained";
  a base commit that changes policy or managed assets would then be merged without the user seeing it in the
  confirmation. Limiting tolerance to commits outside `.devkit/` keeps that case refused.
- **Attempted**: one confirmation for `plan-high-effort-review-loop` was accepted and then refused at preflight;
  nothing was merged.

## Evidence

- `integration_integrate` result: `status: blocked`, `INTEGRATION_REQUEST_STALE` "effective policy or installed
  receipt changed outside the approved merge", `ui_action: accept`, every step `not_run`; request target SHA
  `58dae19`, observed target SHA `fa6aa90`.
- `fa6aa90` (another activity, landed during the confirmation) changed `.devkit/installation.json` and four bundle
  files unrelated to this proposal.
- `service.py` `_validate`: compares a digest of `.devkit/config.toml` and `.devkit/installation.json` with the
  request's and raises `StaleRequestError` on any difference; the request's `merge_method` is fixed to `ff-only`
  (`models.py`).

- **Disposition**: PROP-integration-follow-ups: tolerating base advances during approval (E1-E6)
