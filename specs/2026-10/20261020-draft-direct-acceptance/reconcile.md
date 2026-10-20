---
reconcile_id: REC-draft-direct-acceptance
feature: SPEC-draft-direct-acceptance
status: pending
targets:
  - file: docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    resolution: modified
  - file: docs/capabilities/delivery/CAP-DLV-delivery-workflows.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-agent-guidance.md
    resolution: modified
  - file: docs/capabilities/harness/CAP-HARN-command-mount.md
    resolution: modified
  - file: docs/stories/delivery/US-incubate-and-hand-off-a-proposal.md
    resolution: modified
  - file: docs/decisions/2026-10/20261020-session-reclassification-of-a-queued-draft.md
    resolution: modified
---

# Reconciliation: Direct acceptance of drafts that need no Planning

- `CAP-DLV-proposal-incubation`: the `accept` command (rule 14: forms, eligibility conditions, base-checkout check,
  note, status restore, `--check`), the approval rule's recorded-acceptance guard for bundles bound to `sdd-proposal`
  (rule 2), the
  carried note (rule 12), Backlog's direct acceptance and session-reclassification deletion (rule 13, §3.1), the
  command, options, output, library and the four new codes.
- `CAP-DLV-delivery-workflows`: approvals record `plan-accept` with the command (rule 5), one request may ask both
  gates (rule 6), the direct acceptance path beside Planning (rule 14), the `plan-accept` request condition (4.3), the
  acceptance session's sweep and the reclassification deletion's feedback (Planning feedback), the executor command
  table, and the depth-change non-goal naming the reclassification. The `sdd-proposal` stage schema is unchanged.
- `CAP-HARN-agent-guidance`: the lowering rule's exception, the `spec`, `spec-next` and `spec-orchestrate` skill-table
  rows and commands, and the Backlog and next-work passages; the interim "small drafts run Planning at `low`" rule of
  `ADR-roadmap-in-repository` is named as ended there, while that ADR and `ADR-run-records-and-activity-branches`
  stay unedited history (`ADR-direct-acceptance-command-and-handoff-guard` names them as extended and qualified).
- `CAP-HARN-command-mount`: the command table lists `accept` and the existing `check`.
- `US-incubate-and-hand-off-a-proposal`: the narrative names the command and the direct path; scenarios 1, 2, 5 and 7
  follow the guard, the directive, the carried note and the reclassification deletion; scenario 8 is the direct
  acceptance.
- `ADR-session-reclassification-of-a-queued-draft`: the handoff's code-span rewrite had turned the generic
  `materials/` of "what goes" into this proposal's own materials path; restored to the draft's `materials/` (wording
  only).

Mirrors outside the Living Spec, kept in step: the bundled guidance (`sdd-proposal` body, bundle `AGENTS.md`, the
`spec`, `spec-next` and `spec-orchestrate` skills and references, the seed proposals README, the proposal template),
the scaffold's lifecycle comment and the devkit-spec README. The repository's own `.devkit/managed/` copies are
refreshed by `devkit sync` after integration (outside this worker's write scope).

No deferred work is retained. The workbench strategy-layer update (the proposal's §3.2) lives in another repository
and is reported to the Host, not tracked here.

Entrypoints: the derived candidates were reviewed. `CAP-DLV-proposal-incubation` already declares
`packages/devkit-spec/src/devkit_spec/proposals/`, which holds the new `accept.py`; the story gained
`proposals/accept.py` beside `handoff.py`. The broad joins (the whole bundle, `branches.py`, `errors.py`, the tests)
were rejected as declaration joins, not ownership.
