# Return Envelope and Reports

Read this to record a support role's return (`scout`, `challenger`, `code-reviewer`, `reconcile-reviewer`), write the final change report before `dev-integration`, or report the integration result. The call itself is the `spec-delegate` skill; a `planning-worker` or `development-worker` writes its own records ([worker records](worker-records.md)).

## 1. Return envelope

A role returns these fields; the Developer records them (section 4):

```yaml
status: completed | needs_input | failed
summary: "1-3 line judgment or result"
findings:
  - issue: "Issue found or change made"
    evidence: "path:line or source URL"
    failure_condition: "Under which input or state it fails (required for challenger and reviewer)"
    suggested_action: "Recommended next step"
    severity: "P2"            # see below
assumptions: ["Assumptions made inside the approved scope"]
unverified_areas: ["Scope not explored or needing confirmation"]
checks: { tests: "PASS 14/14" }        # when the role ran checks
diff_scope: { base: "<ref>", head: "<sha>" }
```

- `completed` with no findings is a valid pass.
- `severity` per [review loop](review-loop.md) section 3 (`review`, `reconcile-check` and `challenger` only).
- `needs_input` names the missing input or the decision only the human can make. `failed` (timeout, cancellation, tool failure, unsupported host feature, stale `diff_scope`) is never completion evidence.
- Docs impact has no key: it goes into `reconcile.md`, verified by a `reconcile-check` envelope.

## 2. Final change report (before `dev-integration`)

The `final-change-report` stage needs `checks.tests`, `checks.build` and `checks.lint` starting with `PASS`:

```bash
devkit workflow envelope new --unit <dir> --kind final-report --stage final-change-report \
  --summary "..." --check tests="PASS 14/14" --check build="PASS" \
  --check lint="PASS devkit rules check --staged" --base <ref> --head $(git rev-parse HEAD)
```

- If the final-report is the only pending file, run `devkit workflow envelope commit --unit <dir> --file envelopes/final-report-NN.yaml` after authoring. Prepare integration after that commit, because HEAD changes invalidate older preparation. Keep its evidence SHAs unchanged. Accompanying source/document changes and multiple records require a combined manual commit.
- After a Git/hook/signing failure, fix the cause and retry the same file; do not rerun authoring. `ENVELOPE_COMMIT_UNCERTAIN` requires inspecting HEAD/index/worktree before any further mutation.
- Omit what Git, `reconcile.md` and the latest review envelope already hold; record assumptions the user should see with `--assume`.
- Add each item `devkit docs list feedback --status open --where severity=critical` lists to the report presented to the user, one line each: `FB-<slug> → <target>`.

## 3. Integration result (after `spec-integrate`)

Report in the conversation; integration writes no envelope (a file written after the merge would need another commit):

1. The result of `devkit rules check --ci --base <ref>`.
2. The base integrated, the conflicts resolved and what was re-verified.
3. That code review completed and that integration completed, as two separate facts.

## 4. Where envelopes live

Every envelope of a Unit (`spec` and `proposal` depth) is a file under its directory; a `session` task writes none and receives its reviewer's result as a message.

```
specs/<YYYY-MM>/<YYYYMMDD>-<slug>/envelopes/<kind>-<NN>.yaml
docs/proposals/PROP-<slug>/envelopes/<kind>-<NN>.yaml
```

- `kind` is `scout | challenger | review | reverify | reconcile-check | worker | answer | resolution | final-report`, or a kind a workflow check names (`red`, `green`, `feedback`). `NN` is a per-kind sequence: the highest is current, and every write takes the next number.
- `review-NN` and `challenger-NN` record a round as found (every finding `open`); a `reverify-NN` closes it with `resolution: resolved | waived` per finding (a waiver states its reason). The latest round of each kind, or the reverify closing it, decides; a `challenger` reverify never counts for the review state.
- Write envelopes with `devkit workflow envelope new --unit <dir> --kind <kind> [--stage <id>]` or `devkit workflow envelope <kind>`, never by editing YAML (`--help` lists the flags); `--head` must be a real commit. Check them with `devkit workflow envelope check --unit <dir>`.
- In the conversation, cite an envelope by its summary and path, never its whole content.


## 5. Explicit single-envelope commit

Authoring remains write-only; `next`, `check` and `show` stay read-only. For one existing, fully authored envelope as the sole pending file, `devkit workflow envelope commit --unit <dir> --file envelopes/<kind>-<NN>.yaml` stages that literal path and runs ordinary Git hooks/signing. The deterministic subject uses the tracked SPEC/PROP anchor slug and envelope identity. A clean exact record already in HEAD returns `already_committed` without a second commit. Modified history, skeletons, unrelated dirty paths, partial staging and unsupported Git state refuse before mutation. The command grants no approval, push or merge authority.

Review/reverify and final-report are eligible after their associated work is committed. Feedback with no findings is eligible only when its envelope is the sole pending file. Keep source fixes, Living Spec reflection, multi-record Planning returns, acceptance/decision transactions and problem/emergency commits in their existing combined manual commits. Never detach a record from work it must accompany.
