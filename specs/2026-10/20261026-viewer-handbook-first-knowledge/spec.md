---
id: SPEC-viewer-handbook-first-knowledge
title: Handbook-first knowledge view with on-demand book
summary: Makes the repository viewer's knowledge tab open the release handbook when a repository has one and compute the Living Spec book only on request, so cold loads skip rendering every document.
status: in-progress
created: 2026-10-26
related_capabilities: [CAP-VIEW-repository-viewer, CAP-DLV-release-handbook]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-viewer-handbook-first-knowledge] Handbook-first knowledge view with on-demand book

## 1. Problem Statement & Motivation

Handed off from proposal PROP-viewer-handbook-first-knowledge on 2026-10-26.
- **Preserved Materials**: `docs/materials/2026-10/20261026-viewer-handbook-first-knowledge`

The Book rail tab of `CAP-VIEW-repository-viewer` indexes every Markdown file under `docs/` and `specs/` and renders
every Living Spec chapter as soon as it opens: on this repository about 1.1 s, 922 blob reads and 124k DOM nodes
before anything is readable (`MAT-viewer-handbook-cold-load`). The release handbook (`CAP-DLV-release-handbook`) is the
entry point written for people, but the viewer does not show it.

The decisions are `ADR-handbook-first-book-on-request` (one "Read" tab that opens the handbook where
`handbook/manifest.json` exists and computes the book only on an explicit request) and
`ADR-handbook-staleness-from-version` (the manifest tag ordered against `v<VERSION>`). The book is kept: most served
repositories have no handbook, and the handbook trails the current `docs/` between refreshes.

## 2. User Stories

- **US-1**: As a person opening a repository in the viewer, I want the reading tab to show its release handbook first,
  in my language, so that my first read is the one written for people.
- **US-2**: As a person reading the handbook, I want to see whether its release is the repository's current one, so
  that I know when to read the current contracts instead.
- **US-3**: As a person who wants the current contracts, I want to compute the Living Spec book with one control and
  keep it across tab visits, so that the book costs nothing until I ask for it.
- **US-4**: As a library host (autohub), I want my existing `RepositoryDataSource`, the `book` view id, `initialView`,
  `initialPath` and `sdd:path-change` to keep working, so that I get the handbook without a new data-source method.

## 3. Non-Goals

1. **Scope Excluded**: generating, refreshing or changing the format of the handbook (`CAP-DLV-release-handbook`).
2. **Scope Excluded**: removing the book or changing its content and order once computed.
3. **Scope Excluded**: viewport rendering of the book after the request (`FB-viewer-book-rendering` stays open) and
   anchor-first loading of Proposals and Specs (`FB-viewer-knowledge-anchor-loading` stays open).
4. **Scope Excluded**: a new endpoint, write path, Git process or `RepositoryDataSource` method.
5. **Scope Excluded**: in-page links from the handbook's ID citations to the book, and rewriting its tag-pinned
   source links.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] The reading tab keeps its id with the label "Read"
- **Given** the viewer page
- **When** the navigation rail renders
- **Then** the tab with view id `book` has the accessible name `Read` and the title `Handbook and Living Spec book`,
  and no rail tab is named `Book`.

### [AC-02] A repository with a handbook opens it within the read budget
- **Given** a data source whose `handbook/manifest.json` has `"langs": ["en", "ko"]`, tag `v0.1.4` and `VERSION`
  `0.1.4`
- **When** the reading tab opens and no book control has been selected
- **Then** the content shows `handbook/en/README.md` rendered as Markdown with the tag and generation date, the
  data source received exactly three `blob` calls (`handbook/manifest.json`, `VERSION`, `handbook/en/README.md`) and
  zero `tree` or `treeRecursive` calls, and no `section.chapter` element exists.

### [AC-03] A repository without a handbook shows the absence and the control
- **Given** a data source whose `blob` for `handbook/manifest.json` rejects with `HTTP 404: Not Found`
- **When** the reading tab opens
- **Then** it shows that the repository has no `handbook/manifest.json` and a `Living Spec book` button, after exactly
  one `blob` call and no `tree` call; a manifest rejection with another message (`HTTP 500`), invalid JSON or `langs`
  without `en` shows that error and the same button.

### [AC-04] The book is computed only on request, also after Proposals indexed
- **Given** the reading tab in handbook mode
- **When** the person opens Proposals (which indexes `docs/` and `specs/`), returns to the reading tab, and only then
  selects `Living Spec book`
- **Then** before the selection no `section.chapter` element exists in the reading tab and no `blob` under `docs/` or
  `specs/` was read by the reading tab; after it, the chapters render with no second index scan, so the whole sequence
  starts exactly one scan of the `docs` root.

