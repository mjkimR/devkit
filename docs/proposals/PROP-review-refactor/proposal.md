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
    - packages/devkit-catalog/src/devkit_catalog/maintenance/
    - packages/devkit-catalog/tests/integration/bundles/
    - packages/devkit-catalog/README.md
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

### Run procedure

- The playbook defines intake, review scope, candidate prioritization, agreed changes, verification and completion
  evidence, reusing the `drift-reconciliation` bounding pattern.
- Findings and implemented changes are separate records. Each change carries its behavior-preservation evidence and
  resulting commit. Deferred work links to existing or new follow-ups without duplication.
- Dispositions per finding: consolidate, reduce or remove with behavior preserved; contract change (handling per
  O3); defer; keep with a reason. Coverage counts the candidates dropped for lacking a named cost.
- Invocation, including an external runner naming the exact ID, authorizes no change (`ADR-external-playbook-execution`):
  only the user's decision round does, and an unattended run stops there with nothing applied.
- The user's decision-round approval is the recorded `user` intent for the routed work: it supplies the routed
  workflow's intent approval and never its integration approval. The agreed behavior-preserving changes of one batch
  form one work item with one commit per change; each contract change is its own work item.
- Each work item is applied through the repository's development workflow and classified by that repository's own
  classification criteria; the playbook does not restate them.
- A contract mismatch against agreed documentation is recorded as a deferred finding whose follow-up destination
  names drift reconciliation. The playbook never invokes another playbook; the user may name `drift-reconciliation`
  as a separate invocation. This playbook targets maintenance cost in code that is consistent with its contract.

### Review criteria

- Review criteria come from cited research and distinguish evidenced problems from stylistic preference. A finding
  cites a location and its maintenance cost; a finding without a named cost is dropped, since the reviewing agent
  itself over-reports (`materials/q1-review-criteria-research.md` §3 item 6).
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
  the same behavior, where a change to one must be repeated in the others. A consolidated helper lives at the place
  the target repository's layering allows (placement per O5).
- A reduction is accepted only when the removed content is derivable from the repository, duplicated with a named
  canonical copy kept, enforced mechanically elsewhere, or shown unnecessary by a recorded check. The recorded check
  for code is the verification command and its result plus reachability evidence; for guidance it is a recorded
  representative-task run with and without the text. Without that record the fourth ground is unavailable. Line or
  token reduction is reported but is never the justification. The further evidence a removal or consolidation needs
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
  - A spec-review checklist maps each consolidation and reduction kind and each reduction ground to a playbook
    section.
  - Manual evidence, following the `drift-reconciliation` precedent, is named as manual evidence and never reported as
    test coverage. It has two parts.
    - A real, bounded, read-only sweep of this repository records findings, coverage and gaps. It stops at its
      decision round with nothing applied, as an unattended run does. Its findings are recorded as feedback
      follow-ups, and a real decision round is a separate invocation after delivery. This delivery makes no live
      refactor.
    - The fixture is a disposable Git repository outside the worktree with its own minimal test command. With
      simulated decisions, it exercises one consolidation, one helper fold and one removal, applied only inside the
      fixture, with separate change records and preservation evidence. The patches, commit IDs and before-and-after
      command output are kept in the Unit's materials because the fixture is discarded. The playbook's exercise rule
      reads: decisions are simulated and change only the fixture.
  - The playbook passes the repository's skill document size rule as one `playbooks/<name>.md` file; the criteria
    are condensed into review questions rather than copied from the research tables.

### Planning decisions

- One playbook rather than one per surface (O1); the Q2 bounding pattern reused from the existing maintenance
  playbooks.
- Ownership covers the maintenance bundle, the catalog bundle tests and README, distribution capabilities, governance
  use cases and install guides, which Development edits.
- Pending user answers: bounding (O2), contract removals (O3), preservation evidence (O4), helper placement (O5) and
  presets (O6).

### Interactions

- `PROP-spec-playbook-discovery` also owns
  `packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/`, `packages/devkit-catalog/README.md`,
  `guides/install/`, `docs/usecases/governance/`, `docs/capabilities/delivery/` and
  `docs/capabilities/distribution/`, to reword every playbook's explicit-invocation prerequisite and to let `spec`
  discover playbooks at task intake. The new playbook's invocation prerequisite follows the authority wording that
  proposal settles. Whichever proposal lands second reconciles the other's wording.
- `PROP-maintenance-history` declares the same maintenance bundle and delivery capability paths. The two Developments
  need sequencing on `bundle.toml`, the bundle tests, the README and the maintenance entry of
  `CAP-DIST-content-packages`.

## 4. Lifecycle & Retirement Criteria
<!--
- Preliminary decisions: devkit spec proposal padr review-refactor "<title>" --summary "<Y-statement>" records a PADR in decisions/.
- On acceptance (plan-accept): devkit spec proposal accept review-refactor --by user, then the Planning branch is merged.
  Development starts with devkit spec proposal handoff review-refactor.
- On rejection: change only status: rejected, with the user's reason in the commit message.
-->
