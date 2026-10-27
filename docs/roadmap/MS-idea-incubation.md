---
id: MS-idea-incubation
title: Idea incubation and transition to SDD
summary: "Supports idea discovery, research, experimentation and lightweight app development without SDD lifecycle obligations, while retaining devkit document formats and an optional transition to SDD from the implemented baseline."
status: planned
created_at: 2026-10-27
depends_on: []
---

# [MS-idea-incubation] Idea incubation and transition to SDD

## Goal

Advances `ARCH-01-introduction-and-goals` §1.1 (Asset Distribution & Guidance Delivery), §1.2 (Repository
Governance & Deterministic Verification), §1.3 (Delivery Workflow Orchestration) and §1.9 (Document Search) by
supporting development before a product has stable requirements, architecture or maintenance commitments.

An idea can become a working app through interviews, brainstorming, research, experiments and implementation.
During this incubation, the user and agent can replace features, data models, screens and architecture without
creating an SDD Unit for each change or preserving every abandoned decision. Documents use devkit's established
formats to describe the current product as it takes shape.

Incubation is a complete development path for a small app. It does not require eventual adoption of SDD.
When continued feature development and maintenance need stronger change management, the user can establish a
baseline from the working implementation and current documents, then use SDD for subsequent changes.

Here, idea incubation concerns discovering and building the product itself. It is distinct from incubating an
SDD proposal, whose delivery direction is settled through Planning before Development.

### Starting from an incomplete idea

The entry skill accepts an initial goal without requiring a feature backlog, settled architecture or complete
requirements. Interviews help identify intended users, the problem, constraints, representative usage and signs
that the first version is useful. Questions follow what is missing from the conversation rather than repeating
a fixed questionnaire.

Brainstorming develops alternatives, makes trade-offs explicit and identifies assumptions worth testing.
The user can compare candidates, revise the goal and choose a narrower first version. The agent distinguishes
user decisions from its recommendations and from assumptions that still need evidence.

Discovery continues only as far as needed for the next useful action. Research or implementation can begin
before the whole product is specified. A working result can reopen earlier questions without restarting a
formal planning process.

### Research, experiments and repeated implementation

Research addresses a concrete decision, such as a platform constraint, an integration option or technical
feasibility. Findings identify their evidence, limitations and the decision they inform. When documentation
cannot settle a question, a bounded implementation experiment can test it.

The first implementation connects a representative user flow end to end. Initial setup includes a way to run
the app and verify that flow. Repository structure, tooling and supporting documents grow with the implementation
instead of requiring a complete architecture before the first working result.

Within the agreed product goal, implementation can include broad setup work and repeated reconstruction.
Temporary work breakdowns help execution without turning every task into an independently specified Unit.
An experiment can be discarded, a technology choice replaced and the current architecture rewritten as the
product becomes clearer. A change to the agreed goal or constraints returns to the user for direction.

### Skills and subagent support

The entry skill coordinates discovery, research, implementation, verification and current documentation.
Supporting skills and subagent roles cover product clarification, evidence gathering or feasibility experiments,
and checking actual usage against the intended flow. Delegation is available when a question or verification
scope can be separated; invoking every role is not a prerequisite for each iteration.

Product clarification starts before there is a stable product direction. It discovers candidate users, problems,
usage and first-version boundaries. This differs from the Backlog triage and decomposition addressed by
`MS-backlog-subagent-roles`, which organize feedback and delivery requests rather than discover the product.

The coordinating agent retains enough current context to resume in another session: the goal, decisions still in
effect, unresolved questions, observed results, execution instructions and the next useful action. This context
does not require SDD envelopes, per-iteration approval records or a history of discarded experiments.

### Shared document formats with separate lifecycle policy

Incubation reuses the applicable devkit document formats, including capabilities, use cases, architecture,
UX documents and decision documents. Documents are introduced when they help development or describe a result
that is being retained. Each iteration need not produce a complete document set.

An incubation decision document describes the current choice and its reason. It can be revised, replaced or
deleted when that choice changes. The same freedom applies to the current product and architecture documents;
the incarnation being abandoned need not be preserved as an accepted contract.

Document identity, frontmatter, applicable structural requirements and references remain verifiable.
SDD lifecycle obligations are separate: creating proposal or spec Units, traversing SDD workflow stages,
recording SDD approvals and envelopes, preserving ADR decisions, freezing completed artifacts, and maintaining
change-by-change delivery traceability are not required during incubation.

