---
id: SPEC-review-refactor
title: Maintenance review and refactoring playbook
summary: Adds a review-refactor playbook to the maintenance bundle that reviews code, agent guidance and CLI commands for accumulated AI slop and consolidates, reduces and removes it with evidence, preserving agreed behavior or routing contract changes separately.
status: planned
created: 2026-10-26
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-review-refactor] Maintenance review and refactoring playbook

## 1. Problem Statement & Motivation

Handed off from proposal PROP-review-refactor on 2026-10-26.
- **Preserved Materials**: `docs/materials/2026-10/20261026-review-refactor`

### 1. Background & Hypothesis

AI coding agents tend to add code and text rather than remove it (`user`). Accumulated AI slop in code and agent
guidance (duplicated behavior, repeated technical helpers, unnecessary abstractions, speculative compatibility
paths, unneeded code, options and commands, duplicated or conflicting instructions, excessive always-loaded context)
is not caught by deterministic hygiene checks (`CAP-GOV-evaluation-lifecycle`), and a detect-and-repair pass alone
leaves the surface as large as before.

Hypothesis: a maintenance playbook for a broad review and refactoring pass, run before a release, after substantial
feature growth or on request, shrinks that surface with repository evidence and engineering judgment. It
consolidates duplicated logic into shared modules, folds repeated technical helpers into utilities, and removes
unneeded code, guidance, options and commands, while preserving agreed behavior or routing a contract change
separately. It is the third playbook of the opt-in `maintenance` bundle in `devkit-catalog`, beside
`drift-reconciliation` and `weekly-report`. It is invoked manually or by an external runner and needs no scheduler.
This draft carries the scope its own milestone held before the maintenance milestones merged into
`MS-maintenance-operations`.

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Maintenance review and refactoring playbook so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

- **Q1**: Which cited findings on AI slop patterns, causes and refactoring techniques yield repository-applicable
  review criteria, and where do automated detection limits lie?
  - Answer: 24 candidate criteria across code, guidance and CLI, each tagged with its source, evidence basis and
    detection class (`docs/materials/2026-10/20261026-review-refactor/q1-review-criteria-research.md` §2). Evidence on AI-assisted code quality is mixed
    (§1.1), so AI origin and line count are never findings by themselves. Clone and dead-code tools give textual
    candidates only and miss dynamic dispatch (§3). Shortening guidance can remove constraints that change agent
    behavior (§4).
- **Q2**: How does the playbook bound a review pass (intake, scope, candidate prioritization) so one run stays
  reviewable?
  - Answer: reuse the shared maintenance pattern of intake, explicit batches, coverage, one decision round and
    batch-only completion (`docs/materials/2026-10/20261026-review-refactor/q2-internal-integration.md`). The bounding unit is a user question
    (`docs/materials/2026-10/20261026-review-refactor/design-options.md` O2), settled as one batch per user-selected surface
    (`ADR-bound-review-refactor-runs-by-surface-batch`).

### 3. Proposed Design & Impact

#### Asset and packaging

- `review-refactor` is one playbook asset of `maintenance` covering code, guidance and CLI in batches
  (`docs/materials/2026-10/20261026-review-refactor/design-options.md` O1). It joins the implicit `all` preset, is added to `upkeep` beside
  `drift-reconciliation`, and gets a solo preset `refactoring` (O6, `user`). Projects that already select
  `maintenance:upkeep` receive it on their next sync. Package validation (`devkit-catalog` bundle tests), the package
  README and the bundle recommendation guide are updated. Selecting or invoking it does not require the other
  maintenance playbooks. No version change is needed: the bundle version follows the shared release version.
- Development adds a delivery capability with the playbook as its entrypoint, a governance use case, and the
  maintenance entry of `CAP-DIST-content-packages`.
- The playbook's invocation prerequisite (its entry condition) follows the authority wording that
  `PROP-spec-playbook-discovery` settles for every maintenance playbook. Until that proposal lands, the playbook runs
  only when invoked for the current task, by name or by exact `devkit playbook get maintenance/review-refactor`, and
  the capability points to `CAP-DIST-context-and-playbooks` for invocation instead of naming an entry skill. Its
  `description` names its operation and scope so search can find it.
