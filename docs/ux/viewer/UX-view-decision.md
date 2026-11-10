---
id: UX-view-decision
title: Decision reading view
summary: "Decision reading view for inspecting ADR replacement scope and proposed PADR changes while retaining the decision body and source context."
area: viewer
element: screen
status: active
usecases: [UC-read-decision-supersession]
capabilities: [CAP-VIEW-repository-viewer]
---

# [UX-view-decision] Decision reading view

## 1. Purpose

- **Primary task:** Read a decision and judge its remaining scope.
- **Facts to commit:** decision identity/title/status, the checked-out branch or Planning source context, the
  replaced clauses and any uncertainty from source reads.
- **Secondary items:** relations sit below the decision header; the existing navigation stays beside the body.
  Source/raw controls remain with the document header. This draft covers the decision-reading slice of Read,
  Files and proposal detail, not the other tasks of those host screens.

## 2. Content

The decision body remains the primary reading region. `UX-decision-supersession` is a secondary panel between the
header and body, so it is discoverable before the reader relies on old clauses. Existing host navigation and theme
controls retain their placement.

- Decision (header: ID, title, actual status and source context).
- Supersession relations (panel `UX-decision-supersession`, shown for rendered ADR/PADR documents).
- Decision (body: sanitized Markdown; raw source instead when raw mode is selected).
- Repository navigation (existing tree/book/proposal controls).

## 3. States

- **loading:** selected body load follows the existing view; relation loading has its own panel state. The reader
  can navigate away.
- **populated:** the decision body and relation panel are available; the reader may follow a relation or finish.
- **error:** a document-read error retains existing navigation so another document can be opened.
- **raw:** original source is displayed without the summary; switch to rendered mode to inspect relations.

## 4. Interactions

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Open a decision from existing navigation | `UC-read-decision-supersession` 1 | populated, loading, error, raw | loading | `UX-view-decision` | `CAP-VIEW-repository-viewer` | Selected decision title and body replace the prior one |
| Select rendered mode | `UC-read-decision-supersession` 3 | raw | populated | | `CAP-VIEW-repository-viewer` | Relation loading or summary appears |
| Select raw mode where the host offers it | global: inspect the document source | populated | raw | | `CAP-VIEW-repository-viewer` | Original document source replaces the rendered body |
| Choose another repository or branch | `UC-read-decision-supersession` 4a | populated | loading | `UX-view-decision` | `CAP-VIEW-repository-viewer` | Previous context clears; selected source loads |
| Finish reading | `UC-read-decision-supersession` 5 | populated | populated | end | `CAP-VIEW-repository-viewer` | No repository change; decision remains readable |
