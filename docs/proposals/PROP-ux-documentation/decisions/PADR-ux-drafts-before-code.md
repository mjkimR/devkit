---
id: PADR-ux-drafts-before-code
title: UX drafts reviewed before code
summary: For giving implementation a reviewed screen contract, we draft screens and their use case step citations in target-docs.md or spec.md before code and write docs/ux/ at spec-sync, to keep current-state timing, accepting that the coverage rule first checks them at living-spec-draft.
proposal: PROP-ux-documentation
status: draft
created_at: 2026-10-26
---

# [PADR-ux-drafts-before-code] UX drafts reviewed before code

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

`spec-sync` writes `docs/` at `living-spec-draft`, after code review, so `docs/` states what exists
(`MAT-ux-documentation-planning-spike` §6). Implementation and the UX review need the screens before
`build-verify`. A UX document links use case steps and capabilities, so writing it into `docs/` early also needs the
use case and capability changes it links; otherwise the rules refuse the commit or the review walks the old use case.

## 2. Decision Drivers

- The screen contract exists and is reviewed before the code that implements it.
- `docs/` keeps current-state timing; no partial Living Spec ahead of its behavior.
- One copy of each screen in the Living Spec once delivered.

## 3. Considered Options

- **Drafts before code, Living Spec at sync**: screens and the use case step citations they need are drafted in
  `target-docs.md` (proposal) or a Screens section of `spec.md` (spec depth) in the UX template's shape; the review
  reads the drafts; `spec-sync` writes `docs/ux/` and the use case changes; the link rules first check them at
  `living-spec-draft`, before integration.
- **Contract slice at specify**: UX documents and every use case and capability change they link are written to
  `docs/` on the development branch at `specify`; rules and review run before build, at the cost of an exception to
  current-state writing that covers use cases and capabilities, not only screens.
- **Review only after `spec-sync`**: no timing change; the review cannot shape the build.

## 4. Decision Outcome

Decided by the user (`ux-document-timing`): drafts before code, Living Spec at sync.

- `spec-specify` and the target-docs blueprint gain a Screens draft section in the UX template's shape. On a bundle
  handed off from a proposal, `spec-specify` carries the Screens drafts of `target-docs.md` into `spec.md`, so
  `spec-sync` and the reconcile verification read one place.
- In a draft, an ID the change creates (a new UX, UC or CAP ID) is plain text, never a code span or brackets, so
  `RULE-document-reference` does not resolve it before the document exists; existing IDs stay code spans.
- Register rows the change adds are drafted with the Screens drafts.
- `spec-sync` creates or updates `docs/steering/ux-objects.md` with the drafted rows, lists it in `reconcile.md`,
  and writes each drafted screen to `docs/ux/` and the step citations to the use cases, turning the new IDs
  into code spans, and lists each in `reconcile.md`.

## 5. Consequences

- Positive: no exception to current-state writing; the review still runs before build.
- Negative: no mechanical check before code. A link defect found at `living-spec-draft` that the code shares (for
  example a missing exit) returns the unit to `build-verify`, which repeats code review; one only in the documents is
  fixed at sync.
- Follow-up: a contract slice at specify if projects report link defects found only at sync.

## 6. Confirmation

The reconcile verification at its effort (the `reconcile-reviewer`, or the implementer's self-check at `low` and on a
permitted `medium` skip) checks that every drafted screen in `spec.md` has a `docs/ux/` target in `reconcile.md`;
`RULE-ux-links` checks the written screens. The skills' text is Review only.
