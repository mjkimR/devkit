---
reconcile_id: REC-handoff-modes-and-template-report
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-project-policy.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
    resolution: modified
---

# Reconciliation: `SPEC-handoff-modes-and-template-report`

- `CAP-DLV-proposal-incubation`: the §4.12 `SPEC_HANDOFF_NOT_READY` row drops the report URI and says the user or
  Host resolves the prerequisite; the `SPEC_HANDOFF_REPLY_INVALID` row names the automatic `dev_effort` case and the
  caller's correction (AC-05). The emitted modes now match the documented `BLOCKED`, `INPUT_ERROR` and `MAINTENANCE`
  (AC-01 to AC-04). The Host-authorized lifecycle CLI section states that the composed handoff and
  `accept --mode accept_and_handoff` read `proposal-handoff`, and that the plain handoff in a `dev-<slug>` checkout is
  the Host-run step after that decision and reads no policy itself (AC-07).
- `CAP-DLV-project-policy` rule 4 states the same reader split (AC-07).
- `CAP-DLV-delivery-workflows`: the `code-reviewer` row writes probes in its round's own subdirectory of the ignored
  probe path, read by no other round and left for worktree removal (AC-06).
- `CAP-DIST-sync-and-transactions` (Commented Template) gains a **Result** bullet: `state` is `unchanged` exactly when
  the bytes stay the same, and `added` names every key and table written, commented ones included (AC-09).

The quick reference `docs/development/reference/distribution.md` mirrors the AC-09 result contract. No use case
changes: `UC-incubate-and-hand-off-a-proposal` names the handoff codes without their modes and describes no reviewer
probes or template result, so its steps hold. No architecture, ADR or glossary impact.

## Entrypoints

`devkit spec entrypoints derive` proposed every changed file for every target; no pair is written. The targets already declare their doorways, and the changed files are
error classes, tests, guidance mirrors and a sync output, not doorways.

## Source feedback

Resolved with a Disposition: `FB-handoff-refusals-emit-maintenance`, `FB-code-reviewer-probe-deletion`,
`FB-plain-handoff-skips-proposal-handoff-policy` and `FB-config-template-reports-unchanged-after-writing`.

## Deferred work

- `FB-config-template-rewrites-crlf-line-endings` (this unit's `feedback/`): the CRLF line-ending rewrite review-01
  found, waived in reverify-01 as outside the agreed scope.
