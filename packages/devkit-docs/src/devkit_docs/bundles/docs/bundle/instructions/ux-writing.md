---
name: ux-writing
description: Read before writing or editing a UX document (docs/ux/) or a Screens draft. Defines one element per document, its purpose, content tree, states and interactions, step citations, surfaces beyond pages and forms, contrasting candidates, the UX object register and what stays with the project.
---

# UX Writing

A UX document describes one interface element a person sees and operates: a `screen`, a `modal` or a `panel`
(`element`). It is a text contract at the content-and-states fidelity: what is shown, in which states, what each
interaction does and where it leads. The use case carries the task flow, the capabilities own the behavior, and the
UX document links both (`usecases`, `capabilities`). Start from the `ux` template.

## One element, linked both ways

- One document per element. A modal or panel shown by several screens is its own document, cited by their Content.
- Use case steps cite the screens they happen on, per `usecase-writing`.
- Each Interactions row names the step it serves as `` `UC-<slug>` <key> `` (`3`, `2a`, `*a`). A global control
  (navigation, help, a theme toggle) says why it serves no step in its Step cell, `global: <reason>`, for example
  `| Toggle theme | global: a preference control that belongs to no task | populated | populated | | | Theme changes |`;
  an empty Step cell is a coverage gap `RULE-ux-coverage` keeps warning about. List every use case a Step cell names
  in `usecases`.
- Every screen has an exit (a row targeting another element, `close`, `back` or `end`) unless the task ends on it;
  a modal has a `close` or `back` row. `RULE-ux-links` reports contradictions, `RULE-ux-coverage` the gaps.

## Surfaces beyond pages and forms

The vocabulary above comes from pages and forms; a viewport, a kiosk, a voice assistant, a terminal interface or a
status display fits it by these criteria, not by an exception to the rules.

- **Element**: the surface a person perceives as one place while it is shown is a `screen` (a game viewport, a
  kiosk's attract loop, a terminal pane, a map). An overlay shown beside or over it throughout is a `panel` that the
  screen's Content names (a HUD, a status bar, a toolbar, a transcript). An overlay that interrupts the surface until
  dismissed is a `modal` (a pause menu, a confirmation, a command palette).
- **Continuous input**: write the control scheme (movement, aim, scrubbing, pan and zoom, speech, gestures) in
  Content and States. Write an Interactions row only for a trigger that advances a use case step or is a global
  control (`global: <reason>`); the table does not list every input. Example:
  `| Say "pause" | global: a voice command available in every mode | playing | paused | | | Playback stops |`.
- **Modes**: when the surface has modes rather than data states (exploration and combat, idle and recording,
  connected and degraded), the modes are the lower-case state names and the From and To cells; write `populated`,
  `empty`, `loading` and `error` only where they apply.
- **Transitions**: a change that replaces what the person sees (a scene, a level, another screen) is a row whose
  Target is another UX document; a change of mode on the same surface is a row whose From and To differ with an
  empty Target.
- **Steps**: a step cites the element where its outcome is perceived; a long-running activity and a system
  judgement follow `usecase-writing`.
- **No task flow**: a surface no use case step reaches (free play, an ambient display) leaves `usecases` empty and
  keeps Purpose, Content, States and the Interactions header. Each row it keeps (a `modal`'s `close` or `back` row,
  a mode change) is a global control with `global: <reason>`, because an empty Step cell is a coverage gap on any
  document; then `RULE-ux-links` and `RULE-ux-coverage` report nothing for it. A step that cites the surface makes
  it a listed one: add the use case to `usecases` and name the step in a row.
- **Mismatch**: if the surface still cannot be written under these criteria, record the document and the mismatch
  as feedback instead of omitting the document or loosening the table; that record is the evidence a rule change
  needs.

## Purpose and content

- **Purpose**: the primary task in one verb phrase, the facts a person needs to commit to it, and where every
  secondary item goes. One primary region per element; move what competes with it to another element.
- **Content**: prose region rules in relative terms (primary, secondary, beside, below), then a content tree whose
  nodes name the glossary object and the representation they show, with each node's condition beside it.
- Never draw a character-cell layout (ASCII boxes, aligned text art): it fixes geometry the contract does not own
  and reads badly to agents and people alike.
- **States**: lower-case names; `populated` plus each of `empty`, `loading` and `error` that applies, or the modes
  of a surface that has them (`Surfaces beyond pages and forms`). Every state offers a next action or says why none
  exists.
- **Feedback**: every interaction gives feedback; an irreversible one confirms or can be undone.

## Objects and the register

- Name every object by its glossary term (`docs/steering/glossary.md` plus the selected registered namespace's
  `docs/packages/<name>/steering/glossary.md`). Labels use the use case's and the glossary's terms.
- The representations and calls to action of each object per role live in one steering file,
  `docs/steering/ux-objects.md` (frontmatter `title` and `summary`, no `id`). Create it with the project's first UX
  document that needs shared object rows; nothing seeds it, so a project without an interface never carries it.
- For namespace UX, read the root register together with `docs/packages/<name>/steering/ux-objects.md` when it exists.
- Write namespace-specific object rows in that namespace register; keep shared object rows in the root register.
- Create a namespace register only when local rows are needed; never copy the root register into every namespace.
- Review representations and calls to action against both registers; the UX link and coverage rules do not parse
  object registers or enforce vocabulary semantics.
- Each register row holds only the object, the role, the representation names and the call-to-action names, for the
  objects the use cases with UX documents touch. When the steering body cap is reached, keep only those objects;
  when no steering slot is free, the review records the register item as not applicable with the reason.

## What stays with the project

- **Visual style**: cite the project's steering style files or existing project-owned style/token source; never
  restate colors, type, spacing or tokens in each UX document.
- If no style source exists and the change decides visual style, draft one shared project-owned style source
  within the agreed task/document scope and cite it from the Screens drafts and UX documents.
- If that source is steering background, follow `living-spec-writing` for its location, title and summary;
  for example, a project may choose `docs/steering/visual-style.md` when that path is authorized.
- Use the project's existing style-source convention; no fixed filename or seeded file is required.
- If the needed style-source path is outside the authorized write scope, record the needed path for the scope
  owner before writing it; the fallback grants no additional write authority.
- **Medium**: the wireframe, mock-up or screenshot tool is the project's. Link its artifact from the optional
  Evidence section; the reviewer reads it when present.

## Candidates and timing

- Where a screen's arrangement is open, draft two or three contrasting candidates (different primary regions or
  task splits, not variations of one layout) and give them to the user with a recommendation.
- Draft screens before code in the UX template's shape, with the use case step citations and register rows they need.
- In a draft, an ID the change creates (a new UX, UC or CAP ID) is plain text; existing IDs stay code spans.
- Keep retained screens in `docs/ux/`, their citations in the use cases and their object rows in the register.
- The selected development approach defines review timing and how drafts become current documents.
