---
id: PROP-viewer-handbook-first-knowledge
title: Handbook-first knowledge view with on-demand book
summary: Makes the repository viewer's knowledge tab open the release handbook when a repository has one and compute the Living Spec book only on request, so cold loads skip rendering every document.
status: draft                         # draft | reviewing | accepted | rejected
created_at: 2026-10-26
target_area: viewer/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-viewer/src/devkit_viewer/features/
    - packages/devkit-viewer/frontend/src/lib/
    - packages/devkit-viewer/tests/
    - packages/devkit-viewer/README.md
    - docs/capabilities/viewer/
    - docs/development/reference/viewer.md
  excludes:
    - docs/decisions/
    - handbook/
    - tools/devkit-dev/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-viewer-handbook-first-knowledge] Handbook-first knowledge view with on-demand book

## 1. Background & Hypothesis

The knowledge tab of `CAP-VIEW-repository-viewer` has a book view that renders every current Living Spec document in
contract order: `visibleDocs` is the whole book and each document runs through `renderDocument`, which also rebuilds
its ID index (`FB-viewer-book-rendering`). Cold loads pay that cost before a person reads anything, and the tab loads
bundle contents before the anchors it needs (`FB-viewer-knowledge-anchor-loading`).

`SPEC-release-handbook` added a person-oriented entry point: a tracked `handbook/{en,ko}/` snapshot organized by user
journey and concept, refreshed only on the user's request and bound to a release tag through `handbook/manifest.json`
(`ADR-handbook-on-request-release-snapshot`, `CAP-DLV-release-handbook`). The book is not that entry point; it is a
full read of the current contracts.

Hypothesis: opening the handbook first where one exists and computing the book only when a viewer asks for it gives
people the right first read and removes the book's cold-load cost, without losing the current-contract view.

The book is not removed: the handbook is devkit-repository-only (the `devkit-dev` bundle) and does not exist until its
first requested refresh; the viewer shows several repositories, most without a handbook; and the handbook is
intentionally stale between refreshes while the book shows the current `docs/`.

## 2. Technical Spike Questions

- **Q1**: How does the viewer detect and serve a repository's handbook (presence of `handbook/manifest.json`, the
  language directories, the manifest tag), read-only, with the same path-safety rules as other repository files?
- **Q2**: How are handbook pages rendered and linked: relative links between handbook pages, tag-pinned links to
  source documents, and the en/ko selection with a remembered per-viewer choice?
- **Q3**: What does "on request" mean for the book: an explicit control that starts the computation, kept for the
  session; how are deep links into a book chapter handled before it is computed?
- **Q4**: What is the default for a repository without a handbook: the current non-book knowledge views with the book
  control, and how is the absence shown?
- **Q5**: How is handbook staleness shown: the manifest tag against the repository's current `VERSION` or latest tag?
- **Q6**: Does on-demand book computation make the viewport rendering of `FB-viewer-book-rendering` unnecessary, and
  does anchor-first loading (`FB-viewer-knowledge-anchor-loading`) still apply to the remaining views? Measure the
  cold load before and after on a repository with hundreds of documents.

## 3. Proposed Design & Impact

- A repository with `handbook/manifest.json` opens the knowledge tab on the handbook, in the selected language, with
  its release tag and a staleness note.
- A repository without one opens on the existing non-book knowledge views. In any repository, the book is computed
  only after the viewer selects a "Living Spec book" control.
- The book keeps its current content and order once computed; only when it is computed changes.
- Backend: a read-only handbook listing and page read under the viewer's existing browse feature; no write path.
- Contracts: `CAP-VIEW-repository-viewer` states the knowledge tab's default view, the handbook source and the
  on-demand book; the viewer reference and README follow.
- Interaction: `PROP-ux-documentation` also owns viewer frontend paths; sequence Development against it.

Scope excluded: generating or refreshing the handbook, changing its format, removing the book, and viewport-level
virtualization unless Q6 shows on-demand computation is not enough.

## 4. Lifecycle & Retirement Criteria

- Planning settles Q1-Q6 with a cold-load measurement and decides the fate of `FB-viewer-book-rendering` and
  `FB-viewer-knowledge-anchor-loading` (absorbed, kept or dismissed).
- Acceptance requires: the handbook default only where a manifest exists; no book computation before the explicit
  control; unchanged book content once computed; read-only handbook serving with path safety; a measured cold-load
  improvement; the viewer frontend checks (`just viewer lint`, `check`, `test`, `build`) with the committed page
  rebuilt.
- Retire when the knowledge tab contract in `CAP-VIEW-repository-viewer` states the handbook-first default and the
  on-demand book.
