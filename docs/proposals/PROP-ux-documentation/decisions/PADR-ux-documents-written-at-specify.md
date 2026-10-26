---
id: PADR-ux-documents-written-at-specify
title: UX documents written at specify
summary: For giving implementation a screen contract, we write and check UX documents in docs/ux/ on the development branch during specify, before code, to let the rules and the UX review run before build, accepting UX documents that precede the behavior they describe until integration.
proposal: PROP-ux-documentation
status: draft
created_at: 2026-10-26
---

# [PADR-ux-documents-written-at-specify] UX documents written at specify

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

`spec-sync` writes `docs/` at `living-spec-draft`, after code review (`MAT-ux-documentation-planning-spike` §6).
For behavior that is right: `docs/` states what exists. A screen contract is different: implementation and the UX
review need it before `build-verify`, and the coverage rule only checks documents in `docs/`.

## 2. Decision Drivers

- The contract exists before the code that implements it.
- The rules and the UX review run on the same documents the build follows.
- The base branch never holds a screen without its implementation.

## 3. Considered Options

- **Write UX documents in `docs/ux/` on the development branch at `specify`**: rules and review run before build;
  the base sees them only at integration, together with the code.
- **Draft screens in `spec.md` or `target-docs.md` and move them at `spec-sync`**: keeps the current timing; nothing
  checks them before code, and the move is a second copy.
- **Review only after `spec-sync`**: no timing change; the review cannot shape the build.

## 4. Decision Outcome

Pending the user's answer to `ux-document-timing` (Planning recommendation): the first option. During Planning the
screens are drafted in `target-docs.md`; at `specify` the development worker writes them to `docs/ux/` on its branch,
and `reconcile.md` lists them as targets confirmed at `living-spec-draft`.

## 5. Consequences

- Positive: one copy of each screen; checks before build.
- Negative: an exception to current-state writing on the development branch, scoped to UX documents.
- Follow-up: `living-spec-writing`, `spec-specify` and `spec-sync` state the exception.

## 6. Confirmation

Review only (the skills' text); `RULE-reconcile-contract` lists the UX targets.
