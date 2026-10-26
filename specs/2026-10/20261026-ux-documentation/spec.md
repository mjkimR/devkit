---
id: SPEC-ux-documentation
title: UX documents, authoring guidance and use-case-driven review
summary: Adds a UX document kind for screens and interaction flows linked from use case steps to capabilities, with authoring guidance that leaves the wireframe medium to the project and an isolated reviewer that walks use cases through the screens.
status: in-progress
created: 2026-10-26
depends_on:
  - SPEC-table-driven-document-kinds
  - SPEC-foundation-documents
related_capabilities:
  - CAP-DOCS-document-model
  - CAP-DOCS-namespaces
  - CAP-GOV-spec-rules
  - CAP-DLV-delivery-workflows
  - CAP-VIEW-repository-viewer
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-ux-documentation] UX documents, authoring guidance and use-case-driven review

## 1. Problem Statement & Motivation

Handed off from proposal PROP-ux-documentation on 2026-10-26.
- **Preserved Materials**: `docs/materials/2026-10/20261026-ux-documentation` (`MAT-ux-documentation-planning-spike`,
  `MAT-ux-documentation-practice`, `MAT-ux-object-modeling`)
- **Decisions**: `ADR-ux-screen-documents`, `ADR-ux-step-links-and-coverage`, `ADR-ux-review-before-code`,
  `ADR-ux-drafts-before-code`
- Target Docs Blueprint: `PROP-ux-documentation-target` (Living Spec targets for this plan and reconcile.md)

### 1. Background & Hypothesis

Use cases describe what an actor intends at each step and stay free of interface detail (`usecase-writing`
instruction); capabilities own the behavior contracts. Nothing in the Living Spec describes what a person sees and
operates: screens, their content and states, the effect of each interaction and the transitions between screens.
Projects with a user interface keep such specifications as free-form materials or inside capabilities, without
traceability, and agents implement screens with no contract to check against.

Agent-produced interfaces also fail in known ways: layouts converge to generic averages, an agent grades its own work
leniently, and all information ends up on one screen. Practice and recent studies point to a separate evaluator,
graded criteria with evidence, contrasting candidates and a cap on review rounds (`MAT-ux-documentation-practice`).

Hypothesis: a UX document kind at the content-and-states fidelity, linked as use case step → screen → capability,
lets the spec rules check coverage mechanically and lets an isolated reviewer run a cognitive walkthrough of each use
case through its screens. Authoring guidance asks for contrasting candidates and leaves the wireframe medium to the
project, so the text contract stays devkit-owned and checkable.

### 2. Design as decided

- **Kind** (`ADR-ux-screen-documents`): one kind `ux`, prefix `UX`, at `docs/ux/<area>/UX-<slug>.md` and
  `docs/packages/<name>/ux/<area>/UX-<slug>.md`, one row of the kind definition table. Each document is one interface
  element (`element: screen | modal | panel`) with Purpose, Content, States, Interactions
  (`Trigger | Step | From | To | Target | Capability | Feedback`) and an optional Evidence section. Statuses `draft`,
  `active`, `deprecated`.
- **Links and checks** (`ADR-ux-step-links-and-coverage`): a use case step cites its screen's UX ID in prose; a UX
  document lists `usecases` and `capabilities`, and each interaction's Step cell names the served step. The
  error-severity `RULE-ux-links` reports contradictions; the warning-severity `RULE-ux-coverage` reports steps without
  a screen and interactions without a step.
- **Authoring guidance**: a `ux-writing` instruction; the register `docs/steering/ux-objects.md` is created with a
  project's first UX document and never seeded.
- **Review** (`ADR-ux-review-before-code`): a read-only `ux-reviewer` with the `spec-ux-review` skill, `ux-review-NN`
  envelopes, at most two rounds and a closing envelope, as an optional delegation before code.
- **Timing** (`ADR-ux-drafts-before-code`): screens are drafted before code (Screens sections of `target-docs.md` or
  `spec.md`) and written to `docs/ux/` at `spec-sync`.

## 2. User Stories

- **US-1**: As a project maintainer with a user interface, I want one document kind for screens, modals and panels so
  that the Living Spec holds what a person sees and operates, linked to the use case steps and capabilities it serves.