### [AC-05] The book's content and order are unchanged
- **Given** a fixture with documents in every book group, a README, a proposal and a material
- **When** the book is computed
- **Then** the `section.chapter` ids in order equal the documents of `bookGroups` in group order filtered by
  `bookGroup`, as before this change.

### [AC-06] The request survives rail switches and resets with the repository
- **Given** an `SddViewer` whose book was requested
- **When** the person visits the Dashboard and returns to the reading tab
- **Then** the chapters render without selecting the control again; a change of `dataSource` or `branch` returns the
  tab to handbook mode; a standalone `KnowledgeViews` keeps the request through its bindable `bookRequested` prop.

### [AC-07] Host deep links
- **Given** an `SddViewer` with `initialView` `book`
- **When** `initialPath` is a file under `docs/` (`docs/a.md`), the default `docs/`, or a page under `handbook/`
  (`handbook/ko/concepts.md`)
- **Then** a `docs/` file counts as the book request and the book opens at that document; the default `docs/` opens
  handbook mode; a `handbook/` page opens that page in its language; in handbook mode `sdd:path-change` carries
  `view: "book"` and the `handbook/<lang>/<page>` path.

### [AC-08] Handbook links stay inside the language
- **Given** a handbook page with a relative `.md` link inside `handbook/<lang>/`, a relative link leaving it
  (`../../docs/x.md`), an external `https://github.com/...` link and a cross-page fragment link (`README.md#journeys`)
- **When** each link is selected
- **Then** the inner link opens that page in the tab with one `blob` read; the leaving link is shown as unavailable and
  reads nothing; the external link has `target="_blank"` and `rel="noopener noreferrer"`; the fragment scrolls to the
  English heading slug in `en` and to the raw `<a id="journeys">` anchor in `ko`; a missing page shows an error and the
  `Handbook home` entry.

### [AC-09] Language switch and memory
- **Given** a manifest listing `en` and `ko`
- **When** the person switches to `ko` on `journeys/x.md`
- **Then** the tab reads `handbook/ko/journeys/x.md`, stores `ko` in browser storage, and a later mount opens `ko`;
  without a stored choice the browser language is used when listed, else `en`.

### [AC-10] Staleness from VERSION
- **Given** manifest tag `v0.1.4`
- **When** `VERSION` is `0.1.3` (ahead), `0.1.4` (equal), `0.1.5` (behind), or absent or unparsable
- **Then** the header names the snapshot as prepared for the upcoming release `v0.1.4` without a note; shows the tag
  and date without a note; shows a non-alert note naming `v0.1.4` and `0.1.5` and that the Living Spec book shows the
  current contracts; or shows the tag and date only, respectively.

### [AC-11] Read-only handbook serving with path safety
- **Given** a registered repository with `handbook/manifest.json`, `handbook/en/README.md`, and a symlinked
  `handbook/en/link.md`
- **When** `blob?path=handbook/manifest.json`, `blob?path=handbook/en/README.md`, `tree?path=handbook/en`,
  `blob?path=handbook/en/link.md` and `blob?path=handbook/../VERSION` are requested
- **Then** the first two answer `200` with the file bytes, the listing omits the symlink, the symlink answers `404`
  `VIEWER_PATH_NOT_FOUND` and the `..` path answers `400` `VIEWER_PATH_INVALID`; no endpoint is added.

### [AC-12] Cold-load reduction measured
- **Given** `MAT-viewer-handbook-cold-load` as the base measurement
- **When** its probe reruns against this change with the `Read` tab and the handbook article as readiness
- **Then** the reading tab's cold load reads at most 3 blobs and leaves fewer than 10% of the base's 124k DOM nodes, and
  the result is recorded beside the baseline.

## 5. Security

Handbook pages pass through the existing Markdown and DOMPurify path. Links are rewritten only after sanitization:
external links open in a new browsing context with `rel="noopener noreferrer"`, and a relative link that leaves
`handbook/<lang>/` loses its `href`. All reads go through the host's `blob`, which keeps the server's path, symlink and
`.git` guards; nothing is written.

## 6. Assumptions

- A manifest is readable when it parses as a JSON object with a string `tag` and a `langs` array containing `en`;
  `generated` is shown when it is a string.
- `VERSION` is read only when a manifest exists; any failure reading it counts as absent.
- In book mode the sidebar offers a `Handbook` control that returns to handbook mode; the index stays loaded, so
  selecting the book again renders it without a scan.
- autohub's source is outside this worktree; host compatibility is settled against the library's exported API and its
  in-repository consumer README: `initialView`, `initialPath`, the `book` id, the exports and `sdd:path-change` keep
  their names and shapes, and `KnowledgeViews` gains only an optional prop.

## 7. Source feedback

- `FB-viewer-book-rendering`: addressed for the cold load only; kept open by the user's decision, rescoped to the
  rendering after the request.
- `FB-viewer-knowledge-anchor-loading`: not addressed; kept open.
