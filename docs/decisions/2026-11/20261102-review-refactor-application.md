---
id: ADR-review-refactor-application
title: Review-refactor scope, evidence and application
summary: "For review-refactor runs, we batch selected surfaces per decision round, require reachability evidence and layered placement, apply agreed changes as direct-mode refactors in parallel checkouts and contract removals as own work items, to keep changes reviewable, accepting more rounds and evidence."
status: accepted
created_at: 2026-11-02
aliases:
  - ADR-apply-approved-contract-removals-as-separate-work-items
  - ADR-apply-behavior-preserving-batches-as-direct-mode-refactors
  - ADR-bound-review-refactor-runs-by-surface-batch
  - ADR-require-reachability-evidence-and-layered-placement
  - ADR-apply-review-refactor-changes-in-parallel-checkouts
---

# [ADR-review-refactor-application] Review-refactor scope, evidence and application

- **Status**: Accepted
- **Date**: 2026-11-02
- **Involved Components/Capabilities**: `maintenance/review-refactor` playbook (`packages/devkit-catalog`),
  `CAP-DLV-review-refactor`, `UC-review-and-refactor-accumulated-slop`

---

## 1. Context & Problem Statement

A review-refactor run covers code, agent guidance and CLI commands, whose review criteria differ and whose findings
are not comparable on one scale. A run over everything at once produces a decision round too large to judge and
mixed diffs that cannot be reviewed as one change. A finding often spans two surfaces, and a change on one surface
carries edits on another (tests, references, documentation).

Each behavior-preserving consolidation or removal needs an acceptance bar. Dead-code and clone tools give textual
candidates only and miss dynamic dispatch such as entry points and plugin registries, and a passing test suite proves
nothing for paths it does not exercise. Shortening guidance can remove constraints that change agent behavior. A
consolidated helper placed in the wrong module breaks the target repository's layer direction or grows a catch-all
module; in devkit, package-level `utils` and `base` are created only when needed and `devkit_core` never imports
application packages.

The changes a run applies are refactoring, not feature development (`user`): behavior-preserving consolidations and
reductions that add no behavior and usually span many files across several modules. Routing them through the feature
development workflow adds a Unit, planning and development workers and their records for changes the decision round
has already agreed. `ADR-delivery-classification` sends a behavior-preserving restructuring of several areas whose
direction settles while the work proceeds to the direct-only overall-refactor workflow and keeps a refactor inside
one feature or module on the feature workflows. It names no maintenance playbook run, so without a stated refinement
a multi-module work item of the run reads as feature work at `spec` depth. The playbook must also run in a repository
without the `spec` bundle.

Applying, verifying and committing changes one after another on the previous checkpoint keeps each commit's evidence
to its own change but is too slow on a broad pass with many independent changes: disjoint changes were run in
parallel checkouts outside the written procedure. Without a stated procedure those runs used checkouts without
synchronized managed assets (one change was committed without its commit checks), moved results by hand, and editing
subagents added import exceptions to make their change pass. Parallel subagents also over-report, and editing
subagents can drift beyond the agreed change, into each other's files or into each other's verification.

The reduction direction (`user`) requires that unneeded commands, options, public interfaces and compatibility paths
can actually be removed. Such a removal changes a contract: callers or inputs that worked stop working. It can never
be presented as behavior-preserving refactoring, and in-repository search does not prove the absence of dynamic or
external consumers. Deferring every such removal leaves reductions as unworked follow-ups.

---

## 2. Decision Drivers

- Each decision round and each resulting work item stays reviewable by one person.
- Invocation authorizes no change; only the user's decision round does (`ADR-playbook-retrieval`).
- Every finding is decided exactly once, and nothing is applied outside the scope the user agreed.
- A removed or merged path that is still reached is caught before the change lands.
- Evidence cost follows missing coverage, not a fixed ritual, so the reduction goal is not offset by new test volume.
- Guidance reductions keep every operational constraint they carry.
- Consolidation respects the target repository's declared layering and dependency direction.
- Agreed behavior-preserving changes are applied at the cost of a refactor, not of a feature delivery.
- The route follows the target repository's own boundary between a cross-area refactor and a single-module one.
- Parallel review and editing shorten a broad pass without weakening evidence or authority; a broad pass finishes in
  a fraction of the sequential time.
- Every commit holds one change with its own evidence, made through the repository's commit checks.
- Every applied edit stays inside the agreed change and its write scope, and never weakens governance.
- Reductions are applied, not left as unworked follow-ups.
- Contract changes stay separate and visible, never mixed into behavior-preserving changes.

---

## 3. Considered Options

