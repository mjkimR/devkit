---
id: PROP-incubation-development-guidance
title: Develop and resume an idea without SDD lifecycle records
summary: "Ships opt-in incubation guidance, optional clarification, research and usage-verification roles, and mutable current product context independently of SDD assets."
status: reviewing
created_at: 2026-10-28
target_area: delivery/
priority: medium
size: L
planning_effort: medium
dev_effort: medium
milestone: MS-idea-incubation
depends_on: [PROP-incubation-lifecycle-policy]
boundaries:
  owns:
    - packages/devkit-catalog/
    - docs/capabilities/delivery/
    - docs/capabilities/harness/
    - docs/usecases/delivery/
    - docs/usecases/harness/
    - docs/architecture/
    - docs/decisions/
    - docs/steering/
    - guides/
  excludes:
    - packages/devkit-spec/
    - packages/devkit-docs/
    - packages/devkit-dist/
    - packages/devkit/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-incubation-development-guidance] Develop and resume an idea without SDD lifecycle records

## 1. Background & Hypothesis

`MS-idea-incubation` describes a complete development path from an incomplete idea to an app that can remain in
incubation. `SPEC-document-bundle-split` supplies shared document formats without SDD assets. The lifecycle-policy
proposal owns runtime applicability; this proposal supplies the agent's discovery, implementation and resume behavior.

The existing spec entry skill and support roles operate on SDD delivery requests. Product discovery needs to identify
users, problems and a useful first flow before those delivery requests exist. An opt-in catalog bundle can coordinate
that work without a new wheel or lifecycle records. Ownership evidence is in `materials/ownership-evidence.md`.

## 2. Technical Spike Questions

- **Q1 — ownership**: recommend an opt-in `incubation` bundle in devkit-catalog, rather than an extra wheel or
  putting approach-specific guidance into docs or spec. See `PADR-keep-incubation-guidance-opt-in-and-current-state-based`.
- **Q2 — interaction**: one `/incubate` entry skill adapts discovery, research, implementation and verification to
  the next useful action. Optional support roles do not create mandatory phases.
- **Q3 — resume**: recommend a project-owned `.devkit/incubation.md` with current facts and the next action. It is
  mutable Markdown, not a Unit, managed asset, approval record or history of discarded choices.

## 3. Proposed Design & Impact

### Distribution and entry

1. Register `incubation = "devkit_catalog.incubation"` through the existing `devkit.bundles` mechanism. Keep it opt-in
   with `auto_select` absent, like the other catalog bundles. No extra runtime dependency or new CLI is introduced.
2. `incubation:core` contains the constitution, one `/incubate` entry skill with references, an incubation guidance
   pointer, three optional subagent contracts and a current-context template available to the skill. It seeds no
   product documents or current context automatically.
3. A clean consumer installs devkit-docs plus devkit-catalog and selects `incubation:core`. The document package brings
   its existing distribution/harness dependencies. The supported path requires no installed devkit-spec distribution.
4. Entry and the pointer inspect the effective development approach through the common interface delivered by
   `PROP-incubation-lifecycle-policy`. They run incubation work only when the result is incubation. A mismatch or
   unreadable policy gives the next configuration action; guidance never silently switches approach or removes SDD.
5. Selection and runtime applicability remain separate. Incubation assets can be present while SDD is selected;
   `/incubate` then explains the mismatch without doing product work. No unconditional instruction redirects every
   task in an existing SDD repository. Explicit removal of spec assets is distinct from installed runtime extensions.
6. Read `get-context incubation` once for the selected entry, and `get-context docs` before document authoring.
   Documents are added when they describe retained behavior or help the next decision, not as a complete set up front.

### Adaptive work loop

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

### Optional support contracts

| Role | Responsibility and return | Write and Git boundary |
| --- | --- | --- |
| `product-clarifier` | Candidate users/problems, alternatives, uncertainties and recommended questions for the coordinator; no invented user decisions. | Read-only; no index or HEAD change. |
| `incubation-researcher` | Evidence for one question, or a bounded feasibility experiment when explicitly assigned, with method, limits and recommendation. | Read-only by default; an experiment writes only the payload's explicit sandbox/prototype boundary; no commits. |
| `usage-reviewer` | Exercise the stated representative flow against expected usage; report observed behavior, evidence, missing coverage and failure conditions. | Read-only source scope; run checks/interactions only in the assigned test environment; no commits. |