Project build, lint, test and usage verification remain available independently of SDD. Verification checks the
behavior intended to work in the current iteration. When an experiment is abandoned, tests and documents that
described it can be revised or removed with the implementation.

### Consistent CLI, rules and agent guidance

The project's selected development approach is inspectable and consistent across agent sessions and automated
checks. Shared document operations remain usable without SDD Units or workflow records. Incubation is supported
by the relevant command behavior, active rules and installed guidance together; an agent need not repeatedly
work around SDD failures to complete ordinary incubation work.

Disabling SDD lifecycle enforcement preserves document-format validation and independent project checks.
The implementation distinguishes omitted SDD obligations from checks that actually ran and passed.
Repositories using SDD retain its existing enforcement unless their development approach is explicitly changed.

### Optional transition from the implemented baseline

Transition begins when the user chooses to maintain the implemented product through SDD. Stable usage,
compatibility commitments, repeated feature additions and coordination needs can motivate that choice.
Code size, elapsed time and the number of experiments do not force graduation from incubation.

The transition reconciles retained behavior, important structure, current decisions and verification methods
against the actual implementation. It identifies unresolved behavior or missing evidence before claiming that
the baseline is ready. The resulting Living Spec describes what the user intends to preserve and evolve.

Subsequent changes follow the selected SDD policies. Earlier experiments do not need retrospective proposal or
spec Units, reconstructed approvals or an ADR for every discarded alternative. A small app can instead finish
within incubation or continue receiving lightweight changes there.

### Design decisions left to Planning

This milestone defines the development experience and its boundaries. It does not select a Python package,
bundle name, preset arrangement or exact configuration interface. The distribution design will determine how
shared templates, writing instructions and document tools are reused without installing conflicting entry
guidance or mandatory SDD policies.

The policy design will determine the authoritative project setting, how commands and rules consume it, and
whether temporary environment overrides are needed. CLI preconditions and integration readiness need explicit
incubation behavior where those operations are offered. A blanket bypass of every validation is insufficient
because document-format checks and project verification remain part of the intended experience.

## Exit condition

- A user can start with an incomplete idea and use interviews and brainstorming to choose a useful first
  implementation without first producing a complete feature backlog or SDD Unit.
- The agent can investigate a concrete uncertainty through research or a feasibility experiment and use the
  result to continue, narrow, revise or discard the candidate direction with the user.
- A representative app can be set up, run and exercised through its central user flow, then reconstructed
  within its agreed goal without per-change specs, SDD workflow records or mandatory ADR preservation.
- The delivered skills and subagent support cover product clarification, research or experimentation, and
  actual usage verification without making every role a mandatory stage of each iteration.
- A later agent session can resume from current goals, retained choices, unresolved questions and execution
  instructions without reconstructing the conversation or retaining every discarded experiment.
- Applicable devkit document formats and document lookup or search remain usable and verifiable during
  incubation. Current documents can change with the implementation without SDD lifecycle or immutability
  obligations being applied implicitly.
- CLI behavior, rule selection and installed agent guidance agree on whether SDD lifecycle policies apply.
  Independent project checks remain runnable, and omitted SDD checks are distinguishable from passed checks.
- A small app can be completed and maintained in incubation without being forced into SDD.
- A user can choose SDD adoption, establish a verified current-state baseline and start subsequent changes
  through SDD without backfilling delivery artifacts for earlier incubation work.
- A repository that retains SDD continues to enforce its existing lifecycle policies and document checks.

## Non-goals

- **Scope Excluded**: Implementing a particular end-user app, selecting a universal application stack or shipping
  a framework-specific scaffold catalog. An example app can demonstrate the development path.
- **Scope Excluded**: Replacing SDD proposal Planning or Backlog triage and decomposition for repositories that
  already use those processes.
- **Scope Excluded**: Making incubation a shallower SDD planning depth that still requires every broad setup or
  reconstruction request to pass through proposal and spec Units.
- **Scope Excluded**: Disabling all validation, treating skipped checks as successful verification or removing
  project build and test requirements merely because SDD is not active.
- **Scope Excluded**: Automatically graduating projects to SDD or reconstructing formal delivery history for
  work completed before the baseline.
- **Scope Excluded**: Automatically removing existing SDD obligations or reopening historical SDD artifacts in a
  repository that already follows SDD. The permissive editing described here concerns incubation artifacts.
- **Scope Excluded**: A persistent autonomous execution service, external product-management system or automatic
  publication of the resulting app.

## Completion review

Decomposition: pending
Direct proposal work: pending
