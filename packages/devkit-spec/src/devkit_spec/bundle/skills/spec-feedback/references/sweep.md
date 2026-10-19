# Feedback Sweep

Read this for a workflow stage sweep, a Planning run's return or a user-requested session sweep. The recording procedure of the `spec-feedback` skill (section 2) applies to every observation; promotion, dismissal and forwarding stay in a separate feedback-hygiene session. Capture never changes status;
resolution of explicitly linked source feedback follows the `spec` completion procedure independently of this sweep.

## Entry

Only an explicit user message requesting a session sweep selects the user branch; an agent-chosen invocation of `/spec-feedback` stays autonomous.

- **User-requested session sweep** (collect session observations, a retrospective): cover the whole session whatever the capture, coverage or stage policy says, and write no envelope, even when a spec bundle exists. A request to record one named observation follows the recording procedure instead.
- **Workflow stage**: `devkit workflow next --unit <dir>` names `collect-feedback` (after `living-spec-draft` in Development, after `spike` in Planning); its exit check is `envelope-check-pass(feedback swept)`. Development sweeps once per spec bundle. Zero observations passes.

Policy (`devkit spec policy`) for an autonomous stage sweep:

- Stage switched off (`[SKIPPED: collect-feedback ...]`): no sweep and no envelope; report the stage as skipped. Observed capture during the work stays on.
- `capture=requested-only`: record no observations; write the feedback envelope with `--check "swept=PASS skipped=capture.requested-only"` and a summary of the policy skip, and report it as skipped. A `session` task reports the skip without an envelope.

## Procedure

1. **Collect**: scan this session and `git diff` for unrecorded observations in the ownership scopes of the skill's section 1 (`upstream` only under `coverage=repo-and-upstream` or on request). The user never supplies ownership or destination.
2. **Deduplicate**: `devkit spec list feedback --status open --all-namespaces -n 0` lists every open feedback file, completed spec bundles included (`--query <text>` narrows by ID or title). Read a candidate's `kind` and `category` when its `target` matches: the same `target` and nature is a duplicate. Skip it and keep its ID for the report.
3. **Record** each remaining observation with the recording procedure, in the current proposal, spec or month-level feedback directory.
4. **Report by entry**:
   - **User request**: no envelope. Report recorded IDs, duplicate IDs, and the open and critical counts of this work (`--where severity=critical`). If critical items exist, recommend a separate feedback-hygiene session; do not run it unasked. If context loss prevents full coverage, state the gap instead of claiming a complete sweep.
   - **Unit stage (proposal or spec)**: record the sweep envelope:

     ```bash
     devkit workflow envelope new --unit <dir> --kind feedback --stage collect-feedback \
       --summary "<coverage, recorded IDs and duplicate IDs>" \
       --check "swept=PASS recorded=<n> duplicates=<n>"
     ```

     `swept` is `FAIL <reason>` only when the session could not be covered; name the gap with `--unverified "<gap>"` and leave the stage open. Return one line: `> Feedback sweep: <n> recorded, <n> duplicates (envelopes/feedback-NN.yaml)`.
   - **`report-session` stage of a `session` task** (no unit): steps 1 to 3 against the month-level directory, reported in the session report without an envelope.

## Planning run coverage

Before every Planning return to the user (including questions), sweep this run and its committed accumulated records
and write a new `feedback` envelope under the proposal's `envelopes/`, at `collect-feedback`, before the run's single
`worker` envelope and last commit. An earlier PASS does not cover later work, even when `next` already passes the
stage (an executor procedure, not an engine freshness check). Feedback stays inside the proposal directory; no extra
write root.

Stage-off and requested-only apply as above. Uncovered context is `swept=FAIL <gap>` plus `--unverified`; never claim
complete coverage for a failed or partial run. A separate user-requested sweep does not replace this evidence.

Acceptance and rejection both use the records made before the run returned; a rejection invokes no new agent. A
rejected proposal keeps its feedback until the Host preserves open files before cleanup. Handoff drops Planning
envelopes; Development runs its own sweep.
