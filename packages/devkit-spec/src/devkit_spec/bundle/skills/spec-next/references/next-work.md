# Choose the next repository work

Use this procedure only when no Unit is in progress (a local or fetched plan-/dev- branch for its slug, a
reviewing/accepted proposal, or an incomplete spec; queued drafts are not in progress). Never resume another task
merely because its branch exists.

1. Query `devkit spec list proposal --all-namespaces -n 0` and `devkit spec list milestone --all-namespaces -n 0`.
   Read frontmatter for ordering fields the output omits and use the displayed proposal status (a base draft with a
   Planning branch displays reviewing).
2. Eligible drafts have displayed status draft and no true `needs_decompose`. A milestone is ready when every ID in
   depends_on is done or dropped; use `--history` or resolve dependencies individually, never assume a hidden
   dependency is absent or ready. Invalid/missing/ambiguous dependencies are Backlog actions.
3. Order eligible drafts by enum rank, not text:
   - Critical drafts first, whatever their milestone, with the remaining tie-breaks inside that group; their milestone
     states order active, ready planned, no milestone, unready planned, done, dropped.
   - Then milestone groups: active, ready planned, then no milestone; milestones of the same rank by created_at,
     then ID.
   - Within a group: priority critical/high/medium/low, size S/M/L/XL, draft created_at, draft ID. Missing
     priority/size use the scaffold defaults high/M; missing created_at sorts after dated peers, then by ID.
4. Recommend the first eligible draft; without a recorded plan-intent, recommend confirming intent first. Offer
   Planning, or a direct acceptance when its direction is settled (`devkit spec proposal accept <slug> --by user
   --direct --check` first), and for `session`-depth work the session reclassification at pickup (the `spec` skill's
   `references/backlog.md`); the user chooses. Report
   noncritical drafts in unready/done/dropped milestones and needs_decompose drafts as Backlog actions. Mention open
   feedback as a possible hygiene pass. Do not start, accept or activate anything automatically.
5. Count done milestones (milestone history). At three done milestones or on/after 2027-01-31, whichever occurs first,
   report roadmap review due until an ADR-roadmap-review document exists: Backlog reviews actual milestone use and
   warning value, records its decision, and proposes removing unused machinery. A reminder, never a gate; use the
   session's current date.

Milestones are global: consider queued drafts across all namespaces and keep the namespace in the recommendation.
