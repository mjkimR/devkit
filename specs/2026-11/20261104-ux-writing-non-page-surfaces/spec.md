---
id: SPEC-ux-writing-non-page-surfaces
title: UX writing guidance for surfaces beyond pages and forms
summary: "Extends the ux-writing instruction with criteria for interfaces the page-and-form vocabulary describes poorly, such as real-time viewports, kiosks, voice and terminal surfaces, so a namespace keeps the screen contract and the UX rules instead of opting out."
status: completed
created: 2026-11-04
related_capabilities: [CAP-HARN-agent-guidance]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-ux-writing-non-page-surfaces] UX writing guidance for surfaces beyond pages and forms

## 1. Problem Statement & Motivation

The `ux-writing` instruction and the `ux` template describe an interface element with a vocabulary drawn from pages
and forms: `screen`, `modal`, `panel`, states `populated`, `empty`, `loading`, `error`, and an Interactions table
whose comment asks for "one row per trigger". `RULE-ux-links` and `RULE-ux-coverage` check only the shape of that
contract (`CAP-GOV-spec-rules` 3.15, 3.16): a valid `element`, the seven-column table, well-formed cells, agreement
with the use case steps, and gaps classified with a reason (`ADR-explicit-ux-coverage-exception-notation`).

An agent writing the UX document of a real-time viewport, a kiosk, a voice assistant, a terminal interface or a
status display finds no guidance on how that surface maps onto the vocabulary: what the element is when controls and
a live view share one surface, where continuous input (movement, aim, scrubbing, speech) goes when no use case step
owns it, whether a mode change is a state or a transition, and what a surface with no task flow still writes. The
agent then either forces the surface into rows it does not have or concludes the contract does not fit and asks for
an opt-out. The Planning of the rejected proposal ~~`PROP-ux-rules-path-exclusion`~~ (rejected in commit `aa67659f`;
`ADR-reject-ux-rules-path-exclusion`) found the rules compatible with such
surfaces once the explicit coverage exceptions exist, and that the missing piece is writing guidance, not a rule
setting. This spec adds that guidance, generic across domains, so a namespace keeps the screen contract and every UX
rule.

## 2. User Stories

- **US-1**: As an AI coding agent writing a UX document for a surface that is not a page or a form, I want criteria
  for choosing the element, placing continuous input, naming modes and deciding between a state change and a
  transition, so that I write a document the UX rules accept without inventing structure the surface lacks.
- **US-2**: As an AI coding agent writing a use case whose steps are long-running activities or system judgements, I
  want to know which element a step cites and when it is off screen, so that `RULE-ux-coverage` reports only real
  gaps.
- **US-3**: As a repository owner evaluating whether the screen contract fits a namespace, I want a mismatch the
  guidance cannot resolve recorded as feedback with the document as evidence, so that a later rule change rests on a
  real case.

## 3. Non-Goals

1. **Scope Excluded**: a new or relaxed `element` kind, or any change to the Interactions columns, the cell grammar or
   the two UX rules. **When to Reconsider**: a recorded mismatch (US-3) that the guidance cannot resolve.
2. **Scope Excluded**: a path-scoped opt-out setting for the UX rules; ~~`PROP-ux-rules-path-exclusion`~~ (rejected in
   commit `aa67659f`; `ADR-reject-ux-rules-path-exclusion`) was rejected
   in favor of this guidance.
3. **Scope Excluded**: new sections of the `ux` template or changes to the seeded `docs/ux/README.md`; the
   instruction owns the criteria and the template keeps its five sections.
4. **Scope Excluded**: domain-specific instructions (a game, kiosk or voice instruction); one generic section with
   one example per criterion, drawn from different domains.
5. **Scope Excluded**: changes to the viewer, to `devkit docs` commands or to the `ux-reviewer` rubric.

## 4. Acceptance Criteria & Behavioral Contracts

The instruction text is checked by the `spec` bundle's guidance tests
(`packages/devkit-spec/tests/integration/bundles/spec/test_ux_guidance.py`), which assert that one block states every
token of a rule; the behavior the guidance relies on is pinned by the rule tests of `RULE-ux-links` and
`RULE-ux-coverage`.

### [AC-01] The element is chosen by what a person perceives as one place
- **Given** the `ux-writing` instruction
- **When** an agent reads its section on surfaces beyond pages and forms
- **Then** one block states that a continuously shown surface the person perceives as one place (a viewport, a
  canvas, a map, a console) is a `screen`, that an overlay shown beside or over it throughout (a HUD, a status bar, a
  toolbar, a transcript) is a `panel` named by the screen's Content, and that an overlay that interrupts the surface
  until dismissed (a pause menu, a confirmation, a command palette) is a `modal`; the guidance test asserts the block.

