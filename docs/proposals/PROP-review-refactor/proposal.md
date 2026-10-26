---
id: PROP-review-refactor
title: Maintenance review and refactoring playbook
summary: "Adds a review-refactor playbook to the maintenance bundle that reviews code, agent guidance and CLI commands for accumulated AI slop and consolidates, reduces and removes it with evidence, preserving agreed behavior or routing contract changes separately."
status: reviewing                       # draft | reviewing | accepted | rejected
created_at: 2026-10-22
target_area: delivery/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-maintenance-operations
boundaries:
  owns:
    - packages/devkit-catalog/
    - docs/capabilities/delivery/
    - docs/capabilities/distribution/
    - docs/usecases/governance/
    - guides/install/
  excludes:
    - docs/decisions/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-review-refactor] Maintenance review and refactoring playbook

## 1. Background & Hypothesis

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

## 2. Technical Spike Questions

- **Q1**: Which cited findings on AI slop patterns, causes and refactoring techniques yield repository-applicable
  review criteria, and where do automated detection limits lie?
  - Answer: 24 candidate criteria across code, guidance and CLI, each tagged with its source, evidence basis and
    detection class (`materials/q1-review-criteria-research.md` §2). Evidence on AI-assisted code quality is mixed
    (§1.1), so AI origin and line count are never findings by themselves. Clone and dead-code tools give textual
    candidates only and miss dynamic dispatch (§3). Shortening guidance can remove constraints that change agent
    behavior (§4).
- **Q2**: How does the playbook bound a review pass (intake, scope, candidate prioritization) so one run stays
  reviewable?
  - Answer: reuse the shared maintenance pattern of intake, explicit batches, coverage, one decision round and
    batch-only completion (`materials/q2-internal-integration.md`). The bounding unit is a user question
    (`materials/design-options.md` O2).

## 3. Proposed Design & Impact

### Asset and packaging

- `review-refactor` is one playbook asset of `maintenance` covering code, guidance and CLI in batches
  (`materials/design-options.md` O1). It joins the implicit `all` preset; its explicit preset placement is a user
  question (O6). Package validation (`devkit-catalog` bundle tests), the package README and the bundle recommendation
  guide are updated. Selecting or invoking it does not require the other maintenance playbooks. No version change is
  needed: the bundle version follows the shared release version.
- Development adds a delivery capability with the playbook as its entrypoint, a governance use case, and the
  maintenance entry of `CAP-DIST-content-packages`.
- Wording stays neutral to the parallel `PROP-spec-playbook-discovery` and `PROP-maintenance-history`. The playbook
  runs only when invoked for the current task, by name or by exact `devkit playbook get maintenance/review-refactor`,
  and the capability points to `CAP-DIST-context-and-playbooks` for invocation instead of naming an entry skill. The
  report is a local artifact; the playbook requires no history store and records forward-compatible run fields (run
  ID, intake revision and dirty state, scope, outcome, and the resulting commit per change).
- The playbook body is self-contained: it states its criteria, the reduction rule and the rule-growth criterion
  itself instead of citing this repository's document IDs.

### Run procedure

- The playbook defines intake, review scope, candidate prioritization, agreed changes, verification and completion
  evidence, reusing the `drift-reconciliation` bounding pattern; a manual run demonstrates the path.
- Findings and implemented changes are separate records. Each change carries its behavior-preservation evidence and
  resulting commit. Deferred work links to existing or new follow-ups without duplication.
- Dispositions per finding: consolidate, reduce or remove with behavior preserved; contract change (handling per
  O3); defer; keep with a reason.
- Invocation, including an external runner naming the exact ID, authorizes no change (`ADR-external-playbook-execution`):
  only the user's decision round does, and an unattended run stops there with nothing applied.
- Agreed changes are applied through the repository's development workflow, classified by its own criteria (in a
  devkit-spec repository: a cross-area structural change is `overall-refactor`; a change inside one feature or module
  is `feature`).
- Contract mismatches against agreed documentation route to `drift-reconciliation`; this playbook targets maintenance
  cost in code that is consistent with its contract.

### Review criteria

- Review criteria come from cited research and distinguish evidenced problems from stylistic preference. A finding
  cites a location and its maintenance cost; a finding without a named cost is dropped, since the reviewing agent
  itself over-reports (`materials/q1-review-criteria-research.md` §3 item 6).
- Code review covers duplicated behavior, repeated technical helpers, unnecessary abstractions, speculative
  compatibility paths, unused code, unused parameters and flags, and boilerplate without a demonstrated purpose.
- Guidance review covers skills, playbooks, AGENTS.md and instructions for derivable content, duplication, conflicts,
  obsolete exceptions and excessive always-loaded context. It preserves repository-specific operational constraints,
  decision criteria and examples.
- CLI review inventories commands and subcommands for overlapping purposes, unneeded commands and options,
  fragmented operations and inconsistent grouping. It reviews help and its source docstrings for accuracy and useful
  next steps.
- Tool output (clone detectors, dead-code finders, unselected lint rules) is a candidate list; the playbook installs
  nothing without asking.

### Consolidation and reduction (`user`)

- The playbook treats consolidation and reduction as primary outcomes, not only detection and repair. At minimum it
  covers merging duplicated logic into a shared module, folding repeated technical helpers into a utility, and
  removing unneeded code, guidance, options and commands.
- Shared implementations are introduced only for demonstrated repeated behavior: at least two current callers with
  the same behavior, where a change to one must be repeated in the others. A consolidated helper lives at the place
  the target repository's layering allows (placement per O5).
- A reduction is accepted only when the removed content is derivable from the repository, duplicated with a named
  canonical copy kept, enforced mechanically elsewhere, or shown unnecessary by a behavioral or verification check.
  Line or token reduction is reported but is never the justification. The evidence a removal or consolidation needs
  is set per O4.
- Contract-changing removals, renames or consolidations of commands, options or public interfaces are never
  presented as behavior-preserving refactoring (handling per O3).
- Recurrence prevention first considers deleting, consolidating or correcting existing code and guidance. A new rule
  needs an evidenced recurring failure and a stated benefit, and follows `CAP-GOV-rule-authoring`.

### Non-goals and acceptance direction

- Non-goals: scheduler or trigger design, cosmetic churn without an evidenced problem, speculative commonization,
  behavior-changing feature work presented as refactoring, mandatory rule growth and automatic rule adoption.
- Acceptance direction:
  - Bundle tests cover the new asset in its presets, lexical search and exact retrieval.
  - The playbook text covers each consolidation and reduction kind and the four reduction grounds.
  - A recorded manual run on this repository shows separate finding and change records, at least one consolidation
    or removal with its preservation evidence, and coverage with its gaps.

### Planning decisions

- One playbook rather than one per surface (O1); the Q2 bounding pattern reused from the existing maintenance
  playbooks.
- Ownership widened to the catalog package, distribution capabilities, governance use cases and install guides,
  which Development edits. `PROP-maintenance-history` declares overlapping paths in the same bundle, so the two
  Developments need sequencing.
- Pending user answers: bounding (O2), contract removals (O3), preservation evidence (O4), helper placement (O5) and
  presets (O6).

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr review-refactor "<title>" --summary "<Y-statement>" records a PADR in decisions/.
- On acceptance (plan-accept): devkit spec proposal accept review-refactor --by user, then the Planning branch is merged.
  Development starts with devkit spec proposal handoff review-refactor.
- On rejection: change only status: rejected, with the user's reason in the commit message.
-->