- The report is a local artifact; the playbook requires no history store. It records what the existing maintenance
  playbooks record (run ID, repository identity, intake revision and dirty state, scope, outcome) plus the resulting
  commit per change.
- The playbook body is self-contained: it states its criteria, the reduction rule and the rule-growth criterion
  itself instead of citing this repository's document IDs.

#### Run procedure

- The playbook defines intake, review scope, candidate prioritization, agreed changes, verification and completion
  evidence, reusing the `drift-reconciliation` bounding pattern.
- Bounding (O2, `user`; `ADR-bound-review-refactor-runs-by-surface-batch`): the user selects the surfaces (code,
  guidance, CLI) and the roots at intake, and missing scope is clarified first. The run splits into batches of one
  surface each, with one decision round per batch. A cross-surface finding cites both sides and belongs to the batch
  of the surface where its change lands. A cross-surface finding whose landing surface is outside the selected scope
  is recorded as deferred with a follow-up and is not applied, unless the user adds that surface to the run's scope,
  which adds its own batch, with its roots clarified as at intake, and its own decision round, and is recorded in the
  run report. The following edits of an agreed change belong to that change and its batch on any surface; they are
  not cross-surface findings. Following edits are the tests of the changed code and non-code text naming it
  (documentation, guidance, the Living Spec statement of the result); call sites, imports and re-exports are source
  edits of the change itself. Following edits never touch receipt-owned files: they edit the source bundle the
  receipt projects, or record an upstream follow-up or a `devkit override`.
- Subagent review (`user`; `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`): within a surface
  batch the playbook uses spawned subagents when useful and the host supports them, for example parallel review per
  root or module, or independent verification of a consolidation or removal; otherwise the same steps run in the
  playbook's agent. The playbook's agent keeps coordination, the decision round and integration. A subagent's result
  is an evidence-backed opinion that the playbook's agent validates against the code or the diff at the cited
  location before it enters the decision round or a change record; an unconfirmed claim is dropped or recorded as a
  coverage gap. A verification or negative-reachability claim enters a change record only with its commands and
  results, and the playbook's agent re-runs those commands before recording. A root counts as covered only when the
  subagent's result lists what it read; otherwise it is a coverage gap. Subagents never ask the user, approve a
  change or write the run's records.
- Findings and implemented changes are separate records. Each change carries its behavior-preservation evidence and
  resulting commit. Deferred work links to existing or new follow-ups without duplication.
- Dispositions per finding: consolidate, reduce or remove with behavior preserved; contract change; defer; keep
  with a reason. Coverage counts the candidates dropped for lacking a named cost.
- Invocation, including an external runner naming the exact ID, authorizes no change (`ADR-external-playbook-execution`):
  only the user's decision round does, and an unattended run stops there with nothing applied.
- The user's decision-round approval is the recorded `user` intent for the routed work: it supplies the routed
  workflow's intent agreement (goal, scope and non-goals of the work item) and never its integration approval. The
  agreed behavior-preserving changes of one batch form one work item with one commit per change; each contract
  change is its own work item.
- A contract mismatch against agreed documentation is recorded as a deferred finding whose follow-up destination
  names drift reconciliation. The playbook never invokes another playbook; the user may name `drift-reconciliation`
  as a separate invocation. This playbook targets maintenance cost in code that is consistent with its contract.

#### Applying agreed changes (`user`)

The work the playbook applies is refactoring, not feature development
(`ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`, which refines the applicability of
`ADR-overall-refactor-workflow` for these runs).

- Route: the batch's behavior-preserving work item follows the target repository's workflow for a behavior-preserving
  refactor across several areas (with the `spec` bundle, `sdd-overall-refactor`), not its feature development
  workflow, unless the work item is a single-module refactor. A review-refactor run is a restructuring pass whose
  direction settles batch by batch in the conversation with the user, so a multi-module work item of the run is
  overall-refactor work even though its batch's decision round has agreed its changes.
- Single-module test: the work item is a single-module refactor when every source file its agreed changes edit,
  including call sites, imports and re-exports, lies inside one feature or module as the target repository's
  declared layout defines it; only following edits are left out. In devkit that is one `features/<feature>/`
  directory or one package-level module of one package; on the guidance surface, one skill, playbook or instruction;
  on the CLI surface, one command group's module. A single-module work item follows the repository's feature
  workflow at the depth that repository's own classification gives it (in devkit, `session` when the change touches
  no contract and no Living Spec text). The playbook's agent applies the test once per work item, states the route
  and the edited paths in the decision round, and never splits or merges a work item to change its route. Where the
  repository declares no layout, the decision round names the route with the edited paths and the user's approval
  settles it.
