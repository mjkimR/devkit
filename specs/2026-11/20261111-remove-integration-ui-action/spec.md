---
id: SPEC-remove-integration-ui-action
title: Remove the integration ui_action field
summary: Removes the ui_action field from integration results and the devkit-spec composed output, since it always repeats authority.
status: completed
created: 2026-11-11
related_capabilities:
  - CAP-INT-mcp-services
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-remove-integration-ui-action] Remove the integration ui_action field

## 1. Problem Statement & Motivation

The integration result (`IntegrationResult`) carries an optional `ui_action` field. It is a leftover of the removed
interactive approval surface: only the composed acceptance path (`spec proposal accept`) sets it, and it then holds
exactly the value it also writes to `authority` (`policy` or `host-conversation`). The JSON result of
`devkit integration integrate` and the `integration` object embedded in the `spec proposal accept` result therefore
repeat the same fact twice, and readers must learn a second field with no distinct meaning.

The agreed intent (finding AO-05b of the 2026-11-11 review-refactor code pass, a user decision) is to remove the
field from the result, its JSON and text output and every embedding, together with the plumbing that only feeds it.
There are no external consumers, so no compatibility shim is kept.

## 2. User Stories

- **US-1**: As an agent reading an integration result, I want one authority field so that I do not have to reconcile
  two fields that always agree.

## 3. Non-Goals

1. **Scope Excluded**: renaming or changing the values of `authority`, `acceptance_authority` or any other result
   field; changing integration behavior, approval or policy evaluation.
2. **Scope Excluded**: rewriting historical materials under `docs/materials/` that quote `ui_action` from earlier
   experiments; they are records of their time.
3. **Scope Excluded**: the concurrent retirement of `worktree finish --merge`.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Integration results carry no ui_action

- **Given** a completed local integration under `dev-integration=auto` or under `ask` with the presented digest
- **When** the result is serialized by `IntegrationResult.compact_dict()` (the JSON `devkit integration integrate
  --format json` prints)
- **Then** the object has no `ui_action` key, `authority` is `policy` or `host-conversation` respectively, and
  `IntegrationResult` has no `ui_action` attribute.

### [AC-02] Composed acceptance reports authority without ui_action

- **Given** the composed acceptance-and-integration engine (`IntegrationService._compose_execute`) called with the
  authority the caller decided
- **When** it completes
- **Then** the result's `authority` equals the passed value (`policy` or `host-conversation`) and the `integration`
  object embedded in the `spec proposal accept --format json` result has no `ui_action` key.

### [AC-03] Living Spec lists the result fields without ui_action

- **Given** `CAP-INT-mcp-services` and `docs/development/reference/` pages
- **When** `rg -n ui_action docs/capabilities docs/development/reference packages/*/src` runs
- **Then** it finds no match (tests keep only absence assertions), and the capability states that JSON carries `authority`.

## 5. Assumptions

- The third parameter of `_compose_execute` also decides `authority`, so it is kept and renamed to `authority`
  (assigned directly) instead of removed; only its `ui_action` use is plumbing that feeds the removed field.
- The `devkit-spec` caller already passes the authority value positionally, so its call needs no code change.

## 6. Source feedback

- Finding AO-05b (under AO-05) of `docs/materials/2026-11/20261111-review-refactor-code-pass/report.md`.
