---
name: ux-writing
description: Read before writing or editing a UX document (docs/ux/) or a Screens draft. Defines one element per document, its purpose, content tree, states and interactions, step citations, contrasting candidates, the UX object register and what stays with the project.
---

# UX Writing

A UX document describes one interface element a person sees and operates: a `screen`, a `modal` or a `panel`
(`element`). It is a text contract at the content-and-states fidelity: what is shown, in which states, what each
interaction does and where it leads. The use case carries the task flow, the capabilities own the behavior, and the
UX document links both (`usecases`, `capabilities`). Start from the `ux` template.

## One element, linked both ways

- One document per element. A modal or panel shown by several screens is its own document, cited by their Content.
- A use case step cites the UX ID of the screen it happens on, next to its capability citations
  (`usecase-writing`). A system step cites the screen its response appears on; only a step that truly happens off
  screen (a mail sent, a background job) cites none.
- Each Interactions row names the step it serves as `` `UC-<slug>` <key> `` (`3`, `2a`, `*a`). A global control
  (navigation, help) may leave the Step cell empty. List every use case a Step cell names in `usecases`.
- Every screen has an exit (a row targeting another element, `close`, `back` or `end`) unless the task ends on it;
  a modal has a `close` or `back` row. `RULE-ux-links` reports contradictions, `RULE-ux-coverage` the gaps.

## Purpose and content

- **Purpose**: the primary task in one verb phrase, the facts a person needs to commit to it, and where every
  secondary item goes. One primary region per element; move what competes with it to another element.
- **Content**: prose region rules in relative terms (primary, secondary, beside, below), then a content tree whose
  nodes name the glossary object and the representation they show, with each node's condition beside it.
- Never draw a character-cell layout (ASCII boxes, aligned text art): it fixes geometry the contract does not own
  and reads badly to agents and people alike.
- **States**: lower-case names; `populated` plus each of `empty`, `loading` and `error` that applies. Every state
  offers a next action or says why none exists.
- **Feedback**: every interaction gives feedback; an irreversible one confirms or can be undone.

## Objects and the register

- Name every object by its glossary term (`docs/steering/glossary.md`). Labels use the use case's and the
  glossary's terms.
- The representations and calls to action of each object per role live in one steering file,
  `docs/steering/ux-objects.md` (frontmatter `title` and `summary`, no `id`). Create it with the project's first UX
  document; nothing seeds it, so a project without an interface never carries it.
- Each register row holds only the object, the role, the representation names and the call-to-action names, for the
  objects the use cases with UX documents touch. When the steering body cap is reached, keep only those objects;
  when no steering slot is free, the review records the register item as not applicable with the reason.

## What stays with the project

- **Visual style**: cite the project's steering style files; never restate colors, type, spacing or tokens.
- **Medium**: the wireframe, mock-up or screenshot tool is the project's. Link its artifact from the optional
  Evidence section; the reviewer reads it when present.

## Candidates and timing

- Where a screen's arrangement is open, draft two or three contrasting candidates (different primary regions or
  task splits, not variations of one layout) and give them to the user with a recommendation.
- Draft screens before code in the UX template's shape, with the use case step citations and register rows they need.
- In a draft, an ID the change creates (a new UX, UC or CAP ID) is plain text; existing IDs stay code spans.
- Keep retained screens in `docs/ux/`, their citations in the use cases and their object rows in the register.
- The selected development approach defines review timing and how drafts become current documents.
