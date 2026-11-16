---
id: UX-browse-formal-documents
title: Formal document reading
summary: "Find a formal node and retain its source context."
area: viewer
element: screen
status: active
usecases: [UC-read-formal-document]
capabilities: [CAP-VIEW-repository-viewer]
---

# [UX-browse-formal-documents] Formal document reading

## 1. Purpose

Find a formal node and retain its source context.

## 2. Content

The primary region is the selected book node; secondary navigation contains scope, search and history controls.

- Selected repository/branch and handbook/book control.
- Domain, Designs and Operations chapters with canonical ID/title/status.
- Search, Include retired and selected explicit target.
- Formal body or original raw source; `UX-formal-document-relations` below the header.
- Independent detail/support links and Back to previous document.

Existing viewer component/styles own visual treatment; this element adds no separate style system.

## 3. States

| State | Representation and next action |
| --- | --- |
| handbook | Existing release snapshot; request the book. |
| loading | Source-labelled progress; switch/back remains available. |
| populated | Canonical node/body; inspect, follow or return. |
| empty | No matching entries; change filters. |
| missing | Written target and unavailable reason; reload or return. |
| error | Failed reads remain explicit; reload. |
| raw | Exact source; Rendered returns in place. |

## 4. Interactions

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Request book | `UC-read-formal-document` 1 | handbook | loading |  | `CAP-VIEW-repository-viewer` | Index progress then chapters |
| Search/select scope | `UC-read-formal-document` 2 | populated | populated |  | `CAP-VIEW-repository-viewer` | Matching IDs and scope |
| Clear empty filters | `UC-read-formal-document` 2a | empty | populated |  | `CAP-VIEW-repository-viewer` | Changed results |
| Open node or explicit history | `UC-read-formal-document` 3 | populated | populated |  | `CAP-VIEW-repository-viewer` | Canonical identity and status |
| Inspect references | `UC-read-formal-document` 4 | populated | populated | `UX-formal-document-relations` | `CAP-VIEW-repository-viewer` | Direction/source context |
| Follow detail | `UC-read-formal-document` 5 | populated | populated |  | `CAP-VIEW-repository-viewer` | Independent canonical detail |
| Open supporting file | `UC-read-formal-document` 5 | populated | loading | `UX-read-supporting-artifact` | `CAP-VIEW-repository-viewer` | Path/source context |
| Return from unavailable identity | `UC-read-formal-document` 3b | missing | populated | back | `CAP-VIEW-repository-viewer` | List restored |
| Raw / Rendered | global: inspect original source | populated | raw |  | `CAP-VIEW-repository-viewer` | Exact source or body |
| Source change | `UC-read-formal-document` *a | populated | handbook |  | `CAP-VIEW-repository-viewer` | Old reads cancelled; selected source shown |
| Back | `UC-read-formal-document` 6 | populated | populated | back | `CAP-VIEW-repository-viewer` | Prior reading position restored |
