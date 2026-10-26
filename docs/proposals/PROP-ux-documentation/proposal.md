---
id: PROP-ux-documentation
title: UX documents, authoring guidance and use-case-driven review
summary: "Adds a UX document kind for screens and interaction flows linked from use case steps to capabilities, with authoring guidance that leaves the wireframe medium to the project and an isolated reviewer that walks use cases through the screens."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-26
target_area: documents/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
milestone: MS-ux-documentation
depends_on: [PROP-table-driven-document-kinds]
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/
    - packages/devkit-spec/tests/
    - packages/devkit-viewer/src/devkit_viewer/features/browse/
    - packages/devkit-viewer/frontend/src/lib/
    - packages/devkit-viewer/src/devkit_viewer/static/
    - packages/devkit-viewer/tests/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - docs/capabilities/delivery/
    - docs/capabilities/viewer/
    - docs/usecases/
    - docs/architecture/
    - docs/glossary.md
    - guides/
    - .devkit/installation.json
    - AGENTS.md
  excludes:
    - Wireframe or mock-up rendering and design tool integrations
    - Visual styling, theming and design tokens
    - Engine- or framework-specific UI verification
    - Usability testing with real users
    - Workflow engine changes in packages/devkit/ (check primitives, closable envelope kinds)
    - Use cases or UX documents for devkit's own viewer
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-ux-documentation] UX documents, authoring guidance and use-case-driven review

## 1. Background & Hypothesis

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

## 2. Technical Spike Questions

Options and their evidence are in `MAT-ux-documentation-practice` (sections 1-5) and `MAT-ux-object-modeling`
(options 6a-7b).

- **Q1 (documents)**: Which documents make up the kind: per-screen specifications and a flow document (option 1c), or
  screens only? Which sections are required (purpose, content priority, states, interactions with their effect,
  exits), and what is the ID, path and template of each? Do screens cite glossary terms that carry their
  representations and CTAs per role (6b), and how is content written without a drawing (prose regions and a content
  tree, 7a)?
- **Q2 (links)**: How does a use case step name its screen: in step prose like capability citations today, or through
  a structured field? How does a screen name the capabilities whose state it presents, and must the links be
  bidirectional like `RULE-traceability-link`?
- **Q3 (checks)**: Which mechanical checks ship: orphans only (2a), the flow graph checks (2b) or also extension-to-state
  coverage (2c)? Each needs a fixed table schema in the flow document and parsing of use case steps.
- **Q4 (review)**: Which review: a walkthrough-only reviewer (3a), a walkthrough plus a 0/1/2 heuristic rubric with
  cited evidence (3b), or merged independent runs (3c)? Which rubric, how are deterministic results excluded from
  judgment, and where does the review sit in the delivery workflows (a stage, an optional delegation, or both)?
- **Q5 (authoring and medium)**: Does the authoring guidance require contrasting candidates and a round cap (4b, 4c)?
  Is the wireframe medium only referenced (5a), or does a screen declare an evidence slot the reviewer reads (5b)?
- **Q6 (decomposition)**: Can the kind with its checks, the authoring guidance and the review be delivered and verified
  as one spec, or should Planning return this draft for decomposition into separate proposals?

## 3. Proposed Design & Impact

The Planning recommendation, pending the user's answers (§5); `target-docs.md` is the blueprint.

- **Kind** (`PADR-ux-screen-documents`): one kind `ux`, prefix `UX`, at `docs/ux/<area>/UX-<slug>.md` and per
  namespace `docs/packages/<name>/ux/<area>/`, added as one row of the kind definition table of
  `PROP-table-driven-document-kinds`, with a template, `docs-skeleton` seed, browsing, search and a viewer book
  group. Each document is one interface element (`element: screen | modal | panel`) with Purpose, Content (prose
  region rules and a content tree), States, Interactions (`Trigger | Step | From | To | Target | Capability |
  Feedback`) and an optional Evidence section for the project's own wireframe medium. The use case carries the task
  flow; there is no flow document. Statuses `draft`, `active`, `deprecated` (no terminal status).
