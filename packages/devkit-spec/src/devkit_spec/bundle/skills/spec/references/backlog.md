# Repository Backlog

Backlog uses repository documents only: goals in ARCH-01, milestones under `docs/roadmap/`, queued requests as draft
proposals, and follow-ups as feedback. No external tracker is involved.

## Requests and decomposition

- Classify requests in `direct` mode. Start immediate `session`/`spec` work through inline Planning; keep every
  request not starting now as a draft proposal, including small work. A draft whose direction is settled may be
  accepted directly (below); otherwise Planning runs at its effort. Follow the draft's explicit intent gate first.
- Run `devkit spec proposal check <slug>` (fetch first, within existing network authorization) before editing,
  splitting or deleting a draft. An existing local or fetched `plan-<slug>` means Planning owns it: stop on
  `SPEC_PROPOSAL_IN_PLANNING` and do not edit the base copy. A `reviewing` listing is no check.
- Review open feedback; a repository-owned item selected for work is promoted through feedback hygiene into a draft,
  optionally assigned a milestone. Preserve its destination and avoid duplicate drafts.
- Decompose into drafts only: `devkit spec proposal new <child> --decomposed-from PROP-<parent>` checks the original
  is an editable draft. Preserve the parent's milestone with `--milestone MS-<slug>` when set; choose each child's
  effort hints afresh. Preserve open feedback ([feedback retirement](feedback-retirement.md)) before deleting the
  parent in the same commit.
- Backlog edits and milestone changes are outside Planning/Development worktree and PR requirements. Commit only
  their agreed files in the current checkout; preserve unrelated changes. A direct acceptance and a reclassification
  deletion commit only on the base checkout, once you settled that you can push to the base (or that there is no
  remote); a protected base keeps the draft on Planning. Undo a stranded commit with `git revert`, never a reset.

## Return from Planning for decomposition

When Planning discovers a split is needed, its executor follows [Planning](planning.md): preserve evidence in
`materials/`, set `status: draft` and `needs_decompose: true`, close every open question with an answer recording
that Planning returned to Backlog, and commit the return with the run's records. Do not create children on the
Planning branch or retry `--decomposed-from` there.

The Host then checks the committed return and obtains explicit user authorization to merge that return and
perform cleanup under the existing Git policy. For a local merge, use `devkit worktree finish plan-<slug> --merge
--local-only` from the base after preparing the branch and clearing envelope holds; use the required PR path when
policy requires it. The MCP unit integration path requires an accepted proposal and cannot integrate this draft
return. Do not manufacture `plan-accept` to satisfy that readiness check. This is a return of a draft, not `plan-accept` or authorization to
implement the old proposal. Preserve the committed return on the base before removing the local Planning branch
and worktree. A fetched remote Planning branch also blocks Backlog: coordinate its authorized remote removal and
refresh/prune the fetched ref under existing network authority; do not hide a live remote branch by deleting only
its tracking ref. If authorization or branch cleanup is pending, keep the return pending and do not decompose.

On the base, run `devkit spec proposal check <slug>` again. Only after it passes may Backlog create the children
with `--decomposed-from`, preserve source feedback and retire the parent as described above. `status: draft` alone
is insufficient while a local or fetched Planning branch exists. This procedure adds no merge, push or deletion
permission and gives workers no additional Git actions.

## Direct acceptance

An eligible draft may skip Planning on the user's explicit `plan-accept` (`ADR-eligibility-for-direct-acceptance`,
`ADR-direct-acceptance-command-and-handoff-guard`). Never propose it silently; the user may always choose Planning.

1. In the base checkout run `devkit spec proposal accept <slug> --by user --direct --check --note "<reason>"`; a
   refusal names each failed condition, and a missing intent shows as `pending=gate:plan-intent`.
2. Judge the direction yourself: nothing to compare, no open spike question, not a depth escalation carrying a
   failed attempt's material. Otherwise propose Planning, with the reason.
