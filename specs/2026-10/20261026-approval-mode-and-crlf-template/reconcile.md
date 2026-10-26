---
reconcile_id: REC-approval-mode-and-crlf-template
status: resolved
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
  - file: docs/development/reference/distribution.md
    resolution: modified
---

# Reconciliation: `SPEC-approval-mode-and-crlf-template`

- `CAP-DLV-proposal-incubation` ("Proposal review briefings and combined acceptance"): the error table gains a `Mode`
  column. `PROPOSAL_APPROVAL_NOT_READY` is `BLOCKED` and says the user or Host resolves the prerequisite; the new
  `PROPOSAL_APPROVAL_REPLY_INVALID` row is `INPUT_ERROR` for an invalid requested or confirmed mode or effort;
  `PROPOSAL_APPROVAL_STALE` stays `MAINTENANCE` (AC-01 to AC-04). `PROPOSAL_REVIEW_INVALID` gets the `INPUT_ERROR`
  its class (`ReportInvalidError`, `input_error = True`) already emits; only the column is new for it.
- `CAP-DIST-sync-and-transactions` (Commented Template, **Append-only**): existing lines keep their bytes, line
  endings included; added lines end in CRLF when every line ending of the file is CRLF, and in LF otherwise
  (AC-06, AC-07). The sentence was missing: "no line is changed" did not name line endings.

`docs/development/reference/distribution.md`, the quick reference, mirrors the line-ending sentence in its
`devkit config template` row. The completion reference change (AC-05) is bundle guidance with no Living Spec
statement: `CAP-DLV-proposal-incubation` already says acceptance and handoff take no published report. No use case
changes: `UC-incubate-and-hand-off-a-proposal` names no `PROPOSAL_APPROVAL_*` code or mode, and no use case describes
config template line endings. No architecture, ADR or glossary impact.

## Entrypoints

`devkit spec entrypoints derive` proposes the changed files for the targets; no pair is written. The changed doorways
are already declared (`native_plan_accept.py` for `CAP-DLV-proposal-incubation`, `config.py` for
`CAP-DIST-sync-and-transactions`); the other candidates are tests, a guidance source, a sync output and the other
target's module, not doorways of these documents.

## Source feedback

Resolved with a Disposition: `FB-approval-refusals-emit-maintenance`, `FB-completion-guidance-report-uri` and
`FB-config-template-rewrites-crlf-line-endings`.

## Deferred work

None in the agreed scope. Spec Non-Goal 2 leaves the selection edits (`prepare_config_update`), which also rewrite
a CRLF file's line endings, outside this unit: recorded as `FB-selection-edits-rewrite-crlf-line-endings` (this
unit's `feedback/`, `status: open`).
