# Delegation Input and Return Envelope

Read this for support-role delegation (`scout`, `challenger`, `code-reviewer`, `reconcile-reviewer`), reviews, the final change report before `dev-integration`, or the integration result. Envelopes follow devkit's contract; this reference defines their spec-driven use. A `planning-worker` or `development-worker` writes its own records ([worker records](worker-records.md)).

## 1. Input payload

Pass all five fields and never inject the whole tree; the `spec-delegate` skill's `references/payload.md` defines each field and the rows per role. When the host projection for this call is not `native` (`emulated`, `unsupported`), say so, so the substitute guarantee is explicit.

## 2. Return envelope

A role returns the fields of a devkit envelope; the Developer records them (section 6):

```yaml
status: completed | needs_input | failed
summary: "1-3 line judgment or result"
findings:
  - issue: "Issue found or change made"
    evidence: "path:line or source URL"
    failure_condition: "Under which input or state it fails (required for challenger and reviewer)"
    suggested_action: "Recommended next step"
    severity: "P2"            # P1 | P2 | P3 on every review, reconcile-check and challenger finding
assumptions: ["Assumptions made inside the approved scope"]
unverified_areas: ["Scope not explored or needing confirmation"]
checks: { tests: "PASS 14/14" }        # when the role ran checks
diff_scope: { base: "<ref>", head: "<sha>" }
```

- `completed` with an empty `findings` list is a valid pass; no filler objections.
- A finding carries only the keys above (devkit adds `resolution` and `waiver`). `severity` is `P1`, `P2` or `P3` on every finding of a `review`, `reconcile-check` or `challenger` envelope, at every effort ([review loop](review-loop.md) section 3). The reviewer sets it and the implementer records it unchanged; `reverify` carries it forward. It changes no finding resolution, check or gate outcome. `scout` and `worker` findings carry none.
- `needs_input` names the missing input or the decision only the human can make.
- `failed` covers timeout, cancellation, tool failure, unsupported host feature, or a stale `diff_scope`. A failed or stale result is never completion evidence.
- Docs impact has no envelope key: it goes into `reconcile.md` (targets, or no-impact reasoning in its body), verified by a `reconcile-check` envelope ([completion](completion.md)).
- Decide re-invocation or a stronger model from the failure reason and changed input; never repeat the same call.

## 3. Final change report (before `dev-integration`)

Kind `final-report`; the `final-change-report` stage needs `checks.tests`, `checks.build` and `checks.lint` starting with `PASS`:

```bash
devkit workflow envelope new --unit <dir> --kind final-report --stage final-change-report \
  --summary "..." --check tests="PASS 14/14" --check build="PASS" \
  --check lint="PASS devkit rules check --staged" --base <ref> --head $(git rev-parse HEAD)
```

Do not repeat changed paths (Git), docs impact and reconcile state (`reconcile.md`) or the review result (the latest review envelope). Record assumptions the user should see with `--assume`.

When open feedback marked `severity: critical` exists (`devkit spec list feedback --status open --where severity=critical`), including items the `collect-feedback` sweep just recorded, list each in the report presented to the user as one line, `FB-<slug> → <target>`, so the person deciding `dev-integration` sees that a feedback hygiene pass is due.

## 4. Integration result (after `spec-integrate`)

Integration writes no envelope: anything written after the commit would need another commit. Run `devkit rules check --ci --base <ref>` locally and report the result in the conversation; the repository CI re-runs it as the final gate (`lint-ci-clean`). Report: base integrated, conflicts resolved (if any), what was re-verified, and the two separate facts that code review completed (latest review round or reverify) and integration completed.

## 5. The spec-review report

`spec-review` writes this envelope directly (kind `review`), for both the direct run and the delegated `code-reviewer` run. Boundary violations, stray files and unmet scenarios are `findings` (each with `failure_condition`), check results are `checks`, and the verdict is the status: PASS → `status: completed` with no open findings, REVISE → `status: completed` with open findings, `needs_input` when verification is blocked.

## 6. Where reports live

A Unit (`spec` and `proposal` depth): every envelope is a file under the Unit's directory (the proposal's is dropped at handoff):

```
specs/<YYYY-MM>/<YYYYMMDD>-<slug>/envelopes/<kind>-<NN>.yaml
docs/proposals/PROP-<slug>/envelopes/<kind>-<NN>.yaml
```

- `kind`: `scout | challenger | review | reverify | reconcile-check | worker | answer | resolution | final-report` ([worker records](worker-records.md) for a run's), or any `[a-z][a-z0-9-]*` kind a workflow check names: `red` and `green` in `sdd-spec-bugfix` (the `spec-specify` skill's bugfix reference), `feedback` in `collect-feedback` (the `spec-feedback` skill). `NN` is a sequence per kind; the highest is current. Never overwrite; each write takes the next number.
- `review-NN.yaml` and `challenger-NN.yaml` record a round as found (every finding `open`); `reverify-NN.yaml` closes it, naming it in `review` and carrying its findings forward with `resolution: resolved | waived` (a waiver states its reason), plus any findings found while re-verifying. The latest round of each kind, or the latest reverify that closes it, decides; a reverify of a `challenger` round never counts for the review state.
- Required keys: `kind` (equal to the file name kind) and `status`; a malformed file is reported and ignored. Write other keys only when they carry information; do not restate Git (dates, paths) or `reconcile.md` (docs impact).
- `dev-integration` approval is not an envelope ([completion](completion.md#policy)); after it `devkit workflow next --unit <dir>` names the `integrate` stage.
- Write files with `devkit workflow envelope new --unit <dir> --kind <kind> [--stage <id>]` or `devkit workflow envelope <kind>` (`review`, `reverify`, `worker`, `answer`, `resolution`); see `devkit workflow envelope <kind> --help` for the flags; never edit YAML. `--check key=PASS|FAIL|SKIP[ detail]` is how `envelope-check-pass` stages (`feedback`, `red`, `green`) get their evidence, and `--head $(git rev-parse HEAD)` must be a real commit (`revision-ancestor` compares heads). Check files with `devkit workflow envelope check --unit <dir>`.
- A `session` task (session: no records) gets its reviewer subagent's result as a message. The conversation keeps the summary and the file path, never the whole envelope.