- **US-2**: As an agent implementing a screen, I want the spec rules to report contradictions between screens and use
  cases and warn about steps without a screen so that the screen contract and the task flow stay in step.
- **US-3**: As an agent drafting screens, I want an authoring instruction and drafts before code so that the screen
  contract exists, with contrasting candidates in Planning, before the code that implements it.
- **US-4**: As the Host, I want an isolated read-only reviewer that walks each use case through the drafted screens and
  scores a rubric with evidence so that the author's lenient self-review is not the only check.

## 3. Non-Goals

1. **Scope Excluded**: wireframe or mock-up rendering and design tool integrations; the medium stays the project's.
2. **Scope Excluded**: visual styling, theming and design tokens; screens cite the project's steering style files.
3. **Scope Excluded**: engine- or framework-specific UI verification, and usability testing with real users.
4. **Scope Excluded**: workflow engine changes in `packages/devkit/` (check primitives, closable envelope kinds) and a
   stage switched on by content; the UX review is an optional delegation (`ADR-delivery-classification`).
5. **Scope Excluded**: severity ranking of UX review findings.
6. **Scope Excluded**: extension-to-state coverage, a flow document and a derived navigation listing.
7. **Scope Excluded**: use cases or UX documents for devkit's own viewer, and a seeded `docs/steering/ux-objects.md`.
8. **Scope Excluded**: `entrypoints` on UX documents (`CAP-TRACE-code-entrypoints` keeps capabilities and use cases).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The kind table holds the UX row

- **Given** the kind definition table
- **When** it is read through `definitions()` and the ID grammar
- **Then** it holds a `ux` row after `usecase` with prefix `UX`, directory `ux`, Living Spec membership, area scoping,
  `every-root` format scope, a heading token, an always-required summary, no `entrypoints`, no terminal status,
  default status `draft` and no relation field; `kind_of("UX-login")` is `ux` and `ID_SOURCE` lists `UX` after `UC`.

### [AC-02] RULE-id-convention checks the UX location

- **Given** UX documents at `docs/ux/account/UX-login.md` (with `area: account`), at
  `docs/packages/example/ux/account/UX-pick.md` in a registered namespace, at `docs/ux/UX-flat.md` and at
  `docs/ux/account/screen-login.md`
- **When** `RULE-id-convention` checks them
- **Then** the first two pass; the third is reported `Invalid partition path: UX document must be stored at
  docs/ux/{area}/UX-{slug}.md` and the fourth `Invalid partition path: file name must be UX-{slug} ...`; an
  `area` that differs from the directory is reported and fixable.

### [AC-03] A UX document is indexed, listed, searched and grouped

- **Given** a fixture repository with `docs/ux/account/UX-login.md` (`title`, English `summary`, `area`, `element`,
  `status`)
- **When** `devkit spec resolve UX-login`, `devkit spec list ux` and `devkit spec search "login screen"` run, and the
  viewer's `bookGroup` and reference linking read the document
- **Then** resolve prints `[DOCUMENT: UX-login kind=ux ...]`, list prints its `[DOCUMENT: UX-login ...]` line, search
  returns it as a hit, `bookGroup` returns `UX`, `bookGroups` holds `UX` after `Use Cases`, and a bracketed UX-login
  reference in another page links to it; `RULE-spec-format` and `RULE-document-summary` report a UX document without
  `status` or `summary`.

### [AC-04] RULE-ux-links checks a UX document's own shape

- **Given** `RULE-ux-links` (error severity)
- **When** a UX document has no `element`, an `element` other than `screen`, `modal` or `panel`, no Interactions
  section, an Interactions section without a table whose header is exactly `Trigger | Step | From | To | Target |
  Capability | Feedback`, a Step cell that is neither empty nor `` `UC-<slug>` <key> ``, or a Target cell that is
  neither empty, a UX ID of a UX document, `close`, `back` nor `end`
- **Then** each case is one violation on the UX document, and a well-formed document gives none.

### [AC-05] RULE-ux-links checks the links between a screen and its use cases

