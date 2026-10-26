---
id: PADR-apply-behavior-preserving-batches-as-direct-mode-refactors
title: Apply behavior-preserving batches as direct-mode refactors
summary: For applying a batch's agreed behavior-preserving changes, we route it as a direct-mode refactor whose subagents edit within the batch scope under the playbook agent's validation, to apply consolidations at refactor cost, accepting checks the agent re-runs per edit.
proposal: PROP-review-refactor
status: draft
created_at: 2026-10-26
---

# [PADR-apply-behavior-preserving-batches-as-direct-mode-refactors] Apply behavior-preserving batches as direct-mode refactors

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

The changes a review-refactor run applies are refactoring, not feature development (`user`): consolidations and
reductions that add no behavior and usually span many files across several modules. Routing each work item through
the feature development workflow adds a Unit, planning and development workers and their records for work whose
direction the decision round has already settled. A refactor inside one feature or module, however, follows the
feature workflows in a repository that separates the two (devkit's overall-refactor workflow says so). A broad pass
is parallelizable, but parallel subagents over-report, and editing subagents can drift beyond the agreed change or
into each other's files.

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
  refactor across several areas (with the `spec` bundle, `sdd-overall-refactor`), because the decision round has
  settled its direction and the work is a refactor.
- The work item is a single-module refactor when every path its agreed changes edit, apart from the edits that
  follow a change, lies inside one feature or module of the repository's declared layout; it then follows the
  feature workflow at the depth the repository's own classification gives it, because that is the repository's own
  boundary. The playbook's agent applies the test once per work item, states the route and the edited paths in the
  decision round and never splits or merges a work item to change its route. Without a declared layout, the
  decision round names the route and the user's approval settles it.
- Direct mode: the playbook's agent works with the user, with no planning or development worker and no Unit. It
  splits the work item and uses general subagents for parallel edits, drafting and research when useful and the host
  supports them; otherwise it performs the same steps itself, because parallel edits shorten broad passes.
- A subagent applies only agreed edits inside an explicit write scope the playbook's agent assigns, within the
  batch's write scope and disjoint from every concurrent subagent, and never commits. The playbook's agent checks
  each result against the diff; an edit outside the scope or beyond the agreed change is not committed, because the
  agreed change is the only authority.
- A subagent's review or verification result is an evidence-backed opinion: the playbook's agent validates it against
  the code or diff at the cited location, re-runs the commands of a verification or negative-reachability claim
  before recording it, and counts a root as covered only when the result lists what was read, because parallel review
  must not weaken evidence. Subagents never ask the user, approve a change or write the run's records.
- The playbook's agent commits one change per checkpoint, runs the repository's full verification on the work item's
  final head, starts an independent code reviewer at the run's activity effort, reports in the final response and the
  commit body, and integrates with task kind `overall-refactor`, because these are the overall-refactor workflow's
  verification, review, report and integration steps. The decision round never supplies the integration approval.
- Contract removals stay outside this route
  (`PADR-apply-approved-contract-removals-as-separate-work-items`).

## 5. Consequences

- Positive: consolidations across many files are applied in one reviewed work item per batch, in parallel, without
  Unit overhead.
- Negative: the playbook's agent checks every subagent diff and re-runs verification claims; the work item carries
  no Unit record, so its evidence lives in the run report and the commit bodies.
- Risk: a subagent edit drifts beyond the agreed change; the disjoint scopes, the diff check and the independent
  review bound it. A single-module test applied to a layout the repository does not declare misroutes; the decision
  round names the route so the user can correct it.
- Follow-up: none.

## 6. Confirmation

- Spec-review checklist of the Development maps the route, the single-module test, direct mode, the subagent write
  scopes and diff check, the subagent review rules, commits, full verification, review, report and integration to
  playbook sections.
- Fixture exercise records the route decision and at least one subagent edit with its diff check when the host
  supports subagents (proposal section 3).
