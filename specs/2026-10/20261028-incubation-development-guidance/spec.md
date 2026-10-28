---
id: SPEC-incubation-development-guidance
title: Develop and resume an idea without SDD lifecycle records
summary: "Ships opt-in incubation guidance, optional support roles and mutable current context independently of SDD, with observed iteration and resume verification."
status: completed
created: 2026-10-28
depends_on: [SPEC-incubation-lifecycle-policy]
related_capabilities: [CAP-DLV-idea-incubation]
related_usecases: [UC-incubate-an-idea]
workflow: sdd-spec-feature
---

# [SPEC-incubation-development-guidance] Develop and resume an idea without SDD lifecycle records

## 1. Problem Statement & Motivation

Document formats are independently available, but product discovery, iterative implementation and resumption still
need an entry that does not route every change through SDD. The catalog bundle supplies that entry without a new
wheel or spec dependency. `ADR-keep-incubation-guidance-opt-in-and-current-state-based` fixes its ownership and context.

## 2. User Stories

- As an idea owner, I can start with an incomplete goal and reach a useful implemented or researched next action.
- As a coordinator, I can use optional clarification, research and actual-usage support inside explicit boundaries.
- As a later agent, I can resume from retained current facts and executable instructions without conversation history.

## 3. Non-Goals

- **Scope Excluded**: runtime approach policy, a second policy source or a readiness provider.
- **Scope Excluded**: automatic SDD activation, retrospective Units or immutable incubation history.
- **Scope Excluded**: a new wheel, application framework/scaffold catalog or autonomous execution service.
- **Scope Excluded**: mandatory delegation or a complete document set before implementation.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Isolated opt-in distribution

- **Given** built docs/catalog wheels without devkit-spec.
- **When** incubation is explicitly selected and sync runs.
- **Then** incubation skill, pointer, three roles and context template deploy from catalog; docs formats remain available and no SDD lifecycle assets are installed. Without selection, no incubation assets deploy.

### [AC-02] Adaptive incomplete-idea entry

- **Given** a partial goal and existing conversation/repository facts.
- **When** the entry skill runs in a labelled scenario walkthrough.
- **Then** it reuses known answers and asks only questions needed for the next useful research or implementation action, without a complete backlog, architecture, Unit or mandatory document set.

### [AC-03] Evidenced implementation and reconstruction

- **Given** a concrete uncertainty and representative product flow.
- **When** research or a bounded experiment informs implementation and the flow is exercised.
- **Then** evidence identifies method, source/artifact, outcome, limits and decision; reconstruction inside the goal updates current code/tests/docs without SDD records. A goal or constraint change returns to the user; skipped checks remain unverified.

### [AC-04] Optional bounded delegation

- **Given** separable clarification, research or usage-check work.
- **When** a role runs, or the coordinator elects inline work.
- **Then** payload/results preserve absolute boundaries and source identity without invented decisions, Git authority or a mandatory role sequence. Exercise both inline and delegated scenarios.

### [AC-05] Mutable current context and resume

- **Given** retained choices, run instructions and a recorded limitation.
- **When** another session resumes or sync/reselection runs.
- **Then** current context at `.devkit/incubation.md` preserves its project-owned bytes, lets the session identify and validate the next action, and requires no discarded-experiment history. Only the coordinator writes it.

### [AC-06] Approach applicability and SDD preservation

- **Given** effective SDD or unreadable approach policy.
- **When** `/incubate` runs.
- **Then** it stops product work and reports a configuration action. In incubation it consumes the common policy and docs context while retaining independent checks. Catalog installation never changes approach or existing SDD guidance.

## 5. Agreed Agent Contracts

### Distribution and entry

1. Register `incubation = "devkit_catalog.incubation"` through the existing `devkit.bundles` mechanism. Keep it opt-in
   with `auto_select` absent, like the other catalog bundles. No extra runtime dependency or new CLI is introduced.
2. `incubation:core` contains the constitution, one `/incubate` entry skill with references, an incubation guidance
   pointer, three optional subagent contracts and a current-context template available to the skill. It seeds no
   product documents or current context automatically.
3. A clean consumer installs devkit-docs plus devkit-catalog and selects `incubation:core`. The document package brings
   its existing distribution/harness dependencies. The supported path requires no installed devkit-spec distribution.
4. Entry and the pointer inspect the effective development approach through the common interface delivered by
   `SPEC-incubation-lifecycle-policy`. They run incubation work only when the result is incubation. A mismatch or
   unreadable policy gives the next configuration action; guidance never silently switches approach or removes SDD.
5. Selection and runtime applicability remain separate. Incubation assets can be present while SDD is selected;
   `/incubate` then explains the mismatch without doing product work. No unconditional instruction redirects every
   task in an existing SDD repository. Explicit removal of spec assets is distinct from installed runtime extensions.
6. Read `get-context incubation` once for the selected entry, and `get-context docs` before document authoring.
   Documents are added when they describe retained behavior or help the next decision, not as a complete set up front.

#### Adaptive work loop

