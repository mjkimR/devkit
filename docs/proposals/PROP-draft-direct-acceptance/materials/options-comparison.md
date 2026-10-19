# Options for accepting a draft without Planning

Planning material for `PROP-draft-direct-acceptance` (2026-10-19, `activity-effort` high). It compares where and when
the user's acceptance of a settled draft is recorded, and the alternative of not accepting at all. Engine facts are in
[engine evidence](engine-evidence.md). Revised twice: after `challenger-01.yaml`, which showed that the first version
omitted the rows where acceptance outside Development wins, and after `challenger-02.yaml`, which showed that an
acceptance counted as Backlog work under one policy and as a Planning commit under another contradicts 01 §4.7 and
03 §1/§4; that hybrid (A1) is replaced by A3.

## The two models

- **M1, accept on sight**: the user gives `plan-accept` for a draft whose direction is already settled; the record
  says Planning was skipped and why. The proposal, its gates and provenance travel through the normal handoff.
- **M2, the draft was never `proposal` depth**: a queued draft whose direction is settled is `spec` work waiting in the
  queue; at pickup it is converted into a spec Unit and the user's confirmation is the spec's `plan-intent`. No
  `plan-accept` exists.

Both lower the effective depth of a queued draft on the user's explicit decision; neither is safer on that count. 01
§2.2 must state the approved route either way. M2 costs more: a handoff that accepts a non-accepted proposal
(`CAP-DLV-proposal-incubation` rule 2), and no `plan-accept` record, which the supersede close (01 §7.4) and the
`--supersedes` check need. M1 keeps every existing contract of the handoff and the closes. The comparison below is
within M1, with M2 kept as option C.

## Options

- **A3. A Planning acceptance without a Planning run**: the user accepts during Backlog; the Host starts
  `plan-<slug>` from the base, sweeps its own session, runs the acceptance command as that branch's only commit and
  merges it like any Planning branch: locally under `pull_request = auto` (`finish --merge` or the local integration,
  where the `plan-<slug>` readiness check validates status, both gates and the sweep), through its PR under
  `required`. No worker, no `reviewing` commit, no review run.
- **A2. Backlog acceptance on the base**: the acceptance is a Backlog commit on the base under every policy, outside
  the PR policy; needs explicit amendments of 01 §4.7 (Unit activities on their own branch; the base status changes
  only at a merge) and 03 §4 (acceptance through the Planning PR under `required`).
- **B. Acceptance at Development start**: the first commit on `dev-<slug>`, followed by the handoff; the acceptance
  rides in the Development PR.
- **C. Reclassify at pickup (M2)**.

| | A3 | A2 | B | C |
| --- | --- | --- | --- | --- |
| When the user decides | Backlog, any time before Development | Backlog | When Development starts | When Development starts |
| Branches before Development | One short `plan-<slug>`, one commit | None | None | None |
| PRs under `required` | A one-commit Planning PR, then Development | Development only | Development only | Development only |
| 01 §4.7 Unit activities on their own branch; separate Planning and Development PRs; base status changes at a merge | Kept | Amended | Broken | Broken |
| 03 §1 and §4 (Backlog never through a PR; acceptance through the Planning PR under `required`) | Kept | Amended | Replaced by the Development PR | Not applicable |
| 01 §5.1 Backlog changes only drafts | Kept: the acceptance is Planning's, not Backlog's | Amended | Kept | Kept |
| Mechanical validation before the base sees `accepted` | The readiness check on local merge; PR review under `required` | None | None | None |
| 01 §7.4 supersede and abandon act on the accepted proposal on the base | Work unchanged | Work unchanged | Broken: the base copy is still `draft`, `--supersedes` refuses it | No accepted proposal to supersede |
| `cloud-pr` start (autohub starts an accepted proposal, 01 §7.1) | Works unchanged | Works unchanged | Local Host only | Local Host only |
| New guards for a draft owned by `dev-<slug>` (check, Planning start, `padr`, list display) | None | None | All four | All four |
| Partial state on refusal or objection | A `plan-<slug>` to discard on the user's decision; the base draft is untouched | None | A `dev-<slug>` with a draft, refused by attach | Same as B |
| Staleness between acceptance and Development | Possible, covered by the premise check (01 §7.3) | Same | None | None |
| `dev_effort` confirmation | Reviewed in the acceptance request, confirmed again at Development start | Same | Same exchange | Same exchange |
| Carried body, gates, milestone, provenance | Yes | Yes | Yes | Only with a new conversion command |

## Assessment

- **A3 is recommended.** It changes no structural rule of the strategy layer: the acceptance is a Planning acceptance
  whose Planning had nothing to do, on the slug's own branch, merged like any other, and validated by the existing
  readiness check before the base sees `accepted`. It saves what costs most (the worker run, the `reviewing` commit,
  the question rounds) but keeps a short branch, which under `worktree = required` also means a worktree and its
  setup. Under `required` a team sees the acceptance in its own small PR before any implementation; an objection
  there closes the PR and discards the branch on the user's decision, leaving the draft for Planning.
- **A2** saves the branch too, at the price of amending 01 §4.7 and 03 §1/§4 so that a Unit's status may change on
  the base without a merge, and of losing the readiness check and, under `required`, the team's view of the
  direction before implementation.
- **B** saves the acceptance PR under `required` and decides together with the Development effort, but breaks 01 §4.7
  and §7.4, needs four guards for a new "draft owned by Development" state and leaves a stuck branch on refusal.
- **C** costs a conversion command and loses the `plan-accept` record the closes depend on.

## Common to every M1 option

- The engine opens `gate:plan-accept` only after `collect-feedback` passes (or is switched off) and with
  `status: accepted` on disk, so the executor sweeps its own acceptance session first (usually zero observations, a
  valid PASS) and then accepts; the stage schema stays ([engine evidence](engine-evidence.md)).
- The handoff checks only the status today; for a bundle bound to `sdd-proposal` it must also require the accepted
  `gate:plan-accept` record, or a partial acceptance hands off without the user's decision.
- The acceptance request shows `task_kind`, which `plan-accept` confirms, and the recorded `planning_effort` hint.

## Eligibility (Q1)

See `PADR-eligibility-for-direct-acceptance`. Mechanical: `status: draft`; an accepted `gate:plan-intent`; no
`needs_decompose: true`; no `supersedes`; no `plan-<slug>` other than the acceptance's own; a valid
`task_kind`. Judgment, shown to the user: the direction leaves nothing to compare, no open spike question, not a depth
escalation; the request names the `planning_effort` hint and, when it is not `low`, why Planning is skipped anyway.
No size limit: depth is not size (01 §2.2), and the user's explicit decision is the safeguard.