- **Run scope**:
  - User-selected surfaces and roots split into one batch per surface, one decision round each: reuses the
    `drift-reconciliation` pattern; more rounds per run. (Chosen.)
  - All surfaces with a top-N cap ranked by maintenance cost: an arbitrary cap over incomparable criteria and large
    mixed diffs (rejected in `ADR-bound-review-refactor-runs-by-surface-batch`).
  - Diff-driven since a named ref or the last run: misses accumulated debt; needs `SPEC-maintenance-history` without
    a named ref (rejected in `ADR-bound-review-refactor-runs-by-surface-batch`).
- **Preservation evidence**:
  - Reachability (static plus dynamic reach) with verification before and after and a characterization test only
    where coverage is missing (medium cost). (Chosen.)
  - A characterization test before every change: high cost, adds test volume against the reduction goal (rejected in
    `ADR-require-reachability-evidence-and-layered-placement`).
  - Existing verification passing: untested paths pass trivially (rejected in
    `ADR-require-reachability-evidence-and-layered-placement`).
- **Helper placement**:
  - The lowest common owner under declared layering, with a new cross-package or foundation module as a decision
    (judgment on what is generic). (Chosen.)
  - Always a common `utils` in the nearest shared package: breaks layer direction, catch-all module (rejected in
    `ADR-require-reachability-evidence-and-layered-placement`).
  - Existing shared modules only: blocks most consolidations the `user` direction asks for (rejected in
    `ADR-require-reachability-evidence-and-layered-placement`).
- **Route**:
  - The repository's overall-refactor workflow in direct mode, with the single-module test sending a one-module work
    item to the feature workflows: refactor cost; needs the test. (Chosen.)
  - The feature development workflow for every work item: Unit and worker records per batch for settled work
    (rejected in `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors` and
    `ADR-apply-review-refactor-changes-in-parallel-checkouts`).
  - A fixed route regardless of module span: contradicts the repository's own boundary (rejected in
    `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors` and
    `ADR-apply-review-refactor-changes-in-parallel-checkouts`).
- **Subagents and application**:
  - Concurrent subagents in isolated checkouts from the current checkpoint, results committed one at a time on the
    work item branch: parallel and per-change evidence, at the cost of preparing each checkout and transferring
    results serially. (Chosen.)
  - Read-only review and verification, with the routed workflow applying every change: no edit drift, but no
    parallel edits (rejected in `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`).
  - The playbook's agent alone: slow on broad scope (rejected in
    `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`).
  - Keep sequential application on the previous checkpoint: per-change evidence, but too slow for broad passes
    (rejected in `ADR-apply-review-refactor-changes-in-parallel-checkouts`).
  - Concurrent subagents in one shared checkout: no setup cost, but each change's verification sees the others' edits
    and commits cannot hold one change each (rejected in `ADR-apply-review-refactor-changes-in-parallel-checkouts`).
- **Contract removals**:
  - The decision round may approve a contract removal as its own work item: applies the reduction, at a second work
    item per removal. (Chosen.)
  - A contract removal is always a deferred follow-up (feedback or draft proposal): lowest in-run cost, but
    reductions accumulate unworked (rejected in `ADR-apply-approved-contract-removals-as-separate-work-items`).
  - A removal counts as in-run refactoring when search finds no consumer: lowest cost, but dynamic or external
    consumers the search misses break and a contract change is mislabeled (rejected in
    `ADR-apply-approved-contract-removals-as-separate-work-items`).

---

## 4. Decision Outcome

### Scope and batches

- Intake: the user selects the surfaces (code, guidance, CLI) and the roots; missing scope is clarified before the
  review starts. The run splits into batches of one surface each, with one decision round per batch, because each
  round then judges comparable findings. (`ADR-bound-review-refactor-runs-by-surface-batch`)
- A cross-surface finding cites both sides and belongs to the batch of the surface where its change lands, so it is
  decided exactly once. (`ADR-bound-review-refactor-runs-by-surface-batch`)
- A cross-surface finding whose landing surface is outside the selected scope is recorded as deferred with a
  follow-up and is not applied, because the selected surfaces are the run's agreed scope. The user may add that
  surface to the run's scope, which adds its own batch, with its roots clarified as at intake, and its own decision
  round, and is recorded in the run report, because that addition is the user's own new authority.
  (`ADR-bound-review-refactor-runs-by-surface-batch`)
- The following edits of an agreed change belong to that change and its batch on any surface, because a refactor
  changes code, tests and documentation together and splitting them would leave the change inconsistent. Following
  edits are the tests of the changed code and non-code text naming it (documentation, guidance, the Living Spec
  statement of the result); call sites, imports and re-exports are source edits of the change itself. Following
  edits never touch receipt-owned files; they edit the source bundle, or record an upstream follow-up or a
  `devkit override`, because a sync would revert them. (`ADR-bound-review-refactor-runs-by-surface-batch`)

### Evidence and placement