3. The request shows "Planning: skipped (direct acceptance)", the eligibility reason, `task_kind` (which `plan-accept`
   confirms), the recorded `planning_effort` hint (not `low`: why Planning is skipped anyway), the PADRs the handoff
   will promote and the `dev_effort` you reviewed against the settled direction; under `pull_request = required`, that
   the direction gets no PR review. Without a recorded intent the same request may ask `plan-intent` too, each
   decision named in full and answered explicitly; neither is inferred from the other.
4. On the user's acceptance: record a pending `plan-intent` (`devkit workflow answer --by user`), sweep this session
   at `collect-feedback` under the project's sweep policy (`spec-feedback`; zero observations is a valid PASS), then
   run `devkit spec proposal accept <slug> --by user --direct --note "<reason>"` and commit it all in one Backlog
   commit. No run, `activity-effort` or `worker` envelope. Intent only: no sweep; commit the draft with its intent for
   Planning. A refusal after the sweep: remove the sweep envelope before committing.

Development then hands off as for any accepted proposal. `SPEC_PROPOSAL_ACCEPTANCE_UNRECORDED` at handoff goes to the
user: without a `worker` envelope, on the user's acceptance, repair it on the base with the same `--direct` command
and merge the base into `dev-<slug>`; with one, on the user's decision revert the whole Planning merge to `draft`.

## Session reclassification of a queued draft

When the user picks a queued draft whose work meets the `session` criteria ([classification](classification.md) §1),
you may propose doing it as a `session` task, with the reason; only the user's explicit decision allows it
(`ADR-session-reclassification-of-a-queued-draft`), never a worker or Cloud Agent. It needs push access to the base,
a passing `devkit spec proposal check <slug>` (fetch first), no `PADR-*.md` in `decisions/`, and no
`needs_decompose`, `supersedes` or depth escalation. The request names what goes: the draft and its gate records, its
materials (kept in Git history), its `milestone` membership (review that milestone's exit condition) and the open
feedback preserved. Delete it in one Backlog commit on the base, preserving open feedback and striking through
incoming references ([feedback retirement](feedback-retirement.md)), with the message "depth proposal -> session on
the user's decision: <reason>", and name the commit to the user at once. The session takes a new slug, starts
through inline Planning and names the deletion commit in its final report; one that never integrates is undone by
`git revert` of that commit, on the user's decision.

## Milestone documents and user decisions

Use `.devkit/managed/spec/templates/milestone.md` for a global `docs/roadmap/MS-<slug>.md` document. Slugs start with a
word, for example MS-release-1-0. Required metadata is id, title, English summary, status and created_at; optional
`depends_on` lists milestone IDs. Body: the goal it advances (cite ARCH-01), exit condition and non-goals. Do not
duplicate work lists: proposal/spec anchors own the optional `milestone` field; use `refs --direction in`.

Status is planned, active, done or dropped; several milestones may be active. A milestone is ready when all
dependencies are done or dropped. Cycles are rule errors; the user may activate one out of order.

Every transition is the user's decision, with a concrete candidate prepared first:

1. Activate: show each dependency not done/dropped; the user may still activate it.
2. Close: inspect anchor members on the base and each relevant `plan-`/`dev-` branch, including branches that introduce
   members absent from the base. Reuse registered worktrees or read Git refs without switching another task's checkout.
   Reconcile duplicate slugs across proposal and handed-off spec views. Propose close only after exit conditions
   hold and unsettled members are moved elsewhere or the close waits. Unavailable branch evidence prevents a claim
   that all work is settled.
3. Drop: show unsettled members and dependent successor milestones. Prepare member reassignment, clearing milestone
   or proposal rejection; show each successor so the user keeps or changes its dependencies.

Hygiene reads base facts only: `SPEC_MILESTONE_DONE_UNSETTLED` and `SPEC_MILESTONE_DROPPED_UNSETTLED` name unsettled
members left on finished milestones until they are completed or reassigned/cleared/rejected.
