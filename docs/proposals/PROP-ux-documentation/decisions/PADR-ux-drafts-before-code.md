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

Pending the user's answer to `ux-document-timing` (Planning recommendation): drafts before code, Living Spec at sync.
`spec-specify` and the target-docs blueprint gain the Screens draft shape, and `spec-sync` moves it into
`docs/ux/`.

## 5. Consequences

- Positive: no exception to current-state writing; the review still runs before build.
- Negative: no mechanical check before code; link defects surface at `living-spec-draft` and are fixed there.
- Follow-up: a contract slice at specify if projects report link defects found only at sync.

## 6. Confirmation

Review only (the skills' text); `RULE-reconcile-contract` lists the UX targets at `living-spec-draft`.
