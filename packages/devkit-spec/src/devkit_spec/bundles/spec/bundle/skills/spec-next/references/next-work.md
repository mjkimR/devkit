# Choose the next repository work

Use this when no Unit is in progress (a fetched plan-/dev- branch for the slug also counts). Never resume a task only
because its branch exists. Recommend; do not start, accept or activate anything.

1. Run `devkit docs list proposal --all-namespaces -n 0` and `devkit docs list milestone --all-namespaces -n 0`; read
   frontmatter for ordering fields the output omits. Keep each draft's namespace in the recommendation.
2. Apply the [direct unit prerequisite procedure](#direct-unit-prerequisite-procedure) to every candidate, including
   critical drafts. Eligible: unit-ready, displayed status `draft`, no true `needs_decompose`, and `size` absent or
   exactly `S`, `M` or `L`. A milestone is ready when every `depends_on` ID is done or dropped; resolve hidden ones
   with `--history` from the root or the reserved `_archive/` location, never assume them. Resolve the complete
   milestone set before filtering history.
3. Rank eligible drafts by enum, not text:
   1. Critical drafts first, whatever their milestone, by milestone state: active, ready planned, none, unready
      planned, done, dropped.
   2. Then milestone groups: active, ready planned, none; ties by milestone `created_at`, then ID.
   3. Within a group: priority critical/high/medium/low (default high), size S/M/L/XL (default M), draft
      `created_at` (missing sorts last), draft ID.
4. Recommend the first eligible draft: record an existing explicit task instruction as plan-intent (ask only when
   intent is unresolved), and offer Planning, a direct acceptance
   (`devkit spec proposal accept <slug> --by user --direct --check --note "<reason>"`) when its direction is settled,
   or a session reclassification for `session`-depth work (the `spec` skill's `references/backlog.md`). Report as
   Backlog actions: other drafts in unready/done/dropped milestones, `needs_decompose` and `XL` drafts (decompose
   first with the `decomposer`: [XL size gate](../../spec/references/backlog.md#the-xl-size-gate)) and invalid dependencies.
5. When a milestone's known work has finished, offer the
   [milestone completion review](../../spec/references/milestone-completion.md); never close one silently.

## Direct unit prerequisite procedure

Also used for explicit proposal pickup and direct-spec intake. The result schedules work; it is no gate or refusal.

1. Resolve the local base once (`git rev-parse <base>`) and report the base ref and commit. Read candidates and
   anchors from that commit only (`git ls-tree -r --name-only <commit> -- docs specs`, `git show <commit>:<path>`).
   Do not fetch implicitly. Never substitute completion found only on an activity branch.
2. A direct `depends_on` edge is satisfied only by an exact ID resolving to one SPEC with `status: completed` in that
   snapshot. No dependencies means unit-ready. Do not recursively reopen a completed SPEC's prerequisites.
3. Report each blocked candidate with the prerequisite ID and reason (unfinished proposal, rejected proposal,
   unfinished spec, invalid/unknown target). Missing, ambiguous or malformed evidence is a Backlog repair action. A
   critical blocked draft stays blocked.
4. Explicit user pickup can override order: show the unsatisfied IDs and record the override in the intent
   decision. It cannot waive malformed references or cycles.
