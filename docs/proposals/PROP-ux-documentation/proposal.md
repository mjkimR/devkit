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
    - packages/devkit-viewer/tests/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - docs/capabilities/delivery/
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
  document lists `usecases` and `capabilities`, and each interaction names the served step key. A new UX coverage
  rule in `CAP-GOV-spec-rules` reports uncovered steps, interactions serving no step, link disagreement and the flow
  graph defects (unknown targets, screens without an exit, a modal without `close`, unreachable screens).
- **Authoring guidance**: a `ux-writing` instruction in the `spec` bundle: two or three contrasting candidates for
  the user to choose from where a screen's arrangement is open, no character-cell layouts, objects named by glossary
  terms with a separate UX object table, and the medium left to the project.
- **Review** (`PADR-ux-review-before-code`): an isolated, read-only `ux-reviewer` subagent with a `spec-ux-review`
  skill: a cognitive walkthrough of each linked use case plus a 0/1/2 rubric with evidence, the coverage rule's
  results reported as facts, no severity, `ux-review-NN` envelopes and at most two rounds, run as an optional
  delegation before code (`CAP-DLV-delivery-workflows`).
- **Timing** (`PADR-ux-documents-written-at-specify`): Planning drafts screens in `target-docs.md`; Development
  writes them to `docs/ux/` at `specify`, before code, and `reconcile.md` confirms them.
- Non-goals: wireframe rendering, design tool integrations, visual styling, engine- or framework-specific
  verification, usability testing with real users, severity ranking of findings by the reviewer, and workflow engine
  changes.

## 4. Lifecycle & Retirement Criteria

- On acceptance: recorded with `devkit spec proposal accept`, then handed off to a spec bundle on
  `dev-ux-documentation`; the proposal is deleted there and its decisions become ADRs.
- On decomposition: Planning returns the draft with `needs_decompose: true`, and Backlog creates the children with
  `--decomposed-from PROP-ux-documentation`, keeping the milestone.
- On rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.

## 5. Planning Findings

Evidence: `MAT-ux-documentation-planning-spike` (spike over devkit's code and contracts, from `scout-01` to
`scout-03`), `MAT-ux-documentation-practice` and `MAT-ux-object-modeling` (the user's research).

- **Q1**: a kind is known only by its prefix; one prefix costs one table row and one stem rule, two prefixes double
  rows, directories and relation fields. The use case already holds a task's step order and extensions, so the
  interactions' targets give the transitions without a flow document. Glossary columns would silently disable the
  Owner check; a separate table under its own header does not.
- **Q2**: all 13 current use cases number steps and extensions regularly; no rule maps a body reference to a step.
  Citing UX IDs in step prose reuses reference resolution and alias rewriting; one step segmenter is new.
- **Q3**: with targets in the interactions table, the flow graph checks cost little beyond orphans; not every step
  happens on a screen, so the strictness of "step without a screen" is a user decision.
- **Q4**: a new subagent is a valid role without engine code, but a conditional stage needs a new check primitive in
  `devkit-agt`, and the `review` kind would share the code-review round state. Severity is bundle procedure, so a
  separate `ux-review` kind keeps the no-severity non-goal.
- **Q5**: the medium stays with the project; an optional Evidence section lets the reviewer read a wireframe or
  screenshot when one exists.
- **Q6**: one proposal hands off to exactly one spec; the reviewer depends on the template and step keys, so the
  recommendation keeps one proposal with ordered tasks (a user question).
- **Timing**: `spec-sync` writes `docs/` after code review, too late for a screen contract; a user question.

### Dependencies and order

- `PROP-table-driven-document-kinds` (`depends_on`) is developed first. Assumed of its table, to re-check before
  handoff against its accepted design: it carries the prefix, kind, location, Living Spec membership and directory,
  namespace scope, accepted relation fields with their target kinds, summary requirement and entrypoint
  participation; it removes the binary kind fallbacks. Assumed not carried, so owned here: the bidirectional pair
  logic of `RULE-traceability-link`, per-kind stem rules and messages, `spec_format` scope, templates and seeds, the
  viewer's book group and bracket-ID pattern. Where the accepted table differs, this proposal's Development adapts.
- `PROP-foundation-documents` is not a prerequisite. It moves `docs/glossary.md` (and the viewer's glossary group)
  to `docs/foundation/`; the UX object table and the new terms go to whichever path is current at Development, and
  its excluded table-format change is owned here. Both proposals also own `packages/devkit-spec/src/devkit_spec/features/`,
  the `spec` bundle and `docs/capabilities/documents/`; Development rebases on whichever lands first.
- The viewer's bracket-ID pattern still lists the removed `US` prefix and omits `UC`, `MS` and `FB`
  (`packages/devkit-viewer/frontend/src/lib/api/documents.ts:246`); recorded as feedback for the table proposal's
  viewer step.

### Planning decisions

- `dev_effort` is `medium`: the change creates a document kind and spans packages, and has no irreversible effect or
  external consumer (`effort` reference); the Host may raise it at handoff.
- Boundaries add `docs/glossary.md` (moved by `PROP-foundation-documents` if it lands first), and
  `.devkit/installation.json` and `AGENTS.md` for the `devkit sync` the new bundle assets imply. Workflow engine
  changes are excluded.

