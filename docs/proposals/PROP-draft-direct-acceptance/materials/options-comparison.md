# Options for accepting a draft without Planning

Planning material for `PROP-draft-direct-acceptance` (2026-10-19, `activity-effort` high). It compares where and when
the user's acceptance of a settled draft is recorded, and the alternative of not accepting at all. Engine facts are in
[engine evidence](engine-evidence.md). Revised twice: after `challenger-01.yaml`, which showed that the first version
omitted the rows where acceptance outside Development wins, and after `challenger-02.yaml`, which showed that an
acceptance counted as Backlog work under one policy and as a Planning commit under another contradicts 01 §4.7 and
03 §1/§4; that hybrid (A1) is replaced by A3. A third pass (`challenger-03.yaml`) added the status-quo baseline, which
shows that A3 saves little, and limited A2 to `pull_request = auto`.

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

- **S. Status quo (baseline)**: Planning at `low` in `direct` mode. The Host starts `plan-<slug>` (a worktree and its
  setup under `worktree = required`), commits `status: reviewing`, reviews with questions only, sweeps, writes its
  `worker` envelope, asks for `plan-accept`, records it with `status: accepted` and merges the branch (a PR under
  `required`).
- **A2. Backlog acceptance on the base, under `pull_request = auto` only**: the user accepts during Backlog; after the
  sweep of the acceptance session the command records the acceptance and the Host commits it on the base as Backlog
  work. Under `required`, 03 §4 already sends every acceptance commit through the Planning PR, so a direct acceptance
  is not offered there and small drafts run Planning at `low` as today. Needs 01 §4.7 to allow this one status change
  on the base without a merge, as it already allows Backlog's edits of drafts.
- **A3. A Planning acceptance without a Planning run**: the acceptance is the only commit of a short `plan-<slug>`,
  merged like any Planning branch (locally under `auto`, through its PR under `required`).
- **B. Acceptance at Development start**: the first commit on `dev-<slug>`, followed by the handoff.
- **C. Reclassify at pickup (M2)**.
- **D. No new path**: small drafts keep Planning at `low`; only the handoff guard and the planned `accept` command
  (01 §10) ship.

| | S | A2 | A3 | B | C |
| --- | --- | --- | --- | --- | --- |
| Branch and worktree before Development | `plan-<slug>` | None | `plan-<slug>`, one commit | None | None |
| Commits for the acceptance | `reviewing`, review, sweep and worker record, acceptance, merge | One base commit | One branch commit, merge | One `dev-<slug>` commit | One `dev-<slug>` commit |
| PRs under `required` | Planning PR, then Development | Not offered: S applies | One-commit Planning PR, then Development | Development only | Development only |
| 01 §4.7 (Unit activities on their own branch; separate Planning and Development PRs; base status changes at a merge) | Kept | Amended: one Backlog status change on the base | Kept | Broken | Broken |
| 03 §1 and §4 | Kept | Kept (§1 notes that a direct acceptance is Backlog work under `auto`) | Kept | Replaced by the Development PR | Not applicable |
| 01 §5.1 Backlog changes only drafts | Kept | Amended: Backlog may accept an eligible draft | Kept | Kept | Kept |
| Validation before the base sees `accepted` | The command's checks; readiness only on the MCP integration path | The command's checks | Same as S | The command's checks | None |
| 01 §7.4 closes and `cloud-pr` start | Work | Work | Work | Broken / local only | No record / local only |
| New guards for a draft owned by `dev-<slug>` | None | None | None | Four | Four |
| Partial state on refusal | Planning continues | None (nothing committed) | A `plan-<slug>` to discard, local and remote | A `dev-<slug>` refused by attach | Same as B |
| Saving against S | | Branch, worktree, setup, merge, `reviewing` commit, worker record | `reviewing` commit, worker record, questions-only review | Branch, merge, Planning PR | Same as B |

The validation row reflects where checks run today: the `plan-<slug>` readiness check runs only on the MCP local
integration path (`integration_integrate`); `devkit worktree finish --merge` runs only the envelope-hold guard. The
command's own checks (eligibility, the engine's gate recording) and the handoff guard are what every option relies on.

## Assessment

- **A2 is recommended.** It is the only kept option that removes what S costs most: the branch, its worktree and
  setup, and the merge. Limiting it to `pull_request = auto` keeps 03 §4 as it is, so a team that requires PRs still
  reviews every direction before implementation; the price is one explicit amendment of 01 §4.7 (and §5.1, §4.4),
  of the same kind as the Backlog edits of drafts it already allows.
- **A3** changes no structural rule but saves only a commit, a record and a short review against S, for a new path,
  new eligibility rules and several strategy edits.
- **D** is the honest alternative to A3: if the branch must stay, the saving does not justify a new path; the handoff
  guard and the planned `accept` command are worth shipping alone.
- **B** breaks 01 §4.7 and §7.4 and needs four guards; **C** loses the `plan-accept` record the closes depend on.

## Common to every M1 option

- The engine opens `gate:plan-accept` only after `collect-feedback` passes (or is switched off) and with
  `status: accepted` on disk, so the executor sweeps its own acceptance session first (usually zero observations, a
  valid PASS) and then accepts; the stage schema stays ([engine evidence](engine-evidence.md)).
- The handoff checks only the status today; for a bundle bound to `sdd-proposal` it must also require the accepted
  `gate:plan-accept` record, or a partial acceptance hands off without the user's decision.
- The acceptance request shows `task_kind`, which `plan-accept` confirms, and the recorded `planning_effort` hint.

## Eligibility (Q1)

See `PADR-eligibility-for-direct-acceptance`. Mechanical: `status: draft`; an accepted `gate:plan-intent`; no
`needs_decompose: true`; no `supersedes`; no local or fetched `plan-<slug>`; no envelope hold; a valid
`task_kind`. Judgment, shown to the user: the direction leaves nothing to compare, no open spike question, not a depth
escalation; the request names the `planning_effort` hint and, when it is not `low`, why Planning is skipped anyway.
No size limit: depth is not size (01 §2.2), and the user's explicit decision is the safeguard.