- Every consolidation or removal records reachability evidence covering static references and the repository's
  dynamic reach: entry points, plugin registries, configuration, documentation and string dispatch. The record names
  each search (command, registry or configuration read) and its result, so a later miss is traceable.
  (`ADR-require-reachability-evidence-and-layered-placement`)
- The repository's relevant verification passes before and after the change, with both results recorded.
  (`ADR-require-reachability-evidence-and-layered-placement`)
- A characterization test is added only when some merged caller is exercised by no existing test, so tests are added
  only where coverage is missing. (`ADR-require-reachability-evidence-and-layered-placement`)
- A guidance change records a retained-constraint map: each constraint of the removed or merged text and where it
  remains. When the removal relies on a behavioral check, it also records a representative-task run with and without
  the text. (`ADR-require-reachability-evidence-and-layered-placement`)
- A consolidated helper lives at the lowest common owner every caller may already depend on under the target
  repository's declared layering. A new cross-package or foundation module, or a repository without declared
  layering, becomes a decision in the round. In devkit the order is feature-local first, then package-level `utils`
  (technical helpers) or `base` (contracts), then `devkit_core` only for generic primitives with no application
  dependency. (`ADR-require-reachability-evidence-and-layered-placement`)

### Application of behavior-preserving changes

- **Route**: a batch's behavior-preserving work item follows the target repository's workflow for a
  behavior-preserving refactor across several areas (with the `spec` bundle, `sdd-overall-refactor`). This refines
  `ADR-delivery-classification`: a review-refactor run is a restructuring pass whose direction settles batch by
  batch with the user, so a work item spanning more than one module is overall-refactor work even though its
  decision round agreed its changes. (`ADR-apply-review-refactor-changes-in-parallel-checkouts`)
- **Single-module test**: the work item is a single-module refactor when every source file its agreed changes edit,
  including call sites, imports and re-exports, lies inside one feature or module of the repository's declared
  layout; only following edits (tests of the changed code and non-code text naming it) are left out. It then follows
  the feature workflow at the depth the repository's classification gives it. The playbook's agent applies the test
  once per work item, states the route and edited paths in the decision round and never splits or merges a work item
  to change its route. Without a declared layout, the decision round names the route and the user's approval
  settles it. (`ADR-apply-review-refactor-changes-in-parallel-checkouts`)
- **Write scope**: the batch's write scope is the edited paths the decision round states for its agreed changes,
  including their following edits. (`ADR-apply-review-refactor-changes-in-parallel-checkouts`)
- **Direct mode**: the playbook's agent works with the user, with no planning or development worker and no Unit, on
  the work item's own branch, never on the base branch. It splits the work item into edit tasks and uses general
  subagents for edits, drafting and research when the host supports them; otherwise it performs the same steps
  itself. Without a refactor workflow in the repository these steps are the procedure as stated.
  (`ADR-apply-review-refactor-changes-in-parallel-checkouts`)
- **Parallel application**: edit tasks with disjoint write scopes run concurrently by default, each in its own
  isolated checkout (a Git worktree or any separate checkout) that the playbook's agent creates at the work item
  branch's current commit and prepares with the repository's documented setup (for example dependency installation
  and managed-asset synchronization), so verification and the repository's checks run there as on the work item
  branch. Each subagent edits only inside the explicit write scope the playbook's agent assigns, a subset of the
  batch's write scope, and leaves its result uncommitted. The playbook's agent moves each result onto the work item
  branch one at a time, checks its diff against the agreed change and its scope, reverts a rejected edit hunk by hunk
  without resetting a path another scope owns, redoes a result that no longer applies cleanly on the current
  checkpoint, verifies it there and commits it alone through the commit checks, so every commit holds one change with
  its own evidence. Changes whose write scopes overlap, or that build on another change, run one after another on the
  previous checkpoint. (`ADR-apply-review-refactor-changes-in-parallel-checkouts`)
- **Governance**: neither the playbook's agent nor an editing subagent adds an exception, an ignore entry, a rule
  setting or a bypass of the repository's checks to make a change pass; a subagent reports the failure, and the
  playbook's agent resolves the placement or returns the change to the decision round.
  (`ADR-apply-review-refactor-changes-in-parallel-checkouts`)
- **Subagent results**: a subagent's review or verification result is an evidence-backed opinion: the playbook's
  agent validates it against the code or diff at the cited location, re-runs the commands of a verification or
  negative-reachability claim before recording it, and counts a root as covered only when the result lists what was
  read. Subagents never ask the user, approve a change or write the run's records.
  (`ADR-apply-review-refactor-changes-in-parallel-checkouts`)
