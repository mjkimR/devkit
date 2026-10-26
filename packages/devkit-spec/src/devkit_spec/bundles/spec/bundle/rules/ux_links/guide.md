# [RULE-ux-links] UX Links

## 1. Overview

A UX document (`docs/ux/<area>/UX-<slug>.md`, or the same path under a namespace docs root) describes one screen,
modal or panel; a use case step cites the UX ID of the screen it happens on, and each row of the document's
Interactions table names the step it serves (`ADR-ux-step-links-and-coverage`). This rule reports what the two sides
contradict, so the screen contract and the task flow stay in step. Steps that cite no screen are only a warning
(`RULE-ux-coverage`).

- **Phase and severity**: `linter`, `error`.
- **What is checked**: every current UX document outside materials, against every current use case.
- **Targeting**: a finding is reported on the UX document when the run targets it; a finding that concerns a use case
  too (step keys, `usecases` agreement, exits, reachability) is reported on the use case, at the step's line, when
  only the use case is targeted.

## 2. Cause of Violation

The document's own shape:

- `element is missing; set screen, modal or panel`, or `element "<value>" is not screen, modal or panel`.
- `no Interactions section`, or `Interactions has no table with the columns Trigger | Step | From | To | Target |
  Capability | Feedback` (the first table under the `Interactions` H2, its header compared case-insensitively).
- `Step cell "<value>" is not `UC-<slug>` <key>`: a Step cell is empty (also `-`) or one or more pairs of a use case
  ID in backticks and a step key (`3`, `2a`, `*a` or `\*a`), separated by commas.
- `Target "<value>" is not a UX document, close, back or end`: empty means the interaction stays on the element.
- `modal has no close or back interaction`.

The links, both directions:

- `Step names <UC>, which usecases does not list`.
- `Step names <UC> <key>, which is not a step of <UC>`: steps are the `N.` items at column 0 under `Main Success
  Scenario` (a nested numbered list continues its step) and the `- **<key>.**` bullets under `Extensions`;
  renumbering steps changes their keys.
- `Step names <UC> <key>, which does not cite <UX>`.
- `usecases lists <UC>, but no Step cell names it`.
- `<UC> step <key> cites <UX>, whose usecases does not list <UC>`.

The flow, per listed use case whose steps cite the document (a `panel` is exempt from both):

- `screen has no exit in <UC>`: no row targets another UX document, `close`, `back` or `end`, and no citing step is
  terminal (the last main step, an extension that ends the use case, or a step whose next step cites no screen; an
  extension's next step is the one it `resumes at`; `resumes at the same step` is the step it branches from, and
  an extension with no resume phrase, or a `*a` resuming at the same step, ends the use case).
- `<UX> is not reachable from an entry of <UC>`: entries are the screens cited by the first step, by a step whose
  preceding step cites no screen and by every extension; edges are the targets of the screens the use case cites
  and of the panels their Content section cites.

## 3. Remediation

Fix the side that is wrong: cite the screen in the step it happens on, name the right step key in the Step cell, add
the missing `usecases` entry, add the exit or the `close` row, or add the interaction that leads to the screen. A
system step cites the screen its response appears on, so the screen after it is reached through an interaction. Not
fixable automatically: which side is right is a decision.

## 4. Configuration

No settings.

## 5. Exceptions

No inline suppression. Unresolved use case or UX IDs are `RULE-document-reference`'s and are skipped here.
Extension-to-state coverage is not checked.
