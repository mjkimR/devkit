---
id: PADR-ux-step-links-and-coverage
title: Step citations and UX coverage rule
summary: For tracing use case steps to screens, we cite UX IDs in step prose and name the served step key in each screen interaction, checked by a coverage rule with flow graph checks, to reuse body references and keep both directions checkable, accepting a new use case step parser.
proposal: PROP-ux-documentation
status: draft
created_at: 2026-10-26
---

# [PADR-ux-step-links-and-coverage] Step citations and UX coverage rule

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

The milestone requires the spec rules to report use case steps without a screen and screen interactions that serve
no step, where links are declared. Today every link rule reads frontmatter only; use case steps cite capabilities in
prose, and nothing maps a body reference to a step (`MAT-ux-documentation-planning-spike` §3). All current use cases
number their steps and extension keys regularly, so a step segmenter is cheap. Not every step happens on a screen
(system steps, off-screen actor decisions), and a screen can carry interactions no single task needs (global
navigation, help).

## 2. Decision Drivers

- Use cases stay intent-level: no interface detail in steps.
- Reuse of existing reference resolution, alias rewriting and `devkit spec refs`.
- Both directions checkable: step to screen and interaction to step.
- Commits are refused only for contradictions, not for legitimately screen-less steps.

## 3. Considered Options

- **UX IDs cited in step prose, step keys in the screen's interactions**: reuses body references; one new step
  segmenter; the use case names where a step happens, and a redesign or a second interface edits use cases.
- **A trailing marker per step**: a new micro-syntax with no added information.
- **A frontmatter map of step key to UX ID**: clean prose, but dict-valued fields need new parsing and keys drift on
  renumbering.
- **Links on the screen side only**: use cases stay free of UX IDs; "step without a screen" needs a reverse index and
  the use case author cannot see the screens.

## 4. Decision Outcome

Pending the user's answers to `step-screen-link`, `ux-checks` and `coverage-strictness` (Planning recommendation):

- A use case step cites the UX ID of the screen it happens on in backticks, next to its capability citations; the use
  case gains no frontmatter field.
- A UX document lists the use cases it serves in `usecases`; each interaction's Step cell is the use case ID as a code
  span followed by the step key (`` `UC-<slug>` 2a ``), so the ID is an ordinary reference.
- A new error-severity rule (working name `RULE-ux-links`) reports contradictions: a missing or invalid `element`; a
  missing Interactions section or a table without the seven columns; a Step key that names no step of that use case
  or a step that does not cite the screen; a `usecases` entry with no Step key naming it; a target that is not a UX
  ID, `close`, `back` or `end`; a modal without a `close` or `back` row; a screen without an exit; a screen not
  reachable from an entry.
- The graph is computed per listed use case. Its edges are every interaction of the screens that use case's steps
  cite. Its entries are the screens cited by the first step, by a step whose preceding step cites no screen, and by
  the first step of an extension. A screen needs no exit when it is cited by the last main-scenario step, by an
  extension that ends the use case, or by a step whose next step cites no screen (the task continues off-screen, for
  example a link sent by mail). Panels are exempt from exit and reachability and are reached from the screens whose
  content tree names them.
- A separate warning-severity rule (working name `RULE-ux-coverage`, the `RULE-spec-progress` precedent) reports, for
  every use case a UX document lists, a step or extension that cites no UX ID, and an interaction whose Step cell is
  empty.
- A report concerns two documents; it is reported on the UX document, or on the use case when only the use case is in
  the run, as `RULE-traceability-link` does for the targeted side.
- Extension-to-state coverage is not checked.

## 5. Consequences

- Positive: contradictions are mechanical once screens are in `docs/ux/`; screen-less steps stay visible without
  blocking commits.
- Negative: a use case step parser to maintain (tolerating an intro paragraph, prose in Extensions, the escaped `\*a`
  key and free-form `Covers` lines).
- Known limit: inserting a step before two consecutive steps on the same screen shifts their keys without a report,
  because the shifted step still cites the screen.
- Follow-up: extension-to-state coverage when projects report missing error states.

## 6. Confirmation

Rule tests under each rule's own `tests/` (`CAP-GOV-rule-authoring`), with fixtures for every report, the element
cases and the tolerated step-format deviations; `CAP-GOV-spec-rules` documents both rules.
