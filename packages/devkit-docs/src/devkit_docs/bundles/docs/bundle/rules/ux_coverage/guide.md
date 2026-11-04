# [RULE-ux-coverage] UX Coverage

## 1. Overview

Once a UX document lists a use case in `usecases`, each step of that use case is expected to cite the screen it
happens on, and each interaction of the document to name the step it serves. Not every step happens on a screen (a
mail sent, a background job) and a screen may carry global controls no single task needs, so gaps are warnings, and
an intended gap is classified with a reason so that it stops warning; contradictions are `RULE-ux-links`'s.

- **Phase and severity**: `linter`, `warning` (devkit gives each rule one severity, the `RULE-spec-progress`
  precedent), so it never blocks a commit.
- **What is checked**: every current use case some current UX document lists, and every current UX document.
- **Targeting**: a step report lands on the use case at the step's line when the run targets it, else on the first UX
  document listing the use case that the run targets (path order, at its `usecases` entry), because the fix (a citation
  or an `off screen:` phrase) is written in the use case; `RULE-ux-links` keeps reporting on the UX document first,
  where its fixes mostly land. An interaction report lands on its UX document.

## 2. Cause of Violation

- `<UC> step <key> cites no UX document`: a main-scenario step or extension of a listed use case cites no UX ID and
  carries no `off screen:` phrase.
- `<UC> step <key> is classified off screen without a reason`: the step has `off screen:` with nothing after it.
- `<UC> step <key> is classified off screen but cites <UX>`: the step has the phrase and cites a screen; one of them
  is wrong.
- `interaction has no Step`: an Interactions row whose Step cell is empty or `-`.
- `interaction is classified global without a reason`: a Step cell `global:` with nothing after it.

## 3. Remediation

Cite the UX ID of the screen the step happens on, or of the screen a system step's response appears on. When the
step truly happens off screen, say why on the step: `off screen: <reason>`. Name the served step of an interaction
as `` `UC-<slug>` <key> ``; a global control says why in its Step cell: `global: <reason>`. Write the missing reason,
or remove the phrase from a step whose response does appear on a screen. Not fixable automatically.

## 4. Configuration

No settings. A project that wants full coverage enforced raises it with
`[rules.severity_overrides] "RULE-ux-coverage" = "error"`; the classifications still apply, and a classification
without a reason is then an error too.

## 5. Exceptions

Only the two explicit classifications, each with a non-empty reason that nobody judges mechanically:

- **Global interaction**: the Step cell, stripped, starts with `global:` (any case) followed by the reason. The rest
  of the cell is opaque text, so a reason may mention a step pair. A cell that starts with pairs and carries `global:`
  later, or misspells `global:`, is an invalid Step cell and a `RULE-ux-links` error, as any invalid cell is.
- **Off-screen step**: one of the step's lines holds `off screen: <reason>` (`off-screen:`, any case); the reason is
  the rest of that line without its closing `)` and sentence period. The reason names no screen: a code-span UX ID on
  the step's lines is a citation. A misspelled phrase (`offscreen:`) is not a marker, so the gap keeps warning. A
  classified step keeps the flow effect of an uncited step for `RULE-ux-links` (the screen before it needs no exit
  for it, the screen after it is an entry), so classify only a step whose response reaches no screen.

A blank cell or an uncited step alone is never an exception. A use case no UX document lists is never reported.
