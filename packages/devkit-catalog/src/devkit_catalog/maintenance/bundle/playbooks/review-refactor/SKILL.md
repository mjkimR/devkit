---
name: review-refactor
description: Manually run a review and refactoring pass over user-selected code, agent guidance or CLI command roots that consolidates duplicated logic and removes unneeded code, guidance, options and commands with preservation evidence, one decision round per surface batch.
---

# Review and refactor

Run only when the user invoked or confirmed this playbook (`devkit-playbook`, `devkit playbook get
maintenance/review-refactor` or a confirmed intake offer); selection never executes it. The outcome is a smaller
surface: consolidation and reduction come first, detection and repair second. Invocation, an external runner naming
this playbook and a clean check authorize no change. Only the user's decision round does: an unattended run stops at
the decision round with nothing applied.

This playbook targets maintenance cost in code that agrees with its contract. Record a mismatch against agreed
documentation as a deferred finding whose follow-up names drift reconciliation; never invoke another playbook, the
user may start drift reconciliation as a separate invocation.

## 1. Intake and batches

1. Record the run ID, a credential-free repository identity, HEAD, dirty paths, prior reports and the report
   destination: the owning work unit's materials, else the repository's materials location, as an ordinary local
   file.
2. Have the user select the surfaces (`code`, `guidance`, `cli`) and the roots of each. Clarify missing scope before
   inspecting anything.
3. Split the run into batches of one surface each. Each batch gets its own review and its own decision round.
4. Assign a finding that spans surfaces to the batch of the surface where its change lands, citing both sides.
   - If its landing surface is not selected, record it as deferred with a follow-up and apply nothing.
   - If the user adds that surface, record the addition in the report, clarify its roots as at intake and give it
     its own batch and decision round.
5. Treat following edits as part of the change on any surface, never as cross-surface findings: the tests of the
   changed code and non-code text naming it (documentation, guidance, the statement of the result in the
   repository's specification). Call sites, imports and re-exports are source edits of the change itself.
6. Never edit receipt-owned files (`.devkit/managed/`, agent projections): read them as evidence, and send a finding
   or following edit against them to the source bundle, an upstream follow-up or `devkit override`.

## 2. Review a batch

Read `references/criteria.md` before reviewing; it holds the review questions per surface, the dispositions and the
evidence each change needs.

1. Inventory the batch roots and list candidates against the review questions of the batch's surface.
2. Use tool output (clone detectors, dead-code finders, unselected lint rules) as candidates only; run what is
   installed and install nothing without asking.
3. When useful and the host supports subagents, split the review across subagents (for example one per root or
   module, or an independent check of a proposed consolidation or removal); otherwise run the same steps yourself.
   You keep the coordination, the decision round and the records.
   - Treat a subagent result as an evidence-backed opinion. Check it against the code or the diff at the cited
     location before it enters the decision round or a change record; drop an unconfirmed claim or record it as a
     coverage gap.
   - Re-run the commands of a verification or negative-reachability claim before recording it, and record the
     commands and their results.
   - Count a root as covered only when the result lists what the subagent read; otherwise record a coverage gap.
   - Subagents never ask the user, approve a change or write the run's records.

## 3. Record findings

Per finding, record a report-local key; the location at the recorded revision, dirty content included; the review
question it answers; the maintenance cost it causes (what a future change must repeat, read or keep consistent);
the proposed disposition; and the evidence command or reading. Drop a candidate without a named cost and count it in
the coverage. AI origin and line count are never findings by themselves.

Search open follow-ups (feedback, proposals, issues) before creating one; reuse a match and link earlier report keys.
On a repeat run, recheck the earlier dispositions.

## 4. Decision round

When the batch proposes changes, read `references/applying.md` §1 first. Present all findings of the batch
together, each with its location, cost, proposed disposition and, for changes, the route, the edited paths and the
write scope that §1 defines. Record each decision with its
reason and provenance.

| Disposition | Record and next action |
| --- | --- |
| Consolidate, reduce or remove with behavior preserved | Joins the batch's behavior-preserving work item; preservation evidence per change. |
| Contract change | Its own work item through the repository's normal development workflow. |
| Defer | Reason, follow-up destination (existing or newly created) and restart condition. |
| Keep | The reason the cost is accepted. |

- Present a consolidation of implementations that do not behave identically with each difference and the behavior
  it keeps (`references/criteria.md` §2); the user's decision covers each difference.
- Leave an unanswered finding pending; nothing is applied for it.
- The user's approval in the round is the recorded intent (goal, scope and non-goals) of the routed work item. It
  never supplies the work item's integration approval.
- In an exercise, label decisions as simulated; they change only the fixture.

## 5. Apply agreed changes

When the round approved changes, read the rest of `references/applying.md` and follow it. If HEAD or a relevant dirty path moved
since intake, revalidate the evidence first, and take a change whose intent shifts back to the decision round.

## 6. Report and completion

Recheck HEAD and dirty paths, then write the report:

- Intake: run ID, repository identity, intake revision and dirty state, surfaces, roots and scope additions.
- Coverage per batch: roots reviewed, excluded with reason, coverage gaps, candidates dropped for lacking a named
  cost.
- Findings and changes as separate records. Each change names its finding, preservation evidence, resulting commit,
  line or token delta (reported, never the justification) and any inputs or callers no longer accepted.
- Behavior changes: the approved differences of consolidations, each with its change, recorded apart from the inputs
  or callers no longer accepted.
- Decisions with provenance, follow-ups, and counts: found, applied, contract work items, deferred, kept, pending.
- Outcome: `stopped at decision round`, `applied` or `partially applied`, with the work items' integration state.
  Update it once each work item integrates or stops.

Claim a batch complete only with no pending decision and every agreed change committed or routed. A zero-finding
batch still names its coverage and gaps. Never claim the whole repository reviewed from a batch.