- Write scope: the batch's write scope is the edited paths the decision round states for the batch's agreed changes,
  including their following edits. Every edit stays inside it.
- Direct mode: the playbook's agent works with the user in the conversation, with no planning or development worker
  and no Unit. It splits the work item into edit tasks and, when useful and the host supports them, uses general
  subagents for parallel edits across many files, drafting and research; otherwise it performs the same steps itself.
  Where the repository has no refactor workflow, these steps and the ones below are the procedure as stated.
- Branch: the work item is applied on its own branch, never committed directly to the base branch; with the `spec`
  bundle, as the overall-refactor workflow's Git policy allows.
- Subagent edits: a subagent applies only agreed edits, inside an explicit write scope the playbook's agent assigns:
  a subset of the batch's write scope, disjoint from every other subagent working at the same time. Parallel editing
  subagents work on the same change; changes are applied, verified and committed one after another, each on the
  previous checkpoint. The playbook's agent checks each result against the diff before relying on it: the diff stays
  inside the assigned paths and matches the agreed change. The playbook's agent reverts a rejected edit hunk by hunk,
  never resets a path another scope owns, and redoes the change or returns it to the decision round. Subagents never
  commit, ask the user, approve a change or write the run's records.
- Commits: before each commit the working tree holds only the committed work plus the current change. The playbook's
  agent records the change's preservation evidence and commits the change as a checkpoint, one commit per change.
- Verification: each change's relevant verification passes before and after it, with only that change applied on the
  previous checkpoint (preservation evidence below), and the work item's final head passes the repository's full
  verification on a clean tree (in devkit: the full test suite, lint, type checks and the rules check).
- Review: an independent code review of the work item's diff runs before integration, by a fresh reviewer subagent
  the playbook's agent starts when the host supports it, otherwise as a self-review recorded as such. Its findings are
  fixed before integration. Where the repository's workflow defines review effort and bounded rounds (with the `spec`
  bundle, the run's activity effort, at `high` in bounded rounds), the review follows them.
- Report and integration: the work item's report (what changed and why, every breaking change including each
  compatibility-policy-exception removal and the inputs it no longer accepts, the verification results, anything
  left for follow-up) goes into the final response and the commit body. The work item integrates only after the
  report, through the repository's integration path and its own integration approval (without a repository policy,
  the user's explicit approval); the decision round never supplies it. With the `spec` bundle the path is the session
  integration path with task kind `overall-refactor`, and a single-module work item uses its feature workflow's path.
- Contract removals (O3, `user`; `ADR-apply-approved-contract-removals-as-separate-work-items`): the decision round
  may approve removing a command, option, public interface or compatibility path, unless the declared
  compatibility-policy exception applies (then it is a behavior-preserving removal that still names the inputs no
  longer accepted). The removal is not behavior-preserving: it becomes its own work item through the repository's
  normal development workflow, classified by that repository's own criteria, with the contract and documentation
  updated, kept apart from the batch's behavior-preserving work item and never routed as a refactor.

#### Review criteria

- Review criteria come from cited research and distinguish evidenced problems from stylistic preference. A finding
  cites a location and its maintenance cost; a finding without a named cost is dropped, since the reviewing agent
  itself over-reports (`docs/materials/2026-10/20261026-review-refactor/q1-review-criteria-research.md` §3 item 6).
- Code review covers duplicated behavior, repeated technical helpers, unnecessary abstractions, speculative
  compatibility paths, unused code, unused parameters and flags, and boilerplate without a demonstrated purpose.
- Guidance review covers skills, playbooks, AGENTS.md and instructions for derivable content, duplication, conflicts,
  obsolete exceptions and excessive always-loaded context. It preserves repository-specific operational constraints,
  decision criteria and examples. Receipt-owned files (`.devkit/managed/` and agent projections) are read-only
  evidence: a finding against them goes to the source bundle as an upstream follow-up or to `devkit override`, and
  only repository-owned text is edited.
