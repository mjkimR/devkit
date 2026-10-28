# [RULE-ux-coverage] UX Coverage

## 1. Overview

Once a UX document lists a use case in `usecases`, each step of that use case is expected to cite the screen it
happens on, and each interaction of the document to name the step it serves (`ADR-ux-step-links-and-coverage`). Not
every step happens on a screen (a mail sent, a background job) and a screen may carry global controls no single task
needs, so gaps are warnings; contradictions are `RULE-ux-links`'s.

- **Phase and severity**: `linter`, `warning` (devkit gives each rule one severity, the `RULE-spec-progress`
  precedent), so it never blocks a commit.
- **What is checked**: every current use case some current UX document lists, and every current UX document.
- **Targeting**: an uncovered step is reported once, on the first UX document listing the use case that the run
  targets (path order, at its `usecases` entry), else on the use case at the step's line.

## 2. Cause of Violation

- `<UC> step <key> cites no UX document`: a main-scenario step or extension of a listed use case cites no UX ID.
- `interaction has no Step`: an Interactions row whose Step cell is empty or `-`.

## 3. Remediation

Cite the UX ID of the screen the step happens on, or of the screen a system step's response appears on; leave a step
uncited only when it truly happens off screen. Name the served step of an interaction as `` `UC-<slug>` <key> ``; a
global control may keep an empty Step cell. Not fixable automatically.

## 4. Configuration

No settings. A project that wants full coverage enforced raises it with
`[rules.severity_overrides] "RULE-ux-coverage" = "error"`.

## 5. Exceptions

No inline suppression. A use case no UX document lists is never reported.
