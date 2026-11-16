---
id: UX-read-supporting-artifact
title: Supporting file reading
summary: "Read a parent-linked file and return to its source node."
area: viewer
element: screen
status: active
usecases: [UC-read-formal-document]
capabilities: [CAP-VIEW-repository-viewer]
---

# [UX-read-supporting-artifact] Supporting file reading

## 1. Purpose

Read a parent-linked file and return to its source node.

## 2. Content

The primary region is a safe preview or readable source. Context and Back remain above it.

- Parent identity, path, format and selected source/branch.
- Safe image or shared Markdown/Mermaid preview; CSV/diagram/source text.
- Raw/Rendered and download only for available readable source/bytes.
- Missing/unsupported explanation and Retry; Back to the parent.

Existing viewer component/styles own visual treatment; this element adds no separate style system.

## 3. States

| State | Representation and next action |
| --- | --- |
| loading | Path/source and progress; Back cancels the read. |
| populated | Preview/source and download; Back remains available. |
| raw | Exact readable source; Rendered or Back. |
| missing | Read failure and path; Retry or Back. |
| unsupported | Format explanation and available byte download; Back. |

## 4. Interactions

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Open file | `UC-read-formal-document` 5 | loading | populated |  | `CAP-VIEW-repository-viewer` | Supported content or explicit file state |
| Retry file | `UC-read-formal-document` 5a | missing | loading |  | `CAP-VIEW-repository-viewer` | Fresh source read |
| Raw / Rendered | global: inspect supporting source | populated | raw |  | `CAP-VIEW-repository-viewer` | Source/preview at the same path |
| Download | `UC-read-formal-document` 5a | unsupported | unsupported |  | `CAP-VIEW-repository-viewer` | Available bytes downloaded |
| Back | `UC-read-formal-document` 6 | populated | populated | `UX-browse-formal-documents` | `CAP-VIEW-repository-viewer` | Parent position restored; pending read cancelled |
| Source change | `UC-read-formal-document` *a | populated | loading | `UX-browse-formal-documents` | `CAP-VIEW-repository-viewer` | Old reads and URLs disposed |
