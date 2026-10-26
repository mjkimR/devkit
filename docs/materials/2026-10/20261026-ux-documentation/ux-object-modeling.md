---
id: MAT-ux-object-modeling
title: Object modeling and text layout for UX specifications
summary: "Reviews object-oriented UX (OOUX/ORCA), lifecycle states, text-only layout descriptions and coded prototypes as inputs to the UX document kind, separating sourced claims from practitioner opinion and listing the options they add for Planning."
created_at: 2026-10-26
---

# [MAT-ux-object-modeling] Object modeling and text layout for UX specifications

Research input for `MS-ux-documentation`, complementing `MAT-ux-documentation-practice`. It condenses the user's own
exploratory research (LLM-assisted conversations and a generated survey) after a source check: claims are kept when a
source supports them, marked as opinion when only practitioners assert them, and dropped otherwise (section 8). Little
of this area has controlled evidence; most of it is method literature and practitioner experience.

Two problems are easy to mix up and are kept apart here. This material is about specifying interfaces that an agent
builds and a reviewer checks. Designing the interface of a product whose own users delegate work to an AI agent
(agentic UX, generative UI, approval checkpoints) is a different problem; section 7 notes it only to set it aside.

## 1. OOUX and ORCA

Object-oriented UX models the objects users think about before designing screens. Sophia Prater coined and
popularized it as a UX method ([A List Apart, 2015](https://alistapart.com/article/object-oriented-ux/)), building on
older object-oriented interface work such as IBM's CUA guidelines of 1991-92 (Theo Mandel and others). Its process,
ORCA, names the four things modeled: **Objects**, **Relationships** (with cardinality and nesting), **Calls to action**
per object and role, and **Attributes**, worked through in four rounds: discovery, requirements, prioritization and
representation (Prater's own posts).

What it offers a text specification:

- **Fixed object names.** One name per concept across use cases, screens and code reduces the drift where the same
  thing is a "post", a "card" and an `Article`. devkit's glossary already has this shape: each row of
  `docs/glossary.md` gives the `Term`, its `Definition`, the `Owner` capability, the rejected synonyms to `Avoid`
  and the `Code identifiers`. That is the naming half of an OOUX object list, so a UX object list can extend the
  glossary instead of starting a separate register (section 8, option 6b).
- **Representations instead of per-screen content.** An object is defined once with a small set of representations
  (for example a compact card, a row and a full detail view) and their attribute priority; screens then reference a
  representation instead of re-listing fields. This keeps several screens consistent, and it is the part of OOUX that
  maps most directly onto the "content and hierarchy" section of a screen specification.
- **Calls to action per object and role.** The CTA matrix lists who may do what to which object, which gives the
  reviewer a list to check screens against.

Limits:

- **Not a schema.** The objects often align with domain entities and API resources, but they model the user's mental
  model. Prater herself notes that database objects are not necessarily how users think
  ([Creative Bloq interview](https://www.creativebloq.com/features/perfect-object-oriented-ux), wording seen through
  secondary snippets). A 1:1 mapping to tables, endpoints or tool signatures is a convenient default, not a property
  of the method.
- **States without transitions.** OOUX does treat states: Prater's 2015 example gives an object the states posted, in
  progress, closed and closed with feedback, and round 2 examines attributes for conditional logic. What it lacks is a
  notation for transitions and for the preconditions of a CTA. Section 2 covers that gap.
- **The object map is human work.** One practitioner report found that LLMs produced poor object maps and concluded
  that people should write the structure and use AI for mock data, purpose statements and edge cases ("texture, not
  bones"; [Konovalov](https://medium.com/@lex.konovalov/use-ai-for-texture-not-bones-notes-from-an-ooux-misadventure-6ed0ef2bd49e),
  anecdotal). The same author calls a human-made OOUX document good context for agent-written frontend code.
- **Up-front cost.** A complete ORCA pass over a whole product is a large document. Scoping the object list to the
  objects the specified use cases touch keeps it proportionate (practitioner opinion).

## 2. Lifecycle states and screen states

Two kinds of state need different treatment:

- **Object lifecycle states** (a proposal is `draft`, `reviewing`, `accepted` or `rejected`) and the transitions
  between them, with guards. Statecharts (Harel, 1987, *Science of Computer Programming* 8(3)) are the established
  formalism, applied to user interfaces by Horrocks (1999). In Markdown, a transition table (from, event, guard, to)
  carries the same information and can be parsed. Where a capability already owns the lifecycle, the UX document
  should cite it, not restate it.
- **Screen states** of a single view: at least empty, loading, error or blocked, and populated; `MAT-ux-documentation-practice`
  section 1 adds disabled and "empty after processing". Which states a screen must declare is a Q1 decision; a fixed
  mandatory set per screen may not fit every screen.

Unavailable actions: NN/g asks that disabled controls be used sparingly, stay accessible and explain why they are
disabled ([NN/g](https://www.nngroup.com/videos/why-disabled-buttons-hurt-ux-and-how-to-fix-them/)). The common rule of
thumb (disable when the user should know the action exists, hide when it does not concern them) comes from
[Smashing Magazine, 2024](https://www.smashingmagazine.com/2024/05/hidden-vs-disabled-ux/), not from NN/g. A screen
specification can record this choice per CTA.

The extension → state coverage check (`MAT-ux-documentation-practice` option 2c) needs exactly these state IDs, so a
state naming convention would serve both the specification and that check.

## 3. Describing layout without a drawing

Character-cell (ASCII) layouts are excluded. In the user's own projects they were too inexpressive for nested or
responsive layouts, and agents treated the sketch as the target: they forced the implementation to reproduce its
boxes and proportions and made odd changes to do so. The consumer draft in `MAT-ux-documentation-practice` section 5
forbids detailed ones for the same reason (agents copy them as fixed coordinates). This is first-hand and
practitioner experience; no credible study compares text layout forms for LLM UI generation, so the comparison below
is design reasoning, not evidence.

| Form | What it carries | Fit for a devkit-owned contract |
| --- | --- | --- |
| Prose region rules | Regions, their order and priority, behavior on narrow viewports, sticky or scrolling regions | Good when kept relative ("primary", "secondary", "beside", "below"); exact proportions are medium-specific |
| Content tree | Regions nested with the object representations and CTAs they show, plus conditions ("empty: …", "only for role …") | Good; it is the OOUX representation step written as a hierarchy, independent of the UI stack |
| Component tree | Named implementation components and library parts (for example a web component library) | Project-owned; it fixes the implementation and assumes a stack, while some consumers build engine UIs |

A content tree with conditions written next to its nodes also keeps the screen states of section 2 beside the content
they affect. Proportions, breakpoints and component names belong to the project (option 1b in
`MAT-ux-documentation-practice`).

## 4. Wireframes and coded prototypes

The research argued that, when agents code screens quickly, traditional wireframes can be skipped in favor of
reviewing working output. The evidence supports a narrower reading:

- Reviewing a running interface finds things a static picture does not: the evaluator in Anthropic's long-running
  harness clicks through the application with Playwright rather than scoring a screenshot
  ([Anthropic, 2026](https://www.anthropic.com/engineering/harness-design-long-running-apps)). NN/g recommends testing
  AI-coded prototypes earlier for complex interactions, and warns that such prototypes "may look complete while
  introducing all sorts of assumptions"; its own case study started from wireframes
  ([NN/g, 2026](https://www.nngroup.com/articles/test-earlier-with-ai/)).
- Mock-ups alone show the happy path and hide error, edge and consistency states (the "Figma trap", term attributed to
  ASDLC; [Futurice, 2026](https://www.futurice.com/blog/spec-driven-design)). This argues for a text contract, not
  against pictures.
- Polish has costs: people give fewer negative reactions to high-fidelity prototypes
  ([NN/g](https://www.nngroup.com/articles/ux-prototype-hi-lo-fidelity/)), and several parallel candidates give better
  and more diverse results than one refined concept (Dow et al., ACM TOCHI 2010). A single polished build invites early
  approval.
- No controlled study was found showing that text specifications produce better generated UI than images or
  wireframes. Figma states that screenshots alone are insufficient context, which is a vendor position.

For devkit this supports the existing direction: the text contract is devkit-owned, the medium is project-owned (5a),
and a running build or screenshot can be review evidence when present (5b). Contrasting candidates (4b) also counter
the anchoring of one coded build. Running the build is engine-specific verification, which the proposal excludes.

## 5. An illustrative screen specification

The research drafted an editable proposal review screen with a feedback form. devkit's own interface is the viewer,
which is read-only (`CAP-VIEW-repository-viewer`: it answers `GET` only and writes nothing), so the example below
re-expresses an existing viewer screen instead: the Dashboard's proposals section. Its states and behavior come from
that capability; the document shape, the `SCR` prefix and the use case ID are hypothetical (no use case cites the
viewer yet), and Q1 and Q2 decide the real shape.

```yaml
id: SCR-dashboard-proposals          # hypothetical prefix
title: Dashboard proposals section
kind: screen
status: draft
presents:
  object: Proposal
  representation: card
usecases:
  - UC-example-review-repository-status   # hypothetical
capabilities:
  - CAP-VIEW-repository-viewer
```

```markdown
## Content
- Section header: active proposal count
- Proposal [card] list, ordered reviewing, draft, then accepted, each group by ID; first page of 9
  - card: title, status, summary; a source badge when the Planning overlay supplied it
  - loading: loading state with an unknown count, never an empty list
  - failed: error state with an unknown count, never an empty list
  - overlay failed: checkout cards and count kept, a non-alert note added
- "Load more" while pages remain

## Interactions
| Trigger | From state | To state | Capability | Feedback to the user |
| --- | --- | --- | --- | --- |
| Section opens | (none) | loading | CAP-VIEW-repository-viewer | loading state, count unknown |
| List loads | loading | populated | CAP-VIEW-repository-viewer | checkout cards shown without waiting for the overlay |
| Overlay arrives | populated | populated | CAP-VIEW-repository-viewer | matching cards updated in place; Planning-only proposals appended after the last page |
| Load more | populated | populated | CAP-VIEW-repository-viewer | at most one page appended, order unchanged |
| Repository or branch changes | any | loading | CAP-VIEW-repository-viewer | pending results discarded |
```

The example shows what the text contract adds over the capability: the capability already states each behavior as a
requirement with its test, while the screen document gathers them per screen, names the representation and lets a
use case step point at it. Region proportions and narrow-viewport behavior stay with the project.

## 6. Review questions

The research proposed four questions for the UX reviewer. They fit the walkthrough and rubric options of
`MAT-ux-documentation-practice` section 3 as follows:

| Question | Mechanical or judged | Note |
| --- | --- | --- |
| Do screen labels and regions use the use case's and glossary's terms? | Judged, partly checkable against the glossary's UX objects | Mental model drift |
| Does every state, including empty, loading and failure, offer a next action? | Judged per screen; exits are checkable (2b) | Dead ends |
| Is every operable element traced to the use case step and capability it serves? | Mechanical once links exist (2a) | Not necessarily 1:1: navigation may cite no capability and one control may cite several |
| Does one screen have more than one competing primary region? | Judged | Information dumping |

## 7. Out of scope: interfaces of agentic products

The research also surveyed intent-based agentic UX, generative UI (runtime interfaces an agent composes for end
users, for example over [A2UI](https://github.com/google/A2UI) with a client-side catalog of trusted components or
[AG-UI](https://docs.copilotkit.ai/ag-ui)), autonomy levels with human approval checkpoints, and team role
assignments. These concern products whose users interact with an agent, or team organization, not the specification
of screens an agent builds. A project with such a product can describe them in its own UX documents; they add no
requirement to the devkit kind.

## 8. Options for Planning

These add to the options in `MAT-ux-documentation-practice` section 7; they are inputs, not decisions.

| Option | Content | Cost |
| --- | --- | --- |
| 6a | Screens name the object and representation they present in prose only | Lowest; no new structure |
| 6b | The glossary marks which terms are UX objects and gives each its representations and CTAs per role (extra columns, or a UX object table in `docs/glossary.md`); screens cite the term | Moderate; one register for names, synonyms to avoid and code identifiers. It changes the glossary table format, which `PROP-foundation-documents` excludes and this proposal's boundaries do not yet own, so Planning settles the owner |
| 6c | 6b or 6d plus object lifecycle transition tables in the UX documents | Duplicates lifecycles that capabilities may already own; cite instead where they do |
| 6d | A separate object list document per project, cited by screens | Moderate; a second document type that repeats the glossary's names and has to be kept in step with it |
| 7a | Layout as prose region rules and a content tree, with conditions next to nodes; the writing instruction rules out character-cell layouts | Medium-independent; matches 1a |
| 7b | 7a plus component trees | Stack-specific; project-owned, so outside the devkit template |

The research favors 6b (the glossary as the object register) scoped to the objects the use cases touch, 7a, and
keeping lifecycles in capabilities (citing, not restating).

## 9. Not verified or dropped

- Dropped as unsupported: star ratings and grades comparing methods, "90%/10%" splits of screens needing wireframes,
  claims of hallucination-free or "near 100%" accurate generation, task-flow design producing "spaghetti code", and
  "complete" protection against architecture drift.
- Corrected: spec-driven development is presented as an emerging practice; the spec-first, spec-anchored and
  spec-as-source levels come from [Böckeler, martinfowler.com, 2025](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html),
  which is openly skeptical of the tools. "State-driven design" is not an established method name; statecharts are.
- Not verified: Prater's exact wording on databases (secondary snippets only), Tohidi et al. (CHI 2006, second-hand),
  and the practitioner sources on OOUX with AI agents (blog posts and agency pages).
