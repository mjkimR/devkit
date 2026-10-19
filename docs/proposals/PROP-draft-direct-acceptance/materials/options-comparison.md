# Options for accepting a draft without Planning

Planning material for `PROP-draft-direct-acceptance` (2026-10-19, `activity-effort` high). It compares where and when
the user's acceptance of a settled draft is recorded, and the alternative of not accepting at all. Engine facts are in
[engine evidence](engine-evidence.md). Revised after the `challenger` pass (`challenger-01.yaml`), which showed that the
first version omitted the rows where a Backlog acceptance wins.

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

- **A1. Backlog acceptance under the PR policy** (hybrid): the user accepts during Backlog. Under
  `pull_request = auto` the acceptance is a Backlog commit on the base; under `required` it is the single commit of a
  `plan-<slug>` branch merged through its PR, exactly as a Planning acceptance commit is today (03 §4), with no worker
  and no review run.
- **A2. Backlog acceptance on the base, always**: as A1, but on the base under `required` too, as Backlog work outside
  the PR policy (an exception to 03 §4).
- **B. Acceptance at Development start**: the first commit on `dev-<slug>`, followed by the handoff; the acceptance
  rides in the Development PR.
- **C. Reclassify at pickup (M2)**.

| | A1 | A2 | B | C |
| --- | --- | --- | --- | --- |
| When the user decides | Backlog, any time before Development | Backlog | When Development starts | When Development starts |
| Branches and PRs under `required` | A one-commit Planning PR, then Development | Development only | Development only | Development only |
| 01 §4.7 separate Planning and Development PRs; the accepted proposal on the base is the start queue | Kept | Kept (no Planning PR, base copy accepted) | Broken | Broken |
| 03 §4 acceptance through the Planning PR under `required` | Kept | Exception needed | Replaced by the Development PR | Not applicable |
| 01 §5.1 Backlog changes only drafts | Amended: Backlog may accept an eligible draft | Amended | Kept | Kept |
| 01 §7.4 supersede and abandon act on the accepted proposal on the base | Work unchanged | Work unchanged | Broken: the base copy is still `draft`, `--supersedes` refuses it | No accepted proposal to supersede |
| `cloud-pr` start (autohub starts an accepted proposal, 01 §7.1) | Works unchanged | Works unchanged | Local Host only | Local Host only |
| New guards for a draft owned by `dev-<slug>` (check, Planning start, `padr`, list display) | None | None | All four | All four |
| Partial state on refusal | None on the base; under `required` an empty `plan-<slug>` to discard | None | A `dev-<slug>` with a draft, refused by attach | Same as B |
| Staleness between acceptance and Development | Possible, covered by the premise check (01 §7.3) | Same | None | None |
| `dev_effort` confirmation | Separate exchange at Development start | Same | Same exchange | Same exchange |
| In progress (`next-work`) | From acceptance on, as any accepted proposal | Same | From `dev-<slug>` on | Same as B |
| Carried body, gates, milestone, provenance | Yes | Yes | Yes | Only with a new conversion command |

## Assessment

- **A1 is recommended.** It keeps 01 §4.7, 03 §4 and the 01 §7.4 closes unchanged and needs no new branch guard; the
  only strategy changes are that Backlog may accept an eligible draft (§5.1, §4.4, §6.2) and that §2.2 names this
  route. Under `auto` it is one base commit, which is all the proposal set out to save; under `required` the team still
  reviews the direction in its own small PR before any implementation exists. Backlog is `direct`-only, so a local
  Host records the acceptance and autohub starts the accepted proposal as it does today.
- **A2** removes the acceptance PR under `required` too, at the price of an exception to 03 §4: a team loses the
  review of the direction before implementation.
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
`needs_decompose: true`; no `supersedes`; no Planning branch other than the one the acceptance itself uses; a valid
`task_kind`. Judgment, shown to the user: the direction leaves nothing to compare, no open spike question, not a depth
escalation; the request names the `planning_effort` hint and, when it is not `low`, why Planning is skipped anyway.
No size limit: depth is not size (01 §2.2), and the user's explicit decision is the safeguard.
