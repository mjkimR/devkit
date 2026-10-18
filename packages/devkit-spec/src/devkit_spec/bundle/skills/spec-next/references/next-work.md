# Choose the next repository work

Use this procedure only when no Unit is in progress. A Unit is in progress if its slug has a local or fetched
plan-/dev- branch, is a reviewing/accepted proposal, or is an incomplete spec. Queued drafts are not in progress.
Follow the active Unit's workflow first; never resume another task merely because its branch exists.

1. Query `devkit spec list proposal --all-namespaces -n 0` and `devkit spec list milestone --all-namespaces -n 0`.
   Follow pagination when a bounded query is used. Read frontmatter for ordering fields the output omits and use
   displayed proposal status (a base draft with a Planning branch displays reviewing).
2. Eligible drafts have displayed status draft and no true `needs_decompose`. A milestone is ready when every ID in
   depends_on is done or dropped; use `--history` or resolve dependencies individually. Do not assume a hidden
   dependency is absent or ready. Invalid/missing/ambiguous dependencies are Backlog actions.
3. Order eligible drafts as follows, applying enum ranks rather than text sorting:
   - Critical drafts first, whatever their milestone. Apply the remaining tie-breaks within that group too.
   - Milestone groups: active, ready planned, then no milestone. Within the same milestone rank order milestones by
     created_at, then ID. Critical drafts with otherwise excluded milestone states remain in the critical group;
     use the explicit state order active, ready planned, no milestone, unready planned, done, dropped for their ties.
   - Within a milestone group: priority critical/high/medium/low, size S/M/L/XL, draft created_at, draft ID.
   Missing priority/size use the scaffold defaults high/M; missing created_at sorts after dated peers, then by ID.
4. Recommend the first eligible draft. Without a recorded plan-intent, recommend confirming intent first. Report
   noncritical drafts in unready/done/dropped milestones and needs_decompose drafts as Backlog actions, not runnable
   Planning recommendations. Mention open feedback as a possible hygiene pass; critical feedback still takes
   precedence per the entry skill. Do not start, accept or activate anything automatically.
5. Query milestone history and count done milestones. At three done milestones or on/after 2027-01-31, whichever
   occurs first, report roadmap review due until an ADR-roadmap-review document exists. Backlog reviews actual
   milestone use and warning value, records its decision, and proposes removing unused machinery. This is a reminder,
   never a gate. Use the current date of the session; no network call is needed.

Sorting belongs to this skill, not a CLI sorting option. Milestones are global; consider queued drafts across all
namespaces and preserve namespace information in the recommendation.