- **Verification, review, report, integration**: the playbook's agent runs the repository's full verification on a
  clean tree at the work item's final head, has the diff reviewed by a fresh reviewer subagent (otherwise a
  self-review recorded as such) at the repository's review effort where one is defined, reports every breaking change
  with the rest of the report in the final response and the commit body, and integrates only after the report through
  the repository's integration path and its own integration approval (with the `spec` bundle, task kind
  `overall-refactor`). The decision round never supplies the integration approval.
  (`ADR-apply-review-refactor-changes-in-parallel-checkouts`)
- Contract removals stay outside this route. (`ADR-apply-review-refactor-changes-in-parallel-checkouts`)

### Contract removals

- The decision round may approve removing a command, option, public interface or compatibility path, because the
  reduction direction requires applied removals. (`ADR-apply-approved-contract-removals-as-separate-work-items`)
- The approved removal becomes its own work item through the repository's normal development workflow, classified
  by that repository's own criteria, with the contract and documentation updated, kept apart from the batch's
  behavior-preserving work item and never routed as a refactor (the route under Application of behavior-preserving
  changes), because the contract change then stays visible and reviewable on its own.
  (`ADR-apply-approved-contract-removals-as-separate-work-items`)
- A compatibility-path removal under the declared compatibility-policy exception (the target repository states that
  no external consumer exists for that package) is a behavior-preserving removal instead; its change record still
  names the inputs or callers no longer accepted. (`ADR-apply-approved-contract-removals-as-separate-work-items`)

---

## 5. Consequences

- **Positive**:
  - Each decision round and work item is small and single-surface.
  - Still-reached paths and dropped constraints are caught per change; helpers do not invert layers.
  - Broad passes apply independent changes concurrently, without Unit overhead, and each commit still carries one
    change verified through the commit checks; procedure replaces the ad-hoc parallel runs.
  - Unneeded contracts are removed within the run's authority, each in a reviewable work item.
- **Negative**:
  - A run over three surfaces needs three decision rounds; findings landing on an unselected surface wait for a later
    run unless the user adds that surface.
  - Each change carries a reachability record and two verification results; guidance changes carry a constraint map.
  - Each isolated checkout costs a setup and synchronization; the playbook's agent transfers, checks and verifies
    results serially and re-runs verification claims, and the work item carries no Unit record, so its evidence lives
    in the run report and commit bodies.
  - Each approved contract removal adds a work item and its contract and documentation updates.
- **Risks**:
  - The following-edit rule is stretched to carry an unrelated change on another surface; the narrow definition and
    the diff check of each change against the batch's write scope bound it.
  - Dynamic reach the repository does not declare can still be missed; the record names what was searched, so a miss
    is traceable.
  - A result made on an older checkpoint conflicts with an earlier committed change; the disjoint scopes bound it, and
    a conflicting result is re-applied on the current checkpoint.
  - A subagent edit drifts beyond the agreed change; the assigned scope, the diff check and the independent review
    bound it.
  - A single-module test misapplied, or applied to a layout the repository does not declare, misroutes; the decision
    round names the route so the user can correct it.
  - An external consumer outside the repository breaks after a contract removal; the contract work item and the named
    inputs make the break traceable.
- **Follow-ups**:
  - When `SPEC-maintenance-history` lands, a diff-driven scope may be offered as an intake option; that change needs
    its own decision.
  - The `spec` bundle's classification criteria name no maintenance-playbook case; when this PADR is promoted, the
    Host records the alignment of `packages/devkit-spec` classification text as feedback, since this proposal's
    boundaries exclude it (from `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`).

---

## 6. Confirmation

- Spec-review checklist of the Development maps intake, per-surface batching and cross-surface assignment (an
  unselected landing surface, the user's scope addition, following edits and their receipt-owned exclusion) to
  playbook sections.
- Spec-review checklist of the Development maps each evidence part and the placement order to a playbook section.
- Spec-review checklist of the Development maps the contract-removal work item and the compatibility-policy
  exception to playbook sections.
- Spec-review checklist of the Development maps the route, the single-module test, the batch write scope, direct
  mode and its branch, the subagent write scopes, the diff check and hunk revert, the subagent review rules, commits
  on a clean tree, full verification, review and its fallback, the report with breaking changes and integration after
  its own approval to playbook sections.
- Spec review of `SPEC-review-refactor-lessons` maps AC-01, AC-02 and AC-03 to the playbook's application section
  (`applying.md`) and checks `CAP-DLV-review-refactor` and `UC-review-and-refactor-accumulated-slop` agree with it.
- Review confirms the route, single-module test, direct mode and the verification, review, report and integration
  steps carried over unchanged.
- Fixture exercise records one batch's decision round and its separate change records, the reachability evidence,
  before-and-after verification output and the helper's placement for its consolidation, helper fold and removal,
  and the route decision with at least one parallel subagent edit with its transfer and diff check when the host
  supports subagents (proposal section 3).