- **Links and checks** (`PADR-ux-step-links-and-coverage`): a use case step cites its screen's UX ID in prose; a UX
  document lists `usecases` and `capabilities`, and each interaction's Step cell names the served step
  (`` `UC-<slug>` 2a ``). An error rule reports contradictions (invalid element, unknown or non-citing step keys,
  link disagreement, unknown targets, missing exits and modal close, unreachable screens); a warning rule reports
  steps without a screen and interactions without a step. Both are documented in `CAP-GOV-spec-rules`.
- **Authoring guidance**: a `ux-writing` instruction in the `spec` bundle: two or three contrasting candidates for
  the user in Planning where a screen's arrangement is open (Development takes the recommended one and records the
  others as an assumption), no character-cell layouts, objects named by glossary terms with a seeded UX object table,
  and the medium left to the project.
- **Review** (`PADR-ux-review-before-code`): an isolated, read-only `ux-reviewer` subagent with a `spec-ux-review`
  skill: a cognitive walkthrough of each linked use case plus a six-item 0/1/2 rubric with evidence, the link rules'
  results reported as facts, no severity, `ux-review-NN` envelopes, at most two rounds and a closing envelope, run as
  an optional delegation before code (`CAP-DLV-delivery-workflows`).
- **Timing** (`PADR-ux-drafts-before-code`): screens and the step citations they need are drafted before code in
  `target-docs.md` or a Screens section of `spec.md`, with IDs the change creates in plain text; `spec-sync` writes
  `docs/ux/` and the use case changes, and the link rules check them at `living-spec-draft`. The review runs on the
  drafts (in Planning, or inside `specify` before `spec-plan`).
- Non-goals: wireframe rendering, design tool integrations, visual styling, engine- or framework-specific
  verification, usability testing with real users, severity ranking of findings by the reviewer, a stage switched on
  by content, and workflow engine changes.

## 4. Lifecycle & Retirement Criteria

- Acceptance requires the user's answers to the Planning questions folded into the PADRs and an accepted
  `PROP-table-driven-document-kinds`; the handoff waits for its Development to be integrated (§5).
- Development shows: a UX document in a fixture repository indexed, listed, searched and grouped in the viewer; each
  report of both UX rules by a rule test, including the element and Interactions-table cases, off-screen re-entry
  and the step-format deviations; the role and
  skill contracts by the role-contract tests; and the viewer frontend checks with the committed page rebuilt.
- On acceptance: recorded with `devkit spec proposal accept`, then handed off to a spec bundle on
  `dev-ux-documentation`; the proposal is deleted there and its decisions become ADRs.
- On decomposition: Planning returns the draft with `needs_decompose: true`, and Backlog creates the children with
  `--decomposed-from PROP-ux-documentation`, keeping the milestone.
- On rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.

## 5. Planning Findings

