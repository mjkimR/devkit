---
id: ADR-ux-coverage-step-targeting
title: Uncovered steps are reported on their use case
summary: For locating an uncited use case step, we report it on the use case when the run targets it and only otherwise on the first listing UX document, to point the warning at the document the fix edits, accepting a partial supersession of the targeting clause of ADR-ux-screens.
proposal: SPEC-ux-coverage-explicit-exceptions
supersedes: [ADR-ux-screens]
status: accepted
created_at: 2026-11-04
---

# [ADR-ux-coverage-step-targeting] Uncovered steps are reported on their use case

- **Status**: Accepted
- **Date**: 2026-11-04

---

## 1. Context & Problem Statement

`RULE-ux-coverage` reports an uncited use case step on the first UX document that lists the use case and is in the
run, and on the use case only when no listed UX document is in the run (`ADR-ux-screens`, the
`RULE-traceability-link` precedent). In a whole-workspace run every document is in the run, so one listing screen,
in the consumer evidence a navigation panel, carries every workflow gap of the use cases it lists. With
`ADR-explicit-ux-coverage-exception-notation` the fix for such a gap is written in the use case, a screen citation
or an `off screen:` phrase, so the report names a file the fix never touches.

---

## 2. Decision Drivers

- The report lands on the document the remediation edits.
- A run that targets only the UX document still learns about the gap (devkit's targeting contract).
- No change outside `RULE-ux-coverage`; the stepless-interaction report stays on the UX document.

---

## 3. Considered Options

- **Use case first, listing UX document otherwise** (selected): the report goes on the use case at the step's line
  when the run targets it, else on the first listing UX document in the run at its `usecases` entry.
- **Keep the current state**: the UX document first; one screen owns gaps it cannot fix.
- **Use case only**: simplest; a commit that adds a UX document listing a use case with gaps gets no warning, which
  breaks the targeting contract.

---

## 4. Decision Outcome

Use case first, because the remediation lives there and the UX-document fallback keeps targeted runs informed.

- `RULE-ux-coverage` reports an uncited step on the use case at the step's line when the run targets the use case,
  else on the first listing UX document the run targets, at its `usecases` entry. → `CAP-GOV-spec-rules` 3.16 (SHOULD)
- The interaction-without-Step report stays on the UX document.
- This replaces, in part, the clause of `ADR-ux-screens` "A report concerns two documents; it is reported on the UX
  document, or on the use case when only the use case is in the run" for the uncited-step report only; `RULE-ux-links`
  keeps that targeting.

---

## 5. Consequences

- **Positive**: a whole-workspace run lists each gap on the use case that owns it; a navigation panel no longer
  appears to own unrelated gaps.
- **Negative / Risks**: the two UX rules now target the shared two-document report differently; the guides say why.
- **Follow-ups**: none.

---

## 6. Confirmation

- `RULE-ux-coverage` tests for a run with every document, with only the UX document and with only the use case;
  `CAP-GOV-spec-rules` 3.16 restates the clause.