- CLI review inventories commands and subcommands for overlapping purposes, unneeded commands and options,
  fragmented operations and inconsistent grouping. It reviews help and its source docstrings for accuracy and useful
  next steps.
- Tool output (clone detectors, dead-code finders, unselected lint rules) is a candidate list; the playbook installs
  nothing without asking.

#### Consolidation and reduction (`user`)

- The playbook treats consolidation and reduction as primary outcomes, not only detection and repair. At minimum it
  covers merging duplicated logic into a shared module, folding repeated technical helpers into a utility, and
  removing unneeded code, guidance, options and commands.
- Removing a compatibility path (shim, legacy reader, version branch) is a contract change, unless the target
  repository's declared compatibility policy states that no external consumer exists for that package. Either way,
  the change record names the inputs or callers no longer accepted. In-repository reachability never proves the
  absence of external consumers.
- Shared implementations are introduced only for demonstrated repeated behavior: at least two current callers with
  the same behavior, where a change to one must be repeated in the others.
- Helper placement (O5, `user`; `ADR-require-reachability-evidence-and-layered-placement`): a consolidated helper
  lives at the lowest common owner every caller may already depend on under the target repository's declared
  layering. A new cross-package or foundation module, or a repository without declared layering, becomes a decision
  in the round. The playbook states the devkit order as its example: feature-local first, then package-level
  `utils` (technical helpers) or `base` (contracts), then `devkit_core` only for generic primitives with no
  application dependency.
- A reduction is accepted only when the removed content is derivable from the repository, duplicated with a named
  canonical copy kept, enforced mechanically elsewhere, or shown unnecessary by a recorded check. The recorded check
  for code is the verification command and its result plus reachability evidence; for guidance it is a recorded
  representative-task run with and without the text. Without that record the fourth ground is unavailable. Line or
  token reduction is reported but is never the justification.
- Preservation evidence (O4, `user`; `ADR-require-reachability-evidence-and-layered-placement`): every
  consolidation or removal records reachability evidence covering static references and the repository's dynamic
  reach (entry points, plugin registries, configuration, documentation, string dispatch), and the relevant
  verification passing before and after. The reachability record names each search (command, registry or
  configuration read) and its result. A characterization test is added only when some merged caller is exercised by
  no existing test. A guidance change records a retained-constraint map (each constraint of the removed or merged text
  and where it remains), plus the recorded representative-task run when the removal relies on a behavioral check.
- Contract-changing removals, renames or consolidations of commands, options or public interfaces are never
  presented as behavior-preserving refactoring; they follow the contract-removal work item above.
- Recurrence prevention first considers deleting, consolidating or correcting existing code and guidance. A new rule
  needs an evidenced recurring failure and a stated benefit, and follows `CAP-GOV-rule-authoring`.

#### Non-goals and acceptance direction

- Non-goals: scheduler or trigger design, cosmetic churn without an evidenced problem, speculative commonization,
  behavior-changing feature work presented as refactoring, mandatory rule growth and automatic rule adoption.
