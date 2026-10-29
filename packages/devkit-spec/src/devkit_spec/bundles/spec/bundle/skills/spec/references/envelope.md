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
