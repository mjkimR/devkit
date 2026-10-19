# Repository Backlog

Backlog uses repository documents only: goals in ARCH-01, milestones under `docs/roadmap/`, queued requests as draft
proposals, and follow-ups as feedback. No external tracker is involved.

## Requests and decomposition

- Classify requests in `direct` mode. Start immediate `session`/`spec` work through inline Planning; keep every
  request not starting now as a draft proposal, including small work. Until direct acceptance exists, small drafts
  use Planning at `low` effort. Follow the draft's explicit intent gate before starting Planning.
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
  their agreed files in the current checkout; preserve unrelated changes.

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