- **Given** a use case whose step 2 cites UX-login and a UX document UX-login listing it in `usecases`
- **When** an interaction's Step cell names a step key the use case does not have, names a step that does not cite
  UX-login, or names a use case `usecases` does not list; a `usecases` entry has no Step cell naming it; or a use
  case step cites UX-login whose `usecases` does not list that use case
- **Then** each case is one violation, and the consistent pair gives none.

### [AC-06] RULE-ux-links checks exits and modal close

- **Given** screens cited by a use case's steps
- **When** a `screen` has no interaction whose target leaves it (another UX ID, `close`, `back` or `end`) and is cited
  by no step that is the last main-scenario step, an extension that ends the use case or a step whose next step
  cites no screen; or a `modal` has no `close` or `back` row
- **Then** the screen is reported `screen has no exit` and the modal `modal has no close or back interaction`; a
  `panel` is never reported for an exit; a screen cited by the last step needs none.

### [AC-07] RULE-ux-links checks reachability per use case

- **Given** a use case whose step 1 cites UX-a, step 2 cites UX-b, step 3 cites no screen and step 4 cites UX-c,
  and whose extension 2a cites UX-d
- **When** UX-a has no interaction targeting UX-b
- **Then** UX-b is reported `not reachable from an entry of <UC>`; UX-c (after a step that cites no screen,
  off-screen re-entry) and UX-d (cited by an extension) are entries and not reported; UX-b is not reported for an
  exit (its next step cites no screen); with UX-a targeting UX-b, nothing is reported; a system step between two
  screens that cites the screen of its response makes that screen reachable only through an interaction; a panel
  named in a reached screen's Content contributes its interactions as edges and is never reported unreachable.

### [AC-08] The step parser tolerates the use case formats in use

- **Given** a use case with an intro paragraph before step 1, a non-indented prose paragraph inside Extensions, the
  escaped `**\*a.**` key, indented continuation lines and `Covers` lines in its acceptance scenarios
- **When** `RULE-ux-links` and `RULE-ux-coverage` parse its steps
- **Then** the steps and extension keys are `1`..`N`, `2a` and `*a` (a Step cell may write `*a` or `\*a`), the
  intro and the free prose belong to no step, a citation on a continuation line belongs to its step, and the
  `Covers` lines are not steps; every current use case of this repository parses without error.

### [AC-09] A two-document report lands where the run looks

