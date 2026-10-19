# Options for accepting a draft without Planning

Planning material for `PROP-draft-direct-acceptance` (2026-10-19, `activity-effort` high). It compares where and when
the user's acceptance of a settled draft is recorded, and the alternative of not accepting at all. Engine facts are in
[engine evidence](engine-evidence.md). Revised twice: after `challenger-01.yaml`, which showed that the first version
omitted the rows where acceptance outside Development wins, and after `challenger-02.yaml`, which showed that an
acceptance counted as Backlog work under one policy and as a Planning commit under another contradicts 01 §4.7 and
03 §1/§4; that hybrid (A1) is replaced by A3. A third pass (`challenger-03.yaml`) added the status-quo baseline, which
shows that A3 saves little. A fourth pass (`challenger-04.yaml`) showed that limiting A2 to `pull_request = auto`
contradicts the Backlog policy exemption (01 §5.1, 03 §1, §3, §4); A2 is now independent of policy, like all other
Backlog work, with the auto-only variant kept as A2a.

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

- **S. Status quo (baseline)**: Planning at `low` in `direct` mode. The Host starts `plan-<slug>` (with
  `--no-worktree`, or a worktree and its setup under `worktree = required`), commits `status: reviewing`, reviews with
  questions only, sweeps, writes its `worker` envelope, asks for `plan-accept`, records it with `status: accepted` and
  merges the branch (locally under `pull_request = auto`, through a PR under `required`).
- **A2. Backlog acceptance on the base**: the user accepts during Backlog; after the sweep of the acceptance session
  the command records the acceptance and the Host commits it on the base checkout as Backlog work, under every
  policy, as Backlog's other work already is (01 §5.1, 03 §1). Under `pull_request = required` the request says that
  the direction gets no PR review, and the user may choose Planning instead for that draft.
- **A2a. A2 under `pull_request = auto` only**: under `required` the command refuses and small drafts keep Planning.
  This needs a rule of its own (under `required` every direction is reviewed in a PR before implementation) and
  amendments of the Backlog exemption in 01 §5.1 and 03 §1, §3 and §4, because a policy key would then decide whether
  a proposal gets a Planning branch.
- **A3. A Planning acceptance without a Planning run**: the acceptance is the only commit of a short `plan-<slug>`,
  merged like any Planning branch.
- **B. Acceptance at Development start**: the first commit on `dev-<slug>`, followed by the handoff.
- **C. Reclassify at pickup (M2)**.
- **D. No new path**: small drafts keep Planning at `low`; only the handoff guard and the planned `accept` command
  (01 §10) ship.

| | S | A2 | A2a | A3 | B | C |
| --- | --- | --- | --- | --- | --- | --- |
| Branch before Development | `plan-<slug>` | None | None (under `required`: S) | `plan-<slug>`, one commit | None | None |
| Acceptance commits | `reviewing`, worker record and sweep, acceptance, merge | One base commit | Same as A2 | One branch commit, merge | One `dev-<slug>` commit | One `dev-<slug>` commit |
| Strategy amendments beyond naming the path | None | 01 §4.7 (one status change on the base without a merge), 03 §3 (base checkout), 03 §4 (a direct acceptance takes no PR) | As A2, plus a new policy rule and 01 §5.1, 03 §1 | None | 01 §4.7, §7.4 | 01 §2.2 conversion |
| Policy decides the flow structure (03 §1) | No | No | Yes | No | No | No |
| Validation before the base sees `accepted` | Readiness only on the MCP integration path | The command's checks | The command's checks | Same as S | The command's checks | None |
| Team review of the direction under `required` | Planning PR | None, the user's choice per draft | Planning PR | One-commit PR | Development PR, after implementation | Development PR |
| 01 §7.4 closes and `cloud-pr` start | Work | Work | Work | Work | Broken / local only | No record / local only |
| New guards for a draft owned by `dev-<slug>` | None | None | None | None | Four | Four |
| Partial state on refusal | Planning continues | None (nothing committed) | None | A `plan-<slug>` to discard, local and remote | A `dev-<slug>` refused by attach | Same as B |

Saving against S per configuration:

| Configuration | A2 saves | A3 saves |
| --- | --- | --- |
| `pull_request = auto`, no worktree | Branch start, local merge, `reviewing` commit, worker record, question round | `reviewing` commit, worker record, question round |
| `pull_request = auto`, `worktree = required` | As above, plus a worktree and its setup | As above |
| `pull_request = required` | As above, plus the Planning PR | As above (the Planning PR stays) |

## Assessment

- **A2 is recommended.** It is the only kept option that removes the branch, and under `required` the Planning PR,
  which is the cost §1.1 names. It stays inside the existing Backlog exemption: like every Backlog change it is
  outside the worktree and PR policies, and the user decides per draft, seeing that the direction gets no PR review.
  The amendments are explicit and few: one status change on the base without a merge (01 §4.7), the base checkout for
  it (03 §3) and the note in 03 §4 that a direct acceptance takes no PR.
- **A2 against D**: under the defaults (`auto`, no worktree) A2 saves two Git operations, a commit, a record and a
  question round per small draft; it grows with a worktree policy and with `required`. D keeps the strategy layer
  as it is and still ships the guard and the planned command. Choose D if that saving does not justify the path.
- **A2a** keeps the Planning PR under `required` but makes a policy key decide the flow structure, against 03 §1.
- **A3** changes no structural rule but saves only a commit, a record and a question round; it is dominated by D.
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
`needs_decompose: true`; no `supersedes`; no local or fetched `plan-<slug>`; no envelope hold; the base checkout; a valid
`task_kind`. Judgment, shown to the user: the direction leaves nothing to compare, no open spike question, not a depth
escalation; the request names the `planning_effort` hint and, when it is not `low`, why Planning is skipped anyway.
No size limit: depth is not size (01 §2.2), and the user's explicit decision is the safeguard.
