---
id: SPEC-review-refactor
title: Maintenance review and refactoring playbook
summary: Adds a review-refactor playbook to the maintenance bundle that reviews code, agent guidance and CLI commands for accumulated AI slop and consolidates, reduces and removes it with evidence, preserving agreed behavior or routing contract changes separately.
status: completed
created: 2026-10-26
related_capabilities:
  - CAP-DIST-content-packages
  - CAP-DIST-context-and-playbooks
  - CAP-DLV-drift-reconciliation
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-review-refactor] Maintenance review and refactoring playbook

## 1. Problem Statement & Motivation

Handed off from proposal PROP-review-refactor on 2026-10-26.

- **Preserved Materials**: `docs/materials/2026-10/20261026-review-refactor` (design options, Q1 review criteria
  research, Q2 internal integration, inbound references).
- **Decisions**: `ADR-bound-review-refactor-runs-by-surface-batch`,
  `ADR-apply-approved-contract-removals-as-separate-work-items`,
  `ADR-apply-behavior-preserving-batches-as-direct-mode-refactors` (refines the applicability of
  `ADR-overall-refactor-workflow` for these runs) and `ADR-require-reachability-evidence-and-layered-placement`.

AI coding agents tend to add code and text rather than remove it (`user`). Accumulated AI slop in code and agent
guidance (duplicated behavior, repeated technical helpers, unnecessary abstractions, speculative compatibility
paths, unneeded code, options and commands, duplicated or conflicting instructions, excessive always-loaded context)
is not caught by deterministic hygiene checks (`CAP-GOV-evaluation-lifecycle`), and a detect-and-repair pass alone
leaves the surface as large as before.

A maintenance playbook for a broad review and refactoring pass, run before a release, after substantial feature
growth or on request, shrinks that surface with repository evidence and engineering judgment. It consolidates
duplicated logic into shared modules, folds repeated technical helpers into utilities, and removes unneeded code,
guidance, options and commands, while preserving agreed behavior or routing a contract change separately. It is the
third playbook of the opt-in `maintenance` bundle in `devkit-catalog`, beside `drift-reconciliation` and
`weekly-report`, invoked manually or by an external runner, with no scheduler. It delivers the review and refactoring
outcome of `MS-maintenance-operations`.

## 2. User Stories

- **US-1**: As a developer, I want to invoke one playbook that reviews the code, guidance or CLI surfaces I select
  for accumulated maintenance cost, so that I get evidenced findings instead of a bigger codebase.
- **US-2**: As a developer, I want each surface batch decided in one round and the agreed behavior-preserving changes
  applied as a direct-mode refactor with per-change preservation evidence, so that consolidation and reduction land
  at refactor cost without silent behavior changes.
- **US-3**: As a developer, I want approved command, option, interface and compatibility-path removals to become
  their own contract work items, so that contract changes are never presented as refactoring.
- **US-4**: As a consumer project, I want to select the playbook through `maintenance:refactoring` alone or through
  `maintenance:upkeep` with drift reconciliation, so that I deploy only the procedures I use.

## 3. Non-Goals

1. **Scope Excluded**: scheduler or trigger design, history storage, and automatic execution; invocation and
   selection authorize no change.
2. **Scope Excluded**: cosmetic churn without an evidenced problem, speculative commonization and behavior-changing
   feature work presented as refactoring.
3. **Scope Excluded**: mandatory rule growth and automatic rule adoption; new detector tools as package dependencies.
4. **Scope Excluded**: a live refactor of this repository; acceptance applies changes only inside a disposable
   fixture.
5. **Scope Excluded**: changing the `spec` bundle's classification criteria to name a maintenance-playbook case
   (`packages/devkit-spec/` is outside this Unit; recorded as feedback).

## 4. Acceptance Criteria & Behavioral Contracts

`<pb>` is the playbook directory `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/review-refactor/`
with its entrypoint `SKILL.md` and its `references/`. Text criteria are checked with whitespace collapsed.

### [AC-01] The manifest declares the playbook and both presets

