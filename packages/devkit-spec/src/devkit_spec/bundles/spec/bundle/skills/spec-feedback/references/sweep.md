# Feedback Sweep

Read this for a workflow stage sweep, a Planning run's return or a user-requested session sweep.

## Entry

- **User-requested session sweep**: only an explicit user message selects it; an agent-chosen `/spec-feedback` stays
  autonomous. Cover the whole session regardless of policy and write no envelope.
- **Workflow stage**: `devkit workflow next --unit <dir>` names `collect-feedback`. Zero observations passes.
  - If `next` prints `[SKIPPED: collect-feedback ...]`, report the stage as skipped; observed capture stays on.
  - Under `capture=requested-only`, record nothing and write the envelope with
    `--check "swept=PASS skipped=capture.requested-only"`; a `session` task reports the skip without one.

## Procedure

1. **Collect** unrecorded observations from this session and `git diff`.
2. **Deduplicate** against `devkit spec list feedback --status open --all-namespaces -n 0`: a candidate with a listed
   file's `target` and the same nature is a duplicate. Skip it and keep the listed ID.
3. **Record** each remaining observation with the skill's recording procedure.
4. **Report by entry**:
   - **User request**: recorded IDs, duplicate IDs, and the open and critical counts (`--where severity=critical`). If
     critical items exist, recommend a `feedback-hygiene` session; do not run it unasked.
   - **Unit stage**:

     ```bash
     devkit workflow envelope new --unit <dir> --kind feedback --stage collect-feedback \
       --summary "<coverage, recorded IDs and duplicate IDs>" \
       --check "swept=PASS recorded=<n> duplicates=<n>"
     ```

     If part of the session could not be covered, write `swept=FAIL <gap>` with `--unverified "<gap>"` and leave the
     stage open.
   - **`report-session` stage** (no unit): report in the session report without an envelope.

## Planning run coverage

Before every Planning return to the user, questions included, sweep this run and write a new `feedback` envelope at
`collect-feedback` under the proposal's `envelopes/`, before the run's `worker` envelope and last commit. An earlier
PASS does not cover later work even when `next` passes the stage, because the engine does not check freshness; a
user-requested sweep does not replace it.
