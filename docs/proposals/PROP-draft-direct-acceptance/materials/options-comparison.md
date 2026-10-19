# Options for accepting a draft without Planning

Planning material for `PROP-draft-direct-acceptance` (2026-10-19, `activity-effort` high). It compares where and when
the user's acceptance of a settled draft is recorded, and the alternative of not accepting at all. Engine facts are in
[engine-evidence](engine-evidence.md).

## The two models

- **M1, accept on sight**: the user gives `plan-accept` for a draft whose direction is already settled; the record
  says Planning was skipped and why. The proposal, its gates and provenance travel through the normal handoff.
- **M2, the draft was never `proposal` depth**: a queued draft whose direction is settled is really `spec` work waiting
  in the queue; at pickup it is converted into a spec Unit and the user's confirmation is the spec's `plan-intent`.
  No `plan-accept` exists.

M2 is the more literal reading of `planning-depth` (01 §2.2: a clear direction is `spec`), but it needs a handoff that
accepts a non-accepted proposal (`CAP-DLV-proposal-incubation` rule 2), a depth marker on drafts (the axes are not
stored, `ADR-task-kind-and-planning-depth`) and a second way of lowering depth, which 01 §2.2 forbids so that an agent
cannot classify low to save cost. M1 keeps every existing contract of the handoff and only adds a way to reach
`accepted`. The comparison below is within M1, with M2 kept as option C.

## Options

| | A. Backlog acceptance on the base | B. Acceptance at Development start on `dev-<slug>` | C. Reclassify at pickup (M2) |
| --- | --- | --- | --- |
| When the user decides | During Backlog, any time before Development | When Development of the draft starts | When Development starts |
| Where the acceptance is committed | The base, as Backlog work | `dev-<slug>`, first commit, followed by the handoff commit | No acceptance; a spec Unit on `dev-<slug>` |
| Branches and PRs under `pull_request = required` | Development only; acceptance bypasses review | Development only; the acceptance and the handoff ride in the Development PR | Development only |
| 01 §5.1 "Backlog changes only a draft" | Broken: Backlog moves `draft` to `accepted` | Kept: Development owns the slug once `dev-<slug>` exists | Kept |
| 03 §4 "acceptance through the Planning PR under `required`" | Needs a carve-out (acceptance outside any PR) | Kept in spirit: the acceptance is reviewed in the only PR the slug has | Not applicable |
| `sdd-proposal` body "record `plan-accept` on `plan-<slug>`, never on the base" | Broken | Changed to "on `plan-<slug>`, or on `dev-<slug>` for a direct acceptance; never on the base" | Not applicable |
| In-progress state (`next-work`) | The draft becomes an `accepted` proposal at once; accepting several drafts in one Backlog pass makes several Units in progress before any is started | The slug is in progress from `dev-<slug>` on, as for any Development | Same as B |
| Staleness between acceptance and Development | Possible; covered by the Development premise check (01 §7.3) | None: decided when Development starts | None |
| `dev_effort` confirmation | Separate exchange at Development start | Same exchange as the acceptance | Same exchange |
| Base copy while the branch lives | `accepted`, Backlog leaves it alone already | `draft` on the base while `dev-<slug>` deletes it: `devkit spec proposal check` must also refuse when `dev-<slug>` exists | Same as B |
| Carried body, gates, milestone, provenance | Yes (handoff) | Yes (handoff) | Only with a new conversion command |
| Modes | Any (base commit, then the usual start) | The Host records it in `direct` before handing Development to a worker or Cloud Agent, as inline Planning of a `spec` task does (01 §4.6) | Same as B |

## Common to A and B

- The engine opens `gate:plan-accept` only after `collect-feedback` passes and with `status: accepted` on disk, so the
  executor sweeps its own acceptance session first (usually zero observations, a valid PASS) and then accepts; the
  stage schema stays ([engine evidence](engine-evidence.md)).
- The handoff checks only the status today; it must also require the accepted `gate:plan-accept` record, or a
  partial acceptance hands off without the user's decision.

## Assessment

- **B is recommended.** It reaches the goal (one branch, one PR, no Planning worker) with the fewest changes to the
  strategy layer: no exception to 03 §4, no change to what Backlog may edit, and the acceptance is still reviewable by
  a team because it is in the Development PR. The decision is made when it matters, together with the Development
  effort, so it cannot go stale. Its cost is one guard: `check` must treat `dev-<slug>` like `plan-<slug>`.
- **A** is the working direction of the draft. It lets the user decide during a Backlog pass and leaves the draft
  `accepted` for any later Development, but it needs the 03 §4 carve-out and turns every directly accepted draft into
  an in-progress Unit immediately. It is the better choice only if the user wants to decide acceptance in bulk during
  Backlog, separately from starting the work.
- **C** keeps the semantics most literal but costs a new handoff variant, a depth marker and an exception to the
  lowering rule; rejected unless the user prefers to remove the notion of accepting without review.

## Eligibility (Q1)

Mechanical, checked by the tool: `status: draft`; `gate:plan-intent` accepted; no `needs_decompose: true`; no local or
fetched `plan-<slug>`; `task_kind` valid; no `supersedes` (a supersede reverses an earlier `plan-accept`, and
`classification.md` §4 makes such a draft run Planning anew); not on a branch other than `dev-<slug>` (option B).

Judgment, by the Host and shown to the user: the direction leaves nothing to compare (the Host would propose
`planning_effort: low` and has no question), the body has no open spike question, and the draft is not a depth
escalation carrying a failed attempt's material. No size limit: depth is not size (01 §2.2), and the user's explicit
decision is the safeguard.