Evidence: `MAT-ux-documentation-planning-spike` (spike over devkit's code and contracts, from `scout-01` to
`scout-03`), `MAT-ux-documentation-practice` and `MAT-ux-object-modeling` (the user's research); `challenger-01`
(12 findings) is folded below.

- **Q1**: a kind is known only by its prefix; one prefix costs one table row and one stem rule, two prefixes double
  kinds, directories and relation fields. The use case already holds a task's step order and extensions, so the
  interactions' targets give the transitions without a flow document. Glossary columns would silently disable the
  Owner check; a separate table under its own header does not, so the UX object table is seeded, not added to
  devkit's own glossary.
- **Q2**: all 13 current use cases number steps and extensions regularly; no rule maps a body reference to a step.
  Citing UX IDs in step prose reuses reference resolution and alias rewriting; one step segmenter is new. Whether use
  cases carry UX IDs at all is a user question (`step-screen-link`).
- **Q3**: with targets in the interactions table, the flow graph checks cost little beyond orphans once each
  element's meaning is defined (panels exempt, end-of-task screens, `close`, `back` and `end` targets). Not every step
  happens on a screen, so the strictness of "step without a screen" is a user question (`coverage-strictness`).
- **Q4**: a new subagent is a valid role without engine code; a stage switched on by content is excluded by
  `ADR-delivery-classification`; the `review` kind would share the code-review round state. Severity is bundle
  procedure, so a separate `ux-review` kind keeps the no-severity non-goal, with its own closing record.
- **Q5**: the medium stays with the project; an optional Evidence section lets the reviewer read a wireframe or
  screenshot when one exists. Contrasting candidates are a Planning activity, because Development asks the user no
  direction question (`CAP-DLV-delivery-workflows` rule 7).
- **Q6**: one proposal hands off to exactly one spec; the reviewer depends on the template and step keys, so the
  recommendation keeps one proposal with ordered tasks (a user question).
- **Timing**: `spec-sync` writes `docs/` after code review, and a UX document written early links use case changes
  that do not exist yet; drafts before code with the Living Spec at sync is recommended (a user question).

### Dependencies and order

- `PROP-table-driven-document-kinds` (`depends_on`) is developed first, by the user's decision. This proposal's
  `plan-accept` request waits until that proposal is accepted, so a return to `spike` stays available, and the Host
  re-checks the assumptions below against its accepted design then. The handoff waits until its Development is
  integrated; if it is decomposed, until every child that carries the kind table is integrated. If it is rejected,
  this proposal returns to `spike` for the kind registration.
- Assumed of its table: it carries the prefix, kind, location, Living Spec membership and directory, namespace scope,
  accepted relation fields with their target kinds, summary requirement and entrypoint participation, and it removes
  the binary kind fallbacks. Assumed not carried, so owned here: the bidirectional pair logic of
  `RULE-traceability-link`, per-kind stem rules and messages, `spec_format` scope, templates and seeds, the viewer's
  book group and bracket-ID pattern. Where the accepted table differs, this proposal's Development adapts.
- `PROP-foundation-documents` is not a prerequisite. It moves `docs/glossary.md`, the seeded glossary and the
  viewer's glossary group to `docs/foundation/`; the seeded UX object table and devkit's new terms go to whichever
  path is current at Development. Both proposals also own `packages/devkit-spec/src/devkit_spec/features/`, the
  `spec` bundle and `docs/capabilities/documents/`; Development rebases on whichever lands first.
- `FB-viewer-bracket-id-prefixes-stale` records that the viewer's bracket-ID pattern lists the removed `US` prefix and
  omits `UC`, `MS` and `FB`; the table proposal's viewer step can absorb it, and this proposal adds `UX` either way.

### Planning decisions

- The PADR "UX documents written at specify" is withdrawn: written alone, UX documents in `docs/` link use case steps and
  IDs that `spec-sync` writes only later (`challenger-01` finding 1). `PADR-ux-drafts-before-code` replaces it, and
  the contract-slice alternative stays an option of `ux-document-timing`.
- `dev_effort` is `medium`: the change creates a document kind and spans packages, and has no irreversible effect or
  external consumer (`effort` reference); the Host may raise it at handoff.
- Boundaries add `docs/glossary.md` for the new terms. `RULE-proposal-boundaries` admits no path that does not
  exist yet, and naming the parent `docs/` would own the whole Living Spec, so the Host replaces the entry with the
  moved glossary path before requesting `plan-accept` if `PROP-foundation-documents` has moved it by then, and
  otherwise records the moved path as a scope extension of the spec's `_Boundary:` after handoff. Boundaries also
  add `docs/capabilities/viewer/`, the committed viewer build `packages/devkit-viewer/src/devkit_viewer/static/`, and
  `.devkit/installation.json` and `AGENTS.md` for the `devkit sync` the new bundle assets imply.
