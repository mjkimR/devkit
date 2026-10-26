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
number their steps and extension keys regularly, so a step segmenter is cheap.

## 2. Decision Drivers

- Use cases stay intent-level: no interface detail in steps.
- Reuse of existing reference resolution, alias rewriting and positions.
- Both directions checkable: step to screen and interaction to step.
- Keys that survive renumbering are detected, not silently stale.

## 3. Considered Options

- **UX IDs cited in step prose, step keys in the screen's interactions**: reuses body references; one new step
  segmenter; the use case names where a step happens.
- **A trailing marker per step**: a new micro-syntax with no added information.
- **A frontmatter map of step key to UX ID**: clean prose, but dict-valued fields need new parsing and keys drift on
  renumbering.
- **Links on the screen side only**: use cases stay free of UX IDs; "step without a screen" needs a reverse index and
  the use case author cannot see the screens.

## 4. Decision Outcome

Pending the user's answers to `step-screen-link`, `ux-checks` and `coverage-strictness` (Planning recommendation):

- A use case step cites the UX ID of the screen it happens on in backticks, next to its capability citations; the use
  case gains no frontmatter field.
- A UX document lists the use cases it serves in `usecases`; each interaction row names the served step key
  (`UC-<slug> 2a`).
- A new rule (working name `RULE-ux-coverage`) reports, for every use case a UX document lists: a step or extension
  that cites no UX ID; an interaction whose step key is empty, unknown or names a step that does not cite the screen;
  and a `usecases` entry with no matching step citation, or the reverse.
- The same rule checks the flow graph over the interactions' targets: a target that is neither a UX ID nor `close`, a
  screen without an exit, a modal without `close`, and a screen unreachable from those cited by step 1.
- Extension-to-state coverage is not checked.

## 5. Consequences

- Positive: coverage and dead ends are mechanical; the reviewer receives them as facts.
- Negative: a use case step parser to maintain; renumbering steps invalidates step keys in screens (reported).
- Risk: steps that happen on no screen are reported until the strictness question is settled.
- Follow-up: extension-to-state coverage when projects report missing error states.

## 6. Confirmation

Rule tests under the rule's own `tests/` (`CAP-GOV-rule-authoring`), with fixtures for each report and for the
tolerated step-format deviations; `CAP-GOV-spec-rules` documents the rule.
