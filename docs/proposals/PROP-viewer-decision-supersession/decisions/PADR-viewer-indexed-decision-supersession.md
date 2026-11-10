---
id: PADR-viewer-indexed-decision-supersession
title: Derive viewer supersession from indexed decisions
summary: "For decision readers, we derive supersession in the browser and show it beside each decision body, to retain one read-only viewer across hosts, accepting tested duplication of the document query semantics."
proposal: PROP-viewer-decision-supersession
status: draft
created_at: 2026-11-10
---

# [PADR-viewer-indexed-decision-supersession] Derive viewer supersession from indexed decisions

## 1. Context & Problem Statement

A decision reader needs both replacement directions and the replaced clauses while reading an ADR. The viewer
already parses repository documents in the browser (`ADR-repository-viewer`). Read owns an index; Files reads one
blob. `SPEC-partial-adr-supersession-statements` defines the later ADR's statement and a query for both directions.

## 2. Decision Drivers

- Keep local and library hosts on the same repository-source interface.
- Keep a selected decision readable while relation data loads or fails.
- Show applied ADR relations separately from proposed PADR changes.
- Preserve statement semantics without running each repository's Python environment.

## 3. Considered Options

- Browser derivation from the existing document index: one host-neutral read path; a TypeScript implementation of
  statement and identity semantics needs parity fixtures.
- A server endpoint reusing devkit-docs: one Python parser, but runtime coupling and an additional source interface
  for library hosts; rejected for this change.
- Inline summary below the decision header: both directions are visible with the body; long lists add vertical
  space. Recommended over a dedicated relations sidebar, which competes with navigation and hides text behind
  selection.

## 4. Decision Outcome

- Supersession is derived in the browser from indexed documents without a server endpoint or new dependency.
  → `CAP-VIEW-repository-viewer` planned decision supersession rules (MUST).
- Read and rendered Files place a shared summary below the decision header. Files indexes only after opening a
  rendered decision, and body rendering does not wait for relations.
  → `CAP-VIEW-repository-viewer` planned decision supersession rules (MUST).
- ADR incoming relations include only later ADRs. PADR pages label outgoing replacements as proposed and retain
  their actual source context. → `CAP-VIEW-repository-viewer` planned decision supersession rules (MUST).
- Incomplete reads remain visible and unresolved identities are not navigation links.
  → `CAP-VIEW-repository-viewer` planned decision supersession rules (MUST).

This adds viewer behavior without replacing an existing ADR decision.

## 5. Consequences

- Both hosts can read replacement state through existing tree/blob sources.
- Source-aware parsing is implemented in two languages; fixtures against the delivered document query semantics
  carry the maintenance cost.
- A cold Files decision read can index docs/specs; ordinary files and handbook navigation keep their read budget.
- Proposed PADR incoming impact previews are outside this change.

## 6. Confirmation

Development adds parser/identity/component and Read/Files integration tests under
`packages/devkit-viewer/frontend/src/lib/`, then runs frontend lint/check/test/build and viewer-assets verification.
`CAP-VIEW-repository-viewer` restates the retained contract; review confirms the Screens, use case and register
reflection. No performance improvement is claimed.
