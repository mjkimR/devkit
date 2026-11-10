---
id: UX-decision-supersession
title: Decision supersession summary
summary: "Decision supersession summary for inspecting ADR replacement scope and proposed PADR changes while retaining the decision body and source context."
area: viewer
element: panel
status: active
usecases: [UC-read-decision-supersession]
capabilities: [CAP-VIEW-repository-viewer]
---

# [UX-decision-supersession] Decision supersession summary

## 1. Purpose

- **Primary task:** Inspect replacement relations and their scope without leaving the current decision.
- **Facts to commit:** relation direction, target ID/title/status, whole/partial scope, literal replaced-scope text
  and whether available documents establish a complete list.
- **Secondary items:** a reload action and failed paths follow the relation groups.

## 2. Content

Both directions remain visible in document order rather than a hidden tab. Each group lists its related decisions
in deterministic ID order. Text wraps to the available width; no separate geometry or visual token is prescribed.

- Supersession relations (section heading and loading/incomplete context).
  - `Supersedes` group (ADR only) or `Proposed supersession` group (PADR only).
    - Related decision (written/canonical ID, title and status when resolved; target link only when unambiguous; proposal-detail PADR links open the checkout ADR in Files).
    - Replacement scope (`whole` or `partial`; PADR group additionally says proposed).
    - Replacement text (escaped source text, or `Replacement scope not recorded`).
  - `Superseded by` group (ADR only, later ADRs only; same row facts).
  - Source failures (paths, only when scan errors exist).
  - `Reload relations` action.

A completed empty direction says `None recorded`. An incomplete empty incoming direction says
`No incoming relations found in the documents read`. This is source evidence, not a declaration that a partly
superseded ADR is wholly invalid. An unresolved or ambiguous ID has no link and says why it is unavailable.

## 3. States

- **loading:** `Loading supersession relations…`; body remains available and navigation can cancel the request.
- **populated:** at least one relation is present; follow a resolved link or keep reading.
- **empty:** completed scan found no relations; `None recorded` and reload remain available.
- **incomplete:** successful relations plus `Incomplete`, failed paths and reload; no claim of an empty complete
  reverse list.
- **error:** no usable index result; show failure details and reload, while retaining the decision body.

## 4. Interactions

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Follow an unambiguous resolved decision link | `UC-read-decision-supersession` 4 | populated, incomplete | loading | `UX-view-decision` | `CAP-VIEW-repository-viewer` | Target title/body/summary appears; Read reveals its namespace, Files keeps its view, proposal-detail PADR opens checkout ADR in Files |
| Reload relations | `UC-read-decision-supersession` 3a | populated, empty, incomplete, error | loading | | `CAP-VIEW-repository-viewer` | Source index reloads and replaces summary or shows failure |
| Continue reading after an unavailable target | `UC-read-decision-supersession` 3b | populated, incomplete | populated, incomplete | | `CAP-VIEW-repository-viewer` | Written ID and missing-scope text remain visible without a broken control |
