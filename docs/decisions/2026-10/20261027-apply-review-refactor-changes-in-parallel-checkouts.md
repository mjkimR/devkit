---
id: ADR-apply-review-refactor-changes-in-parallel-checkouts
title: Apply review-refactor changes in parallel isolated checkouts
summary: "For applying a review-refactor batch's agreed changes, we route it as a direct-mode refactor and run disjoint-scope edits concurrently in prepared isolated checkouts, committed one change at a time, to finish broad passes fast with per-change evidence, accepting setup cost and serial transfer."
spec: SPEC-review-refactor-lessons
status: accepted
created_at: 2026-10-27
supersedes: ADR-apply-behavior-preserving-batches-as-direct-mode-refactors
---

# [ADR-apply-review-refactor-changes-in-parallel-checkouts] Apply review-refactor changes in parallel isolated checkouts

- **Status**: Accepted; supersedes `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`
- **Date**: 2026-10-27
- **Deciders**: @minjae
- **Involved Components/Capabilities**: `maintenance/review-refactor` playbook (`packages/devkit-catalog`),
  `CAP-DLV-review-refactor`, `UC-review-and-refactor-accumulated-slop`

---

## 1. Context & Problem Statement

The changes a review-refactor run applies are behavior-preserving consolidations and reductions that usually span
many files across several modules; routing them through the feature development workflow adds a Unit, workers and
records for changes the decision round has already agreed. `ADR-overall-refactor-workflow` sends a cross-area
restructuring to the direct-only overall-refactor workflow and keeps a refactor inside one module on the feature
workflows. The playbook must also run in a repository without the `spec` bundle.

`ADR-apply-behavior-preserving-batches-as-direct-mode-refactors` applied, verified and committed changes one after
another on the previous checkpoint, so each commit's evidence describes only its change. On a broad pass with many
independent changes this is too slow: the user ran disjoint changes in parallel checkouts outside the written
procedure. Without a stated procedure those runs used checkouts without synchronized managed assets (one change was
committed without its commit checks), moved results by hand, and editing subagents added import exceptions to make
their change pass. Parallel subagents also over-report, and editing subagents can drift beyond the agreed change or
into each other's files and verification.

## 2. Decision Drivers

- Agreed behavior-preserving changes are applied at the cost of a refactor, not of a feature delivery.
- The route follows the target repository's own boundary between a cross-area refactor and a single-module one.
- A broad pass finishes in a fraction of the sequential time.
- Every commit holds one change with its own evidence, made through the repository's commit checks.
- Every applied edit stays inside the agreed change and its write scope, and never weakens governance.

## 3. Considered Options

