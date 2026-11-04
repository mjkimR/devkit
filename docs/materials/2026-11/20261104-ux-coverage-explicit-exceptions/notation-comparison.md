# Exception notation comparison

Evidence for `SPEC-ux-coverage-explicit-exceptions` Q1 and Q2, gathered from the shared UX model
(`governance.services.ux`), both UX rules, their guides and tests, the `ux-writing` and `usecase-writing`
instructions and `ADR-ux-screens`.

## What the parser already does

- A Step cell is empty (`-` and dashes count) or `` `UC-<slug>` <key> `` pairs; anything else is a `RULE-ux-links`
  error. The cell is parsed once in the model and both rules read `step_empty` and `step_valid`.
- A use case step is a `N.` item or a `- **<key>.**` bullet with its indented continuation lines; an extension's
  `resumes at <key>` phrase is found by a case-insensitive search over the step's lines. The rules' line reader skips
  code blocks and HTML comments.
- `ADR-ux-screens` rejected a trailing marker per step and a frontmatter map of step key to UX ID as the link
  mechanism: the first added no information, the second needs dict parsing and its keys drift on renumbering.

## Options

| Option | Global interaction | Off-screen step | Survives edits | Validation | Boilerplate |
| --- | --- | --- | --- | --- | --- |
| Inline marker (selected) | Step cell `global: <reason>` | step line `off screen: <reason>` | yes: no key, removed with the item | presence of the reason; contradiction with a cited UX ID | none on linked items |
| Frontmatter map | `exceptions: {<trigger>: reason}` | `exceptions: {<key>: reason}` | no: keys drift on renumbering or renaming | key must resolve to a row or step | a field per document |
| Exceptions section | list keyed by trigger label | list keyed by step key | no: same drift | label or key match | a section per document |
| HTML comment | `<!-- global: reason -->` | `<!-- off screen: reason -->` | yes | invisible to the line reader; invisible when rendered | none |
| Keep current state | empty cell | no citation | n/a | n/a | none; every intended gap warns |

The inline marker adds information (the reason) that the rejected link marker did not, so the ADR's rejection does
not apply to it. The `global:` cell is recognized by its prefix before pairs are read, so a reason may mention a
step pair; `RULE-ux-links` keeps its invalid-cell error for a cell that starts with pairs and carries `global:`
later, without a change to its logic.

## Defective forms and their reports

| Form | Report | Rule |
| --- | --- | --- |
| `global:` with no reason | `interaction is classified global without a reason` (warning) | `RULE-ux-coverage` |
| `off screen:` with no reason | `<UC> step <key> is classified off screen without a reason` (warning) | `RULE-ux-coverage` |
| `off screen:` on a step citing a UX ID | `<UC> step <key> is classified off screen but cites <UX>` (warning) | `RULE-ux-coverage` |
| a cell starting with pairs and carrying `global:` later | `Step cell "<value>" is not `UC-<slug>` <key>` (error, existing) | `RULE-ux-links` |
| a misspelled cell marker (`global nav`, `globl:`) | the same invalid-cell error (existing) | `RULE-ux-links` |
| `GLOBAL: <reason>`, `global: not part of `UC-browse` 2` | accepted: the prefix is any case and the reason is opaque | none |
| `offscreen:`, other step-phrase spellings | not a marker; the existing gap warning stays | `RULE-ux-coverage` |
| a reason naming a screen in a code span | the step cites that screen: `classified off screen but cites <UX>` (warning) | `RULE-ux-coverage` |

## Consumer evidence mapping

resource-indexer at `09f1a8df0dffcf047da5efe2305dd3f6c7fc1058`: 13 stepless interactions, of which the navigation
document's theme, skip-to-content and small-screen menu rows are intended; 27 uncited steps, among them background
work. The fixtures Development writes model these two documents; the proposal changes no consumer repository.