- Acceptance direction:
  - Bundle tests cover the new asset in the `all`, `upkeep` and `refactoring` presets (with `upkeep` keeping
    `drift-reconciliation` and `refactoring` deploying `review-refactor` alone), lexical search and exact retrieval.
    The README preset table and the install recommendation name both presets.
  - A spec-review checklist maps each consolidation and reduction kind, each reduction ground, intake (surface and
    root selection, missing scope clarified first), the per-surface batching and cross-surface assignment (an
    unselected landing surface, the user's scope addition, following edits and their receipt-owned exclusion), the
    subagent review rules (validation and re-run of verification claims, no decision authority, the fallback on a
    host without subagents), the applying rules (route, single-module test, batch write scope, direct mode, branch,
    subagent write scopes, sequential changes, the diff check and hunk revert, one commit per change on a clean
    tree, full verification, independent review and its fallback, report with breaking changes, integration after
    its own approval), the
    contract-removal work item, each preservation-evidence part and the helper placement order to a playbook
    section.
  - Manual evidence, following the `drift-reconciliation` precedent, is named as manual evidence and never reported as
    test coverage. It has two parts.
    - A real, bounded, read-only sweep of this repository records findings, coverage and gaps. It stops at its
      decision round with nothing applied, as an unattended run does. Its findings are recorded as feedback
      follow-ups, and a real decision round is a separate invocation after delivery. This delivery makes no live
      refactor.
    - The fixture is a disposable Git repository in an ignored scratch path inside the worktree (for example
      `scratch/`), never committed to the worktree, with its own minimal test command. Its own `git init` and
      commits are fixture operations. The simulated decision round states the route and the single-module test
      result, and direct mode runs inside the fixture: the playbook's agent applies the changes, at least one
      through a subagent edit with its diff check when the host supports subagents, commits each change in the
      fixture and runs the fixture test command as its full verification; no real workflow, review or integration
      is opened. With simulated decisions, it exercises one consolidation, one helper fold and one removal, applied
      only inside the fixture, with separate change records and the preservation evidence above (reachability,
      before-and-after verification, and the helper's placement). The patches, commit IDs and before-and-after
      command output are kept in the Unit's materials because the fixture is discarded. The playbook's exercise rule
      reads: decisions are simulated and change only the fixture.
  - Every playbook file passes the repository's skill document size rule. A directory-form playbook with
    `references/` is allowed, and the bundle tests then follow its form. The criteria are condensed into review
    questions rather than copied from the research tables.

#### Planning decisions

- One playbook rather than one per surface (O1); the Q2 bounding pattern reused from the existing maintenance
  playbooks.
- Ownership covers the maintenance bundle, the catalog bundle tests and README, distribution capabilities, governance
  use cases and install guides, which Development edits.
- User answers (all recommended options, `user`): bounding by surface batch with batch-scoped subagents (O2-A),
  contract removals as their own work items (O3-A), reachability-based preservation evidence (O4-A), lowest common
  owner placement (O5-A), and `upkeep` plus a solo `refactoring` preset (O6-A). O2 is recorded in
  `ADR-bound-review-refactor-runs-by-surface-batch`, O3 in
  `ADR-apply-approved-contract-removals-as-separate-work-items`, O4 and O5 in
  `ADR-require-reachability-evidence-and-layered-placement`. O6 is packaging and needs no PADR.
- Execution model (`user`, `answer-02`): the playbook applies refactoring, so a batch's behavior-preserving work
  item follows the overall-refactor workflow in direct mode, and playbook-spawned subagents may apply agreed edits
  within the batch's write scope. This replaces the earlier read-only subagent rule under which the routed
  development workflow applied every change. The single-module test follows the overall-refactor workflow's own
  boundary (a refactor inside one feature or module follows the feature workflows), so it needs no user question.
  The deferral of findings that land on an unselected surface still holds, because the selected surfaces are the
  run's agreed scope; the user may add a surface, and the following edits of a change stay with it. The execution
  model and the subagent rules are recorded in `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors`,
  which refines the applicability of `ADR-overall-refactor-workflow` when promoted. Follow-up for the Host: the
  `spec` bundle's classification criteria (`overall-refactor` only for a change whose direction settles during the
  work) name no maintenance-playbook case; aligning them is outside this proposal's boundaries
  (`packages/devkit-spec/`), so the Host records it as feedback.
- `dev_effort` stays `medium`: the work has no effect that cannot be undone locally and no unresolved P1.

#### Interactions

- `PROP-spec-playbook-discovery` also owns
  `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/`, `packages/devkit-catalog/README.md`,
  `guides/install/`, `docs/usecases/governance/`, `docs/capabilities/delivery/` and
  `docs/capabilities/distribution/`, to reword every playbook's explicit-invocation prerequisite and to let `spec`
  discover playbooks at task intake. The new playbook's invocation prerequisite follows the authority wording that
  proposal settles. Whichever proposal lands second reconciles the other's wording.
- `PROP-maintenance-history` declares the same maintenance bundle and delivery capability paths and edits the same
  `bundle.toml`, bundle tests, README and maintenance entry of `CAP-DIST-content-packages`. The Host sequences the two
  Developments.

### 4. Lifecycle & Retirement Criteria

<!--
- Preliminary decisions: devkit spec proposal padr review-refactor "<title>" --summary "<Y-statement>" records a PADR in decisions/.
- On acceptance (plan-accept): devkit spec proposal accept review-refactor --by user, then the Planning branch is merged.
  Development starts with devkit spec proposal handoff review-refactor.
- On rejection: change only status: rejected, with the user's reason in the commit message.
-->

