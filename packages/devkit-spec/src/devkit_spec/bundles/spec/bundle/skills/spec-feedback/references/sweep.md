# Feedback Sweep

Read this for a workflow stage sweep, a Planning run's return or a user-requested session sweep.

## Entry

- **User-requested session sweep**: only an explicit user message selects it (an agent-chosen `/spec-feedback` stays
  autonomous). Cover the whole session regardless of policy; write no envelope.
- **Workflow stage**: `devkit workflow next --unit <dir>` names `collect-feedback`; zero observations passes.
  - `[SKIPPED: collect-feedback ...]`: report the stage as skipped; observed capture stays on.
  - `capture=requested-only`: record nothing and write the envelope with
    `--check "swept=PASS skipped=capture.requested-only"`; a `session` task reports the skip without one.

## Procedure

1. **Collect** unrecorded observations from this session and `git diff`.
2. **Look up** each candidate by step 2 of the skill's recording procedure, adding `--all-namespaces` to the search:
   `devkit docs search "<symptom and asset words>" --kind feedback --history --all-namespaces -n 5`. A candidate the
   matched status says not to record is a duplicate; keep the existing ID for the report.
3. **Record** the rest by the skill's recording procedure from its step 3.
4. **Report by entry**:
   - **User request**: recorded IDs, duplicate IDs, open and critical counts (`--where severity=critical`). With
     critical items, recommend a `feedback-hygiene` session; never run it unasked.
   - **Unit stage**:

     ```bash
     devkit workflow envelope new --unit <dir> --kind feedback --stage collect-feedback \
       --summary "<coverage, recorded IDs and duplicate IDs>" \
       --check "swept=PASS recorded=<n> duplicates=<n>"
     ```

     If part of the session could not be covered: `swept=FAIL <gap>` with `--unverified "<gap>"`; the stage stays
     open.
   - **`report-session` stage** (no unit): in the session report, without an envelope.

## Planning run coverage

Before every Planning return to the user, questions included, sweep this run and write a new `feedback` envelope at
`collect-feedback` under the proposal's `envelopes/`, before the run's `worker` envelope and last commit. An earlier
PASS does not cover later work even when `next` passes the stage (the engine does not check freshness); a
user-requested sweep does not replace it.
