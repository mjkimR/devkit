---
id: ADR-apply-behavior-preserving-batches-as-direct-mode-refactors
title: Apply behavior-preserving batches as direct-mode refactors
summary: For applying a batch's agreed behavior-preserving changes, we route it as a direct-mode refactor whose subagents edit within the batch scope under the playbook agent's validation, to apply consolidations at refactor cost, accepting checks the agent re-runs per edit.
proposal: SPEC-review-refactor
status: superseded
created_at: 2026-10-26
superseded_by: ADR-apply-review-refactor-changes-in-parallel-checkouts
---

# [ADR-apply-behavior-preserving-batches-as-direct-mode-refactors] Apply behavior-preserving batches as direct-mode refactors

- **Status**: Superseded by `ADR-apply-review-refactor-changes-in-parallel-checkouts`
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

The changes a review-refactor run applies are refactoring, not feature development (`user`): consolidations and
reductions that add no behavior and usually span many files across several modules. Routing each work item through
the feature development workflow adds a Unit, planning and development workers and their records for work whose
changes the decision round has already agreed. `ADR-overall-refactor-workflow` applies the direct-only
overall-refactor workflow to a behavior-preserving restructuring of several areas whose direction settles while the
work proceeds, and keeps a refactor inside one feature or module on the feature workflows. It names no maintenance
playbook run, so without a stated refinement a multi-module work item of the run reads as feature work at `spec`
depth. The playbook must also run in a repository without the `spec` bundle. A broad pass is parallelizable, but
parallel subagents over-report, and editing subagents can drift beyond the agreed change, into each other's files or
into each other's verification.

## 2. Decision Drivers

- Agreed behavior-preserving changes are applied at the cost of a refactor, not of a feature delivery.
- The route follows the target repository's own boundary between a cross-area refactor and a single-module one.
- Parallel review and editing shorten a broad pass without weakening evidence or authority.
- Every applied edit stays inside the agreed change and its batch's write scope.

## 3. Considered Options

- **Route**: the repository's overall-refactor workflow in direct mode, with the single-module test sending a
  one-module work item to the feature workflows (refactor cost; needs the test); the feature development workflow
  for every work item (Unit and worker records per batch for settled work); a fixed route regardless of module span
  (contradicts the repository's own boundary).
- **Subagents**: read-only review and verification, with the routed workflow applying every change (no edit drift,
  but no parallel edits); editing subagents with explicit disjoint write scopes and a diff check by the playbook's
  agent (parallel edits, a check per edit); the playbook's agent alone (slow on broad scope).

## 4. Decision Outcome

- A batch's behavior-preserving work item follows the target repository's workflow for a behavior-preserving
  refactor across several areas (with the `spec` bundle, `sdd-overall-refactor`). This refines the applicability of
  `ADR-overall-refactor-workflow`: a review-refactor run is a restructuring pass whose direction settles batch by
  batch in the conversation with the user, as that ADR's first driver describes, so a work item of the run spanning
  more than one module is overall-refactor work even though its batch's decision round agreed its changes.
- The work item is a single-module refactor when every source file its agreed changes edit, including call sites,
  imports and re-exports, lies inside one feature or module of the repository's declared layout; only following
  edits (tests of the changed code and non-code text naming it) are left out. It then follows the feature workflow at
  the depth the repository's own classification gives it, because that ADR keeps such refactors on the feature path.
  The playbook's agent applies the test once per work item, states the route and the edited paths in the decision
  round and never splits or merges a work item to change its route. Without a declared layout, the decision round
  names the route and the user's approval settles it.
- The batch's write scope is the edited paths the decision round states for its agreed changes, including their
  following edits, so every edit has a stated bound.
- Direct mode: the playbook's agent works with the user, with no planning or development worker and no Unit, on the
  work item's own branch, never directly on the base branch. It splits the work item and uses general subagents for
  parallel edits, drafting and research when useful and the host supports them; otherwise it performs the same steps
  itself, because parallel edits shorten broad passes. Without a refactor workflow in the repository these steps are
  the procedure as stated, because the playbook is self-contained.
- A subagent applies only agreed edits inside an explicit write scope the playbook's agent assigns, a subset of the
  batch's write scope disjoint from every concurrent subagent, and never commits. Parallel editing subagents work on
  the same change; changes are applied, verified and committed one after another on the previous checkpoint, because
  each change's evidence must describe only that change. The playbook's agent checks each result against the diff
  and reverts a rejected edit hunk by hunk, never resetting a path another scope owns, because the agreed change is
  the only authority and another subagent's edits must survive.
- A subagent's review or verification result is an evidence-backed opinion: the playbook's agent validates it against
  the code or diff at the cited location, re-runs the commands of a verification or negative-reachability claim
  before recording it, and counts a root as covered only when the result lists what was read, because parallel review
  must not weaken evidence. Subagents never ask the user, approve a change or write the run's records.
- The playbook's agent commits one change per checkpoint with only that change on top of the committed work, runs the
  repository's full verification on a clean tree at the work item's final head, has the diff reviewed by a fresh
  reviewer subagent (otherwise a self-review recorded as such) at the repository's review effort where one is
  defined, reports every breaking change with the rest of the report in the final response and the commit body, and
  integrates only after the report through the repository's integration path and its own integration approval (with
  the `spec` bundle, task kind `overall-refactor`), because these are the overall-refactor workflow's verification,
  review, report and integration steps. The decision round never supplies the integration approval.
- Contract removals stay outside this route
  (`ADR-apply-approved-contract-removals-as-separate-work-items`).

## 5. Consequences

- Positive: consolidations across many files are applied in one reviewed work item per batch, in parallel, without
  Unit overhead.
- Negative: the playbook's agent checks every subagent diff and re-runs verification claims; the work item carries
  no Unit record, so its evidence lives in the run report and the commit bodies.
- Risk: a subagent edit drifts beyond the agreed change; the disjoint scopes, the diff check and the independent
  review bound it. A single-module test applied to a layout the repository does not declare misroutes; the decision
  round names the route so the user can correct it.
- Follow-up: the `spec` bundle's classification criteria name no maintenance-playbook case; when this PADR is
  promoted, the Host records the alignment of `packages/devkit-spec` classification text as feedback, since this
  proposal's boundaries exclude it.

## 6. Confirmation

- Spec-review checklist of the Development maps the route, the single-module test, the batch write scope, direct
  mode and its branch, the subagent write scopes, sequential changes, the diff check and hunk revert, the subagent
  review rules, commits on a clean tree, full verification, review and its fallback, the report with breaking changes
  and integration after its own approval to playbook sections.
- Fixture exercise records the route decision and at least one subagent edit with its diff check when the host
  supports subagents (proposal section 3).