- **Given** a step-key contradiction between UX-login and its use case
- **When** the run targets the UX document, only the use case, or neither
- **Then** the violation is on the UX document, on the use case (at the step's line), or absent; findings about the
  UX document alone (element, table, target, modal close) are reported only on the UX document.

### [AC-10] RULE-ux-coverage warns about uncovered steps and stepless interactions

- **Given** `RULE-ux-coverage` (warning severity) and a UX document listing a use case
- **When** a main-scenario step or an extension of that use case cites no UX ID, or an interaction's Step cell is
  empty
- **Then** the step is reported once (on the first listing UX document the run targets, else on the use case) and the
  interaction on its UX document's row line, each as a warning; a use case no UX document lists is never reported.

### [AC-11] The template and the seed carry the kind

- **Given** the `spec` bundle
- **When** its `templates/ux.md`, its `docs-skeleton` seed and `AGENTS.md.jinja` are read
- **Then** the template has `element`, `usecases`, `capabilities`, the status values `draft | active | deprecated`
  and the Purpose, Content, States, Interactions (the seven-column header) and Evidence sections; the seed holds
  `docs/ux/README.md` and lists `ux/` in `docs/README.md`, and seeds no `steering/ux-objects.md`; the constitution's
  template list names `ux`.

### [AC-12] Authoring guidance covers screens and step citations

- **Given** the `ux-writing` and `usecase-writing` instructions and the bundle manifest
- **When** they are read
- **Then** `ux-writing` is an instruction asset in the `core` preset that asks for two or three contrasting
  candidates in Planning only (Development takes the recommended one and records the others as an assumption), rules
  out character-cell layouts, names objects by glossary terms and creates `docs/steering/ux-objects.md` with the
  first UX document, cites steering style files without restating them, leaves the medium to the project, and says a
  system step cites the screen of its response; `usecase-writing` says a step may cite the screen it happens on.

### [AC-13] The ux-reviewer role and its skill

- **Given** the `spec` bundle's role contracts
- **When** `subagents/ux-reviewer.md` and `skills/spec-ux-review/SKILL.md` are read
- **Then** the contract binds `skill: spec-ux-review`, is isolated, optional and read-only (`x-git-actions: [read]`,
  `disallowedTools: [Write, Edit]`, Codex `read-only`) with the `general-high` profile and `high` effort; the skill
  defines the per-step walkthrough questions, the rubric items R1-R6 scored 0, 1 or 2 with evidence below 2, the
  link-rule items as the reviewer's own judgment outside the rubric, no severity, `ux-review-NN` envelopes, at most
  two rounds and the closing envelope marking each finding `resolved` or `waived`.

### [AC-14] The workflows place the drafts and the review before code

- **Given** `spec-specify` (with its feature and bugfix references), `spec-sync`, the effort reference, `sdd-proposal`,
  the planning reference and the target-docs blueprint `devkit spec proposal new` writes
- **When** they are read
- **Then** `spec-specify` defines a Screens section of `spec.md` in the UX template's shape with new IDs in plain
  text, carries a handed-off `target-docs.md` Screens draft into it and offers the optional UX review before
  `spec-plan` (feature) or `plan-tasks` (bugfix); `spec-sync` writes each drafted screen to `docs/ux/`, the step
  citations to the use cases and the drafted register rows to `docs/steering/ux-objects.md`, and lists each in
  `reconcile.md`; the effort table names the UX review at `medium` and `high` when screens change; the acceptance
  request lists the `ux-review` rounds and their open findings; the blueprint has a Screens drafts section.

### [AC-15] The Living Spec describes the delivered contract

- **Given** this repository after the change
- **When** `devkit rules check` and `devkit sync --check` run
- **Then** `CAP-DOCS-document-model`, `CAP-DOCS-namespaces`, `CAP-GOV-spec-rules`, `CAP-DLV-delivery-workflows` and
  `CAP-VIEW-repository-viewer` describe the kind, the two rules, the role, its envelope and placement, and the book
  group; `docs/steering/glossary.md` defines **UX document** and **UX object register** within the steering body cap;
  both commands exit `0`.

## 5. Assumptions

- The handed-off premises hold on base `02615579`: the kind definition table of `SPEC-table-driven-document-kinds`
  and the flat `docs/steering/` of `SPEC-foundation-documents` are on `main`, and `docs/glossary.md` moved to
  `docs/steering/glossary.md`, which replaces the proposal's boundary path (the agreed boundary, not an extension).
- The rule IDs are the ADR's working names, `RULE-ux-links` and `RULE-ux-coverage`, with assets `ux-links` and
  `ux-coverage` in the `core` preset.
- A Step cell holds one or more `` `UC-<slug>` <key> `` pairs separated by commas; an empty cell, `-` or `—` is
  empty. A Target cell is empty (the interaction stays on the screen), a UX ID with or without backticks, `close`,
  `back` or `end`; a target naming the screen itself is not an exit.
- An extension's next step is the step named by `resumes at [step] <key>`, or for `resumes at the same step` the step
  it branches from; `the use case ends`, no resume phrase, or a `*a` resuming at the same step ends the use case.
- Main steps are `N.` items at column 0, so a nested numbered list continues its step (`review-01` finding 2).
- The use case sections are found by the H2 headings containing `Main Success Scenario` and `Extensions`; steps are
  `N.` list items and extensions `- **<key>.**` bullets; a citation is a body reference of the index whose canonical
  target is a UX document, so aliases and the bracket form count.
- A panel is "named" by a screen when the screen's Content section cites the panel's UX ID.
- The `ux-reviewer` presets `general-high` and `high`, like `code-reviewer`, because it judges content rather than
  verifying a record.
- The viewer book group is titled `UX`; the bracket-ID pattern gains `UX` only (the other stale prefixes stay with
  their own feedback record).
- No use case of this repository changes and no screens are drafted here, so this spec has no Screens section.

## 6. Source feedback

None carried: the two proposal feedback records (`FB-boundaries-cannot-name-prerequisite-paths`,
`FB-plan-branch-depends-on-not-relocated`) are resolved.
