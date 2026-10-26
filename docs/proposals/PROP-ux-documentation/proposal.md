---
id: PROP-ux-documentation
title: UX documents, authoring guidance and use-case-driven review
summary: "Adds a UX document kind for screens and interaction flows linked from use case steps to capabilities, with authoring guidance that leaves the wireframe medium to the project and an isolated reviewer that walks use cases through the screens."
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-26
target_area: documents/
priority: high                        # critical | high | medium | low
size: L                               # S | M | L | XL
planning_effort: high                 # low | medium | high (hint for Planning)
dev_effort: high                      # low | medium | high (hint for Development)
milestone: MS-ux-documentation
depends_on: [SPEC-table-driven-document-kinds]
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
    - guides/
  excludes:
    - Wireframe or mock-up rendering and design tool integrations
    - Visual styling, theming and design tokens
    - Engine- or framework-specific UI verification
    - Usability testing with real users
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

- A UX kind added through the kind definition table of `SPEC-table-driven-document-kinds`, with its templates, an
  entry in `CAP-DOCS-document-model`, browsing, search and the viewer.
- Link fields and the coverage rules chosen in Q2 and Q3, documented in `CAP-GOV-spec-rules`.
- A UX writing instruction in the `spec` bundle, alongside the existing per-kind writing instructions.
- An isolated, read-only UX reviewer subagent and its review skill, following the pattern of the code reviewer, and
  its place in the delivery workflows (`CAP-DLV-delivery-workflows`).
- Non-goals: wireframe rendering, design tool integrations, visual styling, engine- or framework-specific
  verification, usability testing with real users and severity ranking of findings by the reviewer.

## 4. Lifecycle & Retirement Criteria

- On acceptance: recorded with `devkit spec proposal accept`, then handed off to a spec bundle on
  `dev-ux-documentation`; the proposal is deleted there and its decisions become ADRs.
- On decomposition: Planning returns the draft with `needs_decompose: true`, and Backlog creates the children with
  `--decomposed-from PROP-ux-documentation`, keeping the milestone.
- On rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
