# Choose the next repository work

Use this procedure only when no Unit is in progress. In progress means a local or fetched plan-/dev- branch for its
slug, a reviewing/accepted proposal, or an incomplete spec; queued drafts are not in progress. Never resume another
task merely because its branch exists.

Milestones are global: consider queued drafts across all namespaces and keep the namespace in the recommendation.

1. Query `devkit spec list proposal --all-namespaces -n 0` and `devkit spec list milestone --all-namespaces -n 0`.
   - Read frontmatter for ordering fields the output omits.
   - Use the displayed proposal status: a base draft with a Planning branch displays reviewing.
2. Apply the direct unit prerequisite procedure below to every candidate, including critical drafts, before ranking.
   - Eligible drafts are unit-ready, have displayed status draft and no true `needs_decompose`.
   - A milestone is ready when every ID in depends_on is done or dropped. Use `--history` or resolve dependencies
     individually; never assume a hidden dependency is absent or ready.
   - Invalid/missing/ambiguous dependencies are Backlog actions.
3. Order eligible drafts by enum rank, not text:
   - Critical drafts first, whatever their milestone, with the remaining tie-breaks inside that group; their milestone
     states order active, ready planned, no milestone, unready planned, done, dropped.
   - Then milestone groups: active, ready planned, then no milestone; milestones of the same rank by created_at,
     then ID.
   - Within a group: priority critical/high/medium/low, size S/M/L/XL, draft created_at, draft ID. Missing
     priority/size use the scaffold defaults high/M; missing created_at sorts after dated peers, then by ID.
4. Recommend the first eligible draft.
   - Without a recorded plan-intent, record an existing explicit task instruction; ask only when intent is unresolved.
   - Offer Planning, or a direct acceptance when its direction is settled
     (`devkit spec proposal accept <slug> --by user --direct --check --note "<reason>"` first), and for `session`-depth
     work the session reclassification at pickup (the `spec` skill's `references/backlog.md`). The user chooses.
   - Report noncritical drafts in unready/done/dropped milestones and needs_decompose drafts as Backlog actions.
   - Mention open feedback as a candidate hygiene pass.
   - Do not start, accept or activate anything automatically.
5. Count done milestones (milestone history). At three done milestones or on/after 2027-01-31, whichever occurs first,
   report roadmap review due until an ADR-roadmap-review document exists.
   - In that review, Backlog reviews actual milestone use and warning value, records its decision, and proposes
     removing unused machinery.
   - It is a reminder, never a gate. Use the session's current date.

## Direct unit prerequisite procedure

Use this procedure for idle recommendations, explicit proposal pickup and direct-spec intake. Direct-spec intake and
explicit pickup inspect these same fields even when idle recommendation is not running.

Dependencies are optional frontmatter, for example `depends_on: [PROP-foundation, SPEC-parser]`; omit the field when
empty. The procedure adds no creation flag, readiness command, delivery certification, gate or hard readiness refusal.

1. Identify the local base ref from the current worktree policy.
   - Resolve it once with `git rev-parse <base>` and report the base ref and commit.
   - Read candidates and target anchors from that same commit with `git ls-tree -r --name-only <commit> -- docs specs`
     and `git show <commit>:<path>`, across all namespaces and completed history.
   - Do not fetch implicitly or claim remote freshness.
   - Never substitute completion found only on an activity branch.
2. Inspect each direct depends_on edge.
   - Only an exact ID resolving to one SPEC anchor with status completed in that snapshot is satisfied.
   - Do not recursively reopen prerequisites of a completed SPEC.
   - No dependencies means unit-ready.
   - This is a status-based scheduling signal, not verification of tasks, reconciliation, approvals or outcome
     coverage.
3. Report each blocked candidate and its exact prerequisite ID with the reason.
   - Reasons: unfinished proposal, rejected proposal, unfinished spec, or invalid/unknown target.
   - Missing, ambiguous, malformed or unreadable base evidence is a Backlog repair action; a hidden history target is
     not missing.
   - A critical blocked draft stays blocked.
   - Apply the existing milestone readiness and critical-priority milestone exception only to unit-ready drafts.
4. Explicit user pickup can override order: show the unsatisfied IDs and reasons and record the chosen override in the
   ordinary intent decision.
   - The override cannot waive malformed references or cycle diagnostics.

## Milestone close review

- After known associated work finishes, you MAY offer the existing Backlog
  [milestone completion review](../../spec/references/milestone-completion.md).
- Never close silently after integration; never infer completion from empty membership or handoff.
- The user confirms decomposition and direct work settlement on one current candidate. After an interruption,
  recheck its facts; an unchanged approval persists.