- **Given** the `maintenance` bundle manifest
- **When** a test loads it with the `devkit-dist` manifest reader
- **Then** it declares the assets `drift-reconciliation`, `weekly-report` and `review-refactor` (kind `playbook`,
  source the directory `playbooks/review-refactor`), the default preset stays `all`, and the presets are exactly
  `upkeep` = {`drift-reconciliation`, `review-refactor`}, `reporting` = {`weekly-report`} and `refactoring` =
  {`review-refactor`}.

### [AC-02] Each preset deploys its playbooks with search and exact retrieval

- **Given** a scratch project synchronized with `devkit-catalog`'s `maintenance` bundle
- **When** a test selects each of `all`, `upkeep`, `reporting` and `refactoring` in turn and syncs
- **Then** the managed tree holds exactly `bundle.toml` and the selected playbooks' files (`review-refactor`
  deploying `SKILL.md` and its `references/*.md`), nothing is deployed before selection, lexical search for each
  selected playbook's name returns it under bundle `maintenance`, and `GetPlaybook` for `maintenance/<name>` returns
  its name and a non-empty body.

### [AC-03] Entry condition and description bound invocation

- **Given** `<pb>SKILL.md`
- **When** a test reads its header and body
- **Then** the `description` names the review and refactoring operation and its user-selected scope, the entry
  condition says the user invoked or confirmed the playbook and names `devkit playbook get
  maintenance/review-refactor`, and the body states that invocation authorizes no change and an unattended run stops
  at the decision round with nothing applied.

### [AC-04] The playbook is self-contained and within the size budget

- **Given** every Markdown file under `<pb>`
- **When** a test reads them
- **Then** each is at most 12288 bytes, every `references/<name>.md` link in `SKILL.md` names an existing file and
  every reference file is linked, and no file contains a repository document ID matching
  `\b(ADR|CAP|UC|US|ARCH|SPEC|MS|PROP|FB)-[a-z]`; `uv run devkit rules check --phase hygiene <pb>` reports no
  `RULE-skill-document-size` or `RULE-agent-asset-wording` warning.

### [AC-05] A spec-review checklist maps the agreed design to playbook sections

- **Given** `materials/checklist.md` of this Unit
- **When** the reviewer reads it beside `<pb>`
- **Then** every item of §6 below has a row naming the playbook file and section that states it: each consolidation
  and reduction kind, each reduction ground, intake (surface and root selection, missing scope first), per-surface
  batching and cross-surface assignment (an unselected landing surface, the user's scope addition, following edits
  and their receipt-owned exclusion), the subagent review rules (validation and re-run of verification claims, no
  decision authority, the fallback without subagents), the applying rules (route, single-module test, batch write
  scope, direct mode, branch, subagent write scopes, sequential changes, the diff check and hunk revert, one commit
  per change on a clean tree, full verification, independent review and its fallback, report with breaking changes,
  integration after its own approval), the contract-removal work item and the compatibility-policy exception, each
  preservation-evidence part and the helper placement order; no row is empty.

### [AC-06] Living Spec, README and install guide name the playbook

- **Given** the Living Spec and package documentation after this change
- **When** `uv run devkit rules check` runs and a reader compares them with the manifest
- **Then** a delivery capability CAP-DLV-review-refactor lists `<pb>SKILL.md` as its entrypoint and a governance
  use case UC-review-and-refactor-accumulated-slop, which lists it; `CAP-DIST-content-packages` §6, the
  `devkit-catalog` README preset table and maintenance section, and the `maintenance` row of the install bundle
  recommendations name `review-refactor`, `upkeep` and `refactoring`; and the rules check reports no violation.

### [AC-07] A real read-only sweep stops at its decision round

- **Given** this repository at the Unit's base revision and the playbook source
- **When** the agent runs one bounded batch of the playbook over a user-equivalent selected surface and root
- **Then** `materials/sweep.md` records the intake, coverage, findings with location and named cost, dropped
  candidates and gaps, and a decision round left pending with nothing applied; each finding is recorded as a feedback
  follow-up in this Unit's `feedback/`; it is labeled manual evidence, not test coverage.

### [AC-08] A disposable fixture exercises direct-mode application