- On entry, read existing current context and relevant run instructions before asking questions. Reuse answers already
  in the conversation or repository. Ask only what is missing for the next useful action, with a recommendation when
  alternatives are known. No fixed questionnaire, complete backlog or architecture is a prerequisite.
- Interview and brainstorming identify intended users, the problem, constraints, a representative flow and signs of
  usefulness. Label user decisions, agent recommendations and assumptions separately. Compare candidates only far
  enough to choose the next research or implementation action.
- Research answers one concrete decision. Retain evidence, limitations and the decision informed. When documentation
  is insufficient, bound a feasibility experiment by question, write scope, execution method and stop condition.
  Check sources when facts are time-sensitive. An inconclusive experiment is not successful verification.
- The first retained implementation connects a representative flow end to end, with commands to run it and verify it.
  Choose structure and tooling only as needed. Inside the agreed product goal and constraints, the coordinator can
  replace technologies, data models, features, tests and documents without a proposal, spec Unit or SDD envelope.
- A change to the agreed goal or constraints returns to the user. Normal implementation choices inside that scope
  do not create another approval ceremony. Existing host permissions and external mutation authority still apply.
- Build, lint, tests and actual usage check intended current behavior. Record which commands or interactions ran,
  their observed result and limitations. Never describe an unexecuted or skipped check as passed. Changes invalidate
  only affected evidence; abandoned experiments may remove their tests and documents with the implementation.
- Maintain current documents and `.devkit/incubation.md` when a retained choice or executable flow changes and before
  pausing or handing off. The coordinator owns that file; parallel roles return results rather than editing it.

#### Optional support contracts

| Role | Responsibility and return | Write and Git boundary |
| --- | --- | --- |
| `product-clarifier` | Candidate users/problems, alternatives, uncertainties and recommended questions for the coordinator; no invented user decisions. | Read-only; no index or HEAD change. |
| `incubation-researcher` | Evidence for one question, or a bounded feasibility experiment when explicitly assigned, with method, limits and recommendation. | Read-only by default; an experiment writes only the payload's explicit sandbox/prototype boundary; no commits. |
| `usage-reviewer` | Exercise the stated representative flow against expected usage; report observed behavior, evidence, missing coverage and failure conditions. | Read-only source scope; run checks/interactions only in the assigned test environment; no commits. |

Each call has one goal, absolute read/write boundaries, current source/artifact identity and expected output.
Roles are optional: use one when the question or verification scope separates usefully. Availability or selection
of the bundle does not require invoking all roles. The coordinator checks actual diff boundaries and folds evidence
into current context. A failed role result remains failed; it is not a product decision or approval.

#### Current context

`.devkit/incubation.md` is project-owned Markdown created by `/incubate` when useful, preserved by sync and eligible
for normal version control. It is not placed in managed or transient storage and has no devkit document ID or lifecycle
status. No new parser, schema, command or deterministic governance rule validates it.

The template captures:

- Current product goal, intended users, constraints and representative flow.
- Retained user decisions, current implementation choices and assumptions still requiring evidence.
- Run/setup instructions and the current verification method, observed results and source/artifact identity.
- Open product or technical questions, limitations and the next useful action.
- Pointers to current documents or retained evidence when those exist.

Keep current facts, not transcripts, per-iteration approvals, an immutable decision log or a list of discarded
experiments. Remove superseded choices and failed experiments that no longer inform work. Preserve important
uncertainty while it still matters. A temporary execution checklist may live in a coordinator-chosen scratch area;
it does not become a spec Unit or a durable product contract.

#### Interfaces with concurrent proposals

- The lifecycle-policy proposal owns setting location, inspection output, command preconditions and readiness.
  Its accepted shared `sdd|incubation` setting is inspected through `config show`, using
  `configuration.development.approach` and its source. The integrated policy preserves independent checks;
  this guidance adds no second policy source.
- `SPEC-incubation-sdd-baseline` consumes current goal, retained choices, implementation and verification evidence
  semantically. It need not parse this context filename or require historical records. Voluntary transition is owned
  there; `/incubate` records the user's intent and points to the accepted transition entry when available.
  For an explicit adoption request, explain preparing the spec package/assets while the effective approach remains
  incubation, then route to `sdd-baseline` in `spec:core` once available. Baseline readiness, activation and recovery
  remain owned by that playbook; the incubation entry does not activate SDD itself.
- All three Planning units write separate proposal directories. Implementation remains dependent on the accepted
  policy, and overlapping guides or architecture changes integrate sequentially after a scope comparison.


## 6. Verification Boundary and Assumptions

Mechanical asset tests cannot establish adaptive discovery or usable resume. Bounded scenario walkthroughs use
labelled synthetic inputs and a sample app, recording real commands/interactions and unmet observations.
The integrated policy supplies actual common inspection. Built-wheel consumers and labelled semantic walkthroughs
record observations in `materials/semantic-exercises.md`; shared Living Spec reflection is verified independently.
Historical worker records retain earlier scoped-turn limitations and do not describe final readiness.
