---
id: UX-formal-document-relations
title: Formal document context
summary: "Follow current references and distinguish historical origin."
area: viewer
element: panel
status: active
usecases: [UC-read-formal-document]
capabilities: [CAP-VIEW-repository-viewer]
---

# [UX-formal-document-relations] Formal document context

## 1. Purpose

Follow current references and distinguish historical origin.

## 2. Content

The panel also appears on another indexed document declaring related_designs, related_domains or related_operations. The primary region holds current outgoing/incoming references. Provenance is separately labelled below it.

- Subject canonical identity and source path.
- Direction/field, written alias, canonical ID/title/status and current target.
- Unavailable target and incomplete index/metadata explanations with reload.
- Provenance-labelled historical origin.
- Inspectable metadata and declared source anchors, without a validity claim.

Existing viewer component/styles own visual treatment; this element adds no separate style system.

Supporting files appear below current references as a secondary list of parent-relative paths. DESIGN lists the
whole bundle except its anchor; DOMAIN/OPS list their adjacent ID/artifacts subtree. File selection opens the
existing source-bound reader. Complete empty inventory says no supporting files; loading/error shows incomplete
inventory and the existing reload action. Invalid identified support stays a file, without a relation identity.

## 3. States

| State | Representation and next action |
| --- | --- |
| loading | Keep the body readable while references load. |
| populated | Follow a current or provenance target. |
| empty | No references in the loaded complete index; return to body. |
| incomplete | Partial rows and failure/metadata details; reload. |
| unresolved | Written ID with missing/ambiguous explanation; return/retry. |

## 4. Interactions

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Open supporting file | `UC-read-formal-document` 5 | populated | loading | `UX-read-supporting-artifact` | `CAP-VIEW-repository-viewer` | Parent-relative path and selected source retained |
| Follow resolved target | `UC-read-formal-document` 4 | populated | populated | `UX-browse-formal-documents` | `CAP-VIEW-repository-viewer` | Canonical identity with written-reference context |
| Reload references | `UC-read-formal-document` 4a | incomplete | loading |  | `CAP-VIEW-repository-viewer` | Fresh source/index progress |
| Inspect unavailable target | `UC-read-formal-document` 4b | unresolved | unresolved |  | `CAP-VIEW-repository-viewer` | Written ID has no arbitrary link |
| Return to body | `UC-read-formal-document` 6 | populated | populated | back | `CAP-VIEW-repository-viewer` | Reading context retained |