Each call has one goal, absolute read/write boundaries, current source/artifact identity and expected output.
Roles are optional: use one when the question or verification scope separates usefully. Availability or selection
of the bundle does not require invoking all roles. The coordinator checks actual diff boundaries and folds evidence
into current context. A failed role result remains failed; it is not a product decision or approval.

### Current context

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

### Interfaces with concurrent proposals

- The lifecycle-policy proposal owns setting location, inspection output, command preconditions and readiness.
  Its draft shared `sdd|incubation` setting is unapproved; this proposal relies only on an inspectable effective
  approach and preservation of independent checks. Before Development, refresh this proposal against its accepted
  interface; an incompatible choice returns to Planning rather than inventing a second policy source.
- `PROP-incubation-sdd-baseline` consumes current goal, retained choices, implementation and verification evidence
  semantically. It need not parse this context filename or require historical records. Voluntary transition is owned
  there; `/incubate` records the user's intent and points to the accepted transition entry when available.
- All three Planning units write separate proposal directories. Implementation remains dependent on the accepted
  policy, and overlapping guides or architecture changes integrate sequentially after a scope comparison.

### Validation scenarios

- **AC-01 — isolated selection**: Given built devkit-docs and devkit-catalog wheels in a clean consumer without
  devkit-spec, when incubation is selected and sync runs, then the skill, pointer, roles and context template deploy
  from their catalog owner, docs formats remain available, and no SDD skill/workflow/envelope requirement is installed.
  Catalog installation without selection deploys no incubation assets. Check receipt and projected role contracts.
- **AC-02 — incomplete idea**: Given only a product goal and partial constraints in a scenario walkthrough, when
  `/incubate` runs, then it uses available answers, asks only missing next-action questions and reaches a research or
  implementation action without a complete backlog, architecture, proposal, Unit or mandatory document set.
- **AC-03 — evidence and iteration**: Given a concrete uncertainty and a representative flow, when research or a
  bounded experiment informs implementation, then the result identifies method, evidence, limits and decision; the
  app flow can be run and exercised. Reconstructing inside the goal changes current code/tests/docs without SDD records,
  while a goal/constraint change requests user direction. Unexecuted checks remain explicitly unverified or skipped.
- **AC-04 — optional delegation**: Given a separable clarification, research or usage-check scope, when a role is used,
  then its payload and result preserve boundaries and evidence and do not invent authority. An inline iteration can
  finish without any role; no prescribed sequence requires all three. Exercise both inline and delegated walkthroughs.
- **AC-05 — resume and ownership**: Given a completed action with retained choices, a limitation and run instructions,
  when another session resumes, then it reads `.devkit/incubation.md`, identifies the next useful action and verifies
  relevant facts without conversation reconstruction. Sync and re-selection preserve existing context bytes; superseded
  experiments can be removed without a historical Unit or immutable decision record. Roles never write the context.
- **AC-06 — applicability and SDD preservation**: Given effective SDD or unreadable approach policy, when `/incubate`
  is invoked, then it stops product work and reports the next configuration action. Given incubation, it uses the common
  policy and document context without weakening independent project checks. Existing SDD entry guidance and its tests
  remain unchanged; installing the catalog alone changes no development approach.

Mechanical checks cover manifest/projection inventories, references, wheel isolation, opt-in selection and context
preservation. Semantic checks use a bounded sample app and synthetic scenario inputs clearly labelled as test data;
record actual commands/interactions, produced context and unmet observations. A text-token assertion alone cannot
establish adaptive discovery or usable resumption. No production app is shipped by this proposal.

### Non-goals

- **Scope Excluded**: Runtime approach-policy implementation, command readiness providers or a second policy source.
- **Scope Excluded**: SDD baseline activation, retroactive delivery records and a new lifecycle/workflow engine.
- **Scope Excluded**: A new wheel, universal app stack, framework scaffold catalog or persistent autonomous service.
- **Scope Excluded**: Mandatory subagent invocation, immutable incubation history and automatic approach switching.

## 4. Lifecycle & Retirement Criteria

Accept the catalog ownership, optional-role and mutable-context direction after Host/user review, then hand off one
feature spec after the prerequisite policy contract is accepted. Retire this proposal only through the authorized
handoff. Before claiming Development complete, pass AC-01 through AC-06, build-wheel isolation, scenario walkthroughs,
relevant lint/types, affected tests and cumulative governance checks. The broader milestone remains open until its
other proposals complete.