- **Given** a Git repository under the ignored `scratch/` path, with its own minimal test command, never committed
  to the worktree
- **When** the agent runs the playbook on it with simulated decisions
- **Then** `materials/fixture-exercise.md` records the decision round with its route and single-module test result,
  one consolidation, one helper fold and one removal as separate change records, each with reachability evidence,
  verification before and after, its fixture commit and patch, the helper's placement, at least one edit applied by
  a subagent with its diff check, and the fixture test command as full verification; decisions are labeled
  simulated, change only the fixture, and no real workflow, review or integration is opened.

## 5. Assumptions

- The playbook is a directory-form asset (`SKILL.md` plus `references/`), because the agreed procedure does not fit
  one 12288-byte file without trimming required constraints; `SKILL.md` keeps intake, batching, review, decisions
  and completion, and references hold the review criteria and evidence (`references/criteria.md`) and the applying
  procedure (`references/applying.md`), each read only at the step that needs it.
- The use case is named UC-review-and-refactor-accumulated-slop and the capability CAP-DLV-review-refactor; the
  capability carries the contract and the use case the developer's goal, as for drift reconciliation.
- This repository's `.devkit/config.toml` does not select `maintenance`, so no sync output changes; the sweep and the
  fixture read the playbook from its bundle source.
- The real sweep selects the CLI surface with the `devkit playbook` command group as its root: small enough for one
  batch, and it exercises inventory, help-accuracy and docstring criteria against code the reviewer did not write.
- The fixture exercise uses this host's subagents for one editing step, since the host supports them.
- `SPEC-spec-playbook-discovery` settled the entry wording; its manual-run sample is not extended, because AC-03
  checks the description form and the offer rule is unchanged.
- `PROP-maintenance-history` (draft) edits the same manifest, tests, README and `CAP-DIST-content-packages` entry; the
  run report records the fields that proposal names (run ID, repository identity, intake revision and dirty state,
  scope, outcome, resulting commit per change) without a history store.
- Interaction: the `spec` bundle's classification criteria name no maintenance-playbook case; the alignment is
  recorded as feedback for the Host, not changed here.

## 6. Agreed Design

The design agreed at `plan-accept`; the playbook states each rule in its own words without citing repository IDs.

### Asset and packaging

- `review-refactor` is one playbook asset of `maintenance` covering code, guidance and CLI in batches
  (`docs/materials/2026-10/20261026-review-refactor/design-options.md` O1). It joins the implicit `all` preset, is added to `upkeep` beside
  `drift-reconciliation`, and gets a solo preset `refactoring` (O6, `user`). Projects that already select
  `maintenance:upkeep` receive it on their next sync. Package validation (`devkit-catalog` bundle tests), the package
  README and the bundle recommendation guide are updated. Selecting or invoking it does not require the other
  maintenance playbooks. No version change is needed: the bundle version follows the shared release version.
- Development adds a delivery capability with the playbook as its entrypoint, a governance use case, and the
  maintenance entry of `CAP-DIST-content-packages`.
- The playbook's entry condition uses the wording every maintenance playbook carries: it runs only when the user
  invoked or confirmed it (`devkit-playbook`, `devkit playbook get maintenance/review-refactor` or a confirmed `spec`
  intake offer); selection never executes it. Its `description` names one operation (a review and refactoring pass
  that consolidates and reduces code, agent guidance and CLI commands) and its scope (user-selected surfaces and
  roots), so intake offers it only for a real review-refactor request (`ADR-spec-intake-playbook-discovery`). The
  capability points to `CAP-DIST-context-and-playbooks` for invocation instead of naming an entry skill.
- The report is a local artifact; the playbook requires no history store. It records what the existing maintenance
  playbooks record (run ID, repository identity, intake revision and dirty state, scope, outcome) plus the resulting
  commit per change.
- The playbook body is self-contained: it states its criteria, the reduction rule and the rule-growth criterion
  itself instead of citing this repository's document IDs.

### Run procedure

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

### Applying agreed changes (`user`)

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

### Review criteria

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

### Consolidation and reduction (`user`)

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