### [AC-02] Continuous input is described in prose and the table lists only step-serving and global rows
- **Given** the same section
- **When** the agent writes a surface with continuous or modeless input (movement, aim, scrubbing, pan and zoom,
  speech, gestures)
- **Then** one block states that the control scheme is written in Content and States, that an Interactions row is
  written only for a trigger that advances a use case step or is a global control with `global: <reason>`, and that
  the table does not list every input; the guidance test asserts the block, and the `ux` template's Interactions
  comment asks for one row per trigger that serves a step or is a global control.

### [AC-03] Modes of the surface are its states
- **Given** the same section
- **When** the surface has modes rather than data states (exploration and combat, idle and recording, connected and
  degraded)
- **Then** one block states that the modes are the lower-case state names and the From and To cells, and that
  `populated`, `empty`, `loading` and `error` are written only where they apply; the guidance test asserts the block.

### [AC-04] A transition replaces the surface; a mode change stays on it
- **Given** the same section
- **When** the agent decides between a Target and a state change
- **Then** one block states that a change that replaces what the person sees (a scene, a level, another screen) is a
  row whose Target is another UX document, and that a change of mode on the same surface is a row whose From and To
  differ with an empty Target; the guidance test asserts the block.

### [AC-05] Long-running and judged steps cite by perceived outcome
- **Given** the `usecase-writing` instruction
- **When** a use case step is a long-running activity (a match, a recording, a session) or a judgement the system
  makes
- **Then** one block states that a long-running activity is one step citing the element where its outcome is
  perceived, and that a system judgement whose result reaches no element is classified `off screen: <reason>`; the
  guidance test asserts the block, and `ux-writing` points to `usecase-writing` for step citations as it does today.

### [AC-06] A surface without a task flow keeps the contract and passes the rules
- **Given** a UX document with `element: screen`, `usecases: []` and an Interactions section holding only the header
  row, and a `panel` document in the same shape
- **When** `RULE-ux-links` and `RULE-ux-coverage` check the workspace
- **Then** both report no finding; the rule tests of both rules pin this, and one block of the `ux-writing` section
  states that a surface without a task flow leaves `usecases` empty, keeps Purpose, Content and States, keeps the
  Interactions header, and is reported by neither rule.

### [AC-07] A mismatch the guidance cannot resolve is recorded as feedback
- **Given** the same section
- **When** a surface still cannot be written under the criteria
- **Then** one block directs the agent to record the document and the mismatch as feedback instead of omitting the
  document or loosening the table, and names that record as the evidence a later rule change needs; the guidance test
  asserts the block.

### [AC-08] The instruction stays within its header budget and the guidance contract
- **Given** the edited `ux-writing` and `usecase-writing` instructions
- **When** `just test devkit-spec tests/integration/bundles/spec` and
  `uv run devkit rules check --phase hygiene <instruction>` run
- **Then** both descriptions start with `Read before` and stay within 300 characters, the hygiene run reports no
  `RULE-agent-asset-wording` warning, and the `ux-writing` row of `CAP-HARN-agent-guidance` 4.3 names the surface
  criteria.

### [AC-09] The instruction stays self-contained
- **Given** the edited docs bundle instructions
- **When** `rg -n '\b(ADR|PADR|CAP|UC|UX|ARCH|SPEC|PROP|MS|MAT|FB)-[A-Za-z0-9]' packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/ux-writing.md packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/usecase-writing.md` runs
- **Then** every match is a placeholder or an example that names no real document (`UX-<slug>`, `UC-<slug>`,
  `CAP-<AREA>-<slug>` and the existing mail example of `usecase-writing`).

## 5. Assumptions

- The seven criteria agreed in conversation (element choice, continuous input, modes as states, transitions, step
  citation, task-less surfaces, feedback on mismatch) are the section's content; examples come from a game viewport,
  a kiosk, a voice assistant, a terminal interface and a status display, no domain getting its own instruction.
- The step citation criterion (AC-05) lives in `usecase-writing`, which owns step citations, and `ux-writing` refers
  to it, under the one-owner rule of `CAP-HARN-agent-guidance` 4.3.
- The `ux` template's Interactions comment ("One row per trigger") is clarified in place rather than left to
  contradict AC-02; the template's sections and lines the guidance tests pin are unchanged.