- **Route**: the overall-refactor workflow in direct mode with a single-module test (refactor cost; needs the test);
  the feature development workflow for every work item (Unit and worker records for settled work); a fixed route
  regardless of module span (contradicts the repository's boundary).
- **Application** (chosen: isolated checkouts):
  - Keep sequential application on the previous checkpoint: per-change evidence, but too slow for broad passes.
  - Concurrent subagents in one shared checkout: no setup cost, but each change's verification sees the others' edits
    and commits cannot hold one change each.
  - Concurrent subagents in isolated checkouts from the current checkpoint, results committed one at a time on the
    work item branch: parallel and per-change evidence, at the cost of preparing each checkout and transferring
    results serially.

## 4. Decision Outcome

- **Route**: a batch's behavior-preserving work item follows the target repository's workflow for a
  behavior-preserving refactor across several areas (with the `spec` bundle, `sdd-overall-refactor`). This refines
  `ADR-overall-refactor-workflow`: a review-refactor run is a restructuring pass whose direction settles batch by
  batch with the user, so a work item spanning more than one module is overall-refactor work even though its
  decision round agreed its changes.
- **Single-module test**: the work item is a single-module refactor when every source file its agreed changes edit,
  including call sites, imports and re-exports, lies inside one feature or module of the repository's declared
  layout; only following edits (tests of the changed code and non-code text naming it) are left out. It then follows
  the feature workflow at the depth the repository's classification gives it. The playbook's agent applies the test
  once per work item, states the route and edited paths in the decision round and never splits or merges a work item
  to change its route. Without a declared layout, the decision round names the route and the user's approval
  settles it.
- **Write scope**: the batch's write scope is the edited paths the decision round states for its agreed changes,
  including their following edits.
- **Direct mode**: the playbook's agent works with the user, with no planning or development worker and no Unit, on
  the work item's own branch, never on the base branch. It splits the work item into edit tasks and uses general
  subagents for edits, drafting and research when the host supports them; otherwise it performs the same steps
  itself. Without a refactor workflow in the repository these steps are the procedure as stated.
- **Parallel application** (the change from the superseded ADR): edit tasks with disjoint write scopes run
  concurrently by default, each in its own isolated checkout (a Git worktree or any separate checkout) that the
  playbook's agent creates at the work item branch's current commit and prepares with the repository's documented
  setup (for example dependency installation and managed-asset synchronization), so verification and the
  repository's checks run there as on the work item branch. Each subagent edits only inside the
  explicit write scope the playbook's agent assigns, a subset of the batch's write scope, and leaves its result
  uncommitted. The playbook's agent moves each result onto the work item branch one at a time, checks its diff
  against the agreed change and its scope, reverts a rejected edit hunk by hunk without resetting a path another
  scope owns, redoes a result that no longer applies cleanly on the current checkpoint, verifies it there and commits it
  alone through the commit checks, so every commit holds one change with its own evidence. Changes whose write scopes
  overlap, or that build on another change, run one after another on the previous checkpoint.
- **Governance**: neither the playbook's agent nor an editing subagent adds an exception, an ignore entry, a rule
  setting or a bypass of the repository's checks to make a change pass; a subagent reports the failure, and the
  playbook's agent resolves the placement or returns the change to the decision round.
- **Subagent results**: a subagent's review or verification result is an evidence-backed opinion: the playbook's
  agent validates it against the code or diff at the cited location, re-runs the commands of a verification or
  negative-reachability claim before recording it, and counts a root as covered only when the result lists what was
  read. Subagents never ask the user, approve a change or write the run's records.
- **Verification, review, report, integration**: the playbook's agent runs the repository's full verification on a
  clean tree at the work item's final head, has the diff reviewed by a fresh reviewer subagent (otherwise a
  self-review recorded as such) at the repository's review effort where one is defined, reports every breaking change
  with the rest of the report in the final response and the commit body, and integrates only after the report through
  the repository's integration path and its own integration approval (with the `spec` bundle, task kind
  `overall-refactor`). The decision round never supplies the integration approval.
- Contract removals stay outside this route (`ADR-apply-approved-contract-removals-as-separate-work-items`).

## 5. Consequences

- Positive: broad passes apply independent changes concurrently, and each commit still carries one change verified
  through the commit checks; procedure replaces the ad-hoc parallel runs.
- Negative: each isolated checkout costs a setup and synchronization; the playbook's agent transfers, checks and
  verifies results serially, and the work item carries no Unit record, so its evidence lives in the run report and
  commit bodies.
- Risk: a result made on an older checkpoint conflicts with an earlier committed change; the disjoint scopes bound it,
  and a conflicting result is re-applied on the current checkpoint. A subagent edit drifts beyond the agreed change;
  the assigned scope, the diff check and the independent review bound it. A misapplied single-module test misroutes;
  the decision round names the route so the user can correct it.

## 6. Confirmation

- Spec review of `SPEC-review-refactor-lessons` maps AC-01, AC-02 and AC-03 to the playbook's application section
  (`applying.md`) and checks `CAP-DLV-review-refactor` and `UC-review-and-refactor-accumulated-slop` agree with it.
- Review confirms the route, single-module test, direct mode and the verification, review, report and integration
  steps carried over unchanged.
- A fixture exercise records the route decision and at least one parallel subagent edit with its transfer and diff
  check when the host supports subagents.
