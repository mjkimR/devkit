---
id: PADR-handbook-first-book-on-request
title: Handbook first, Living Spec book on request
summary: For the viewer's reading tab, we open the release handbook where a manifest exists and compute the Living Spec book only on an explicit request, through the existing tree and blob reads, to remove the book's cold-load cost, accepting one more selection to reach current contracts.
proposal: PROP-viewer-handbook-first-knowledge
status: draft
created_at: 2026-10-26
---

# [PADR-handbook-first-book-on-request] Handbook first, Living Spec book on request

- **Status**: Draft
- **Date**: 2026-10-26

---

## 1. Context & Problem Statement

The viewer's Book rail tab (`view` id `book`, the Living Spec reading tab of `CAP-VIEW-repository-viewer` §4, whose label there differs from the
code's) indexes every
Markdown file under `docs/` and `specs/` and renders every Living Spec chapter as soon as it opens. On this
repository that is about 1.1 s, 922 blob reads and 124k DOM nodes before anything is readable, of which about
0.47 s is rendering (`MAT-viewer-handbook-cold-load`). The release handbook (`CAP-DLV-release-handbook`) is the
entry point written for people, but the viewer does not show it, and `CAP-DLV-release-handbook` §2 lists that as out
of scope with a reason that no longer holds: the viewer reads the working tree (`ADR-viewer-working-tree`), where
`handbook/` is an ordinary directory.

Only this repository has a handbook (the playbook is in the repository-only `devkit-dev` bundle), the viewer serves
several repositories, and the handbook trails the current `docs/` between refreshes, so the book must stay reachable.

Parts marked "pending" follow the recommended answer of this Planning run's questions and change with the answer.

## 2. Decision Drivers

- The first read of the tab is the person-oriented one where it exists.
- No index or book rendering before a person asks for the current contracts.
- Unchanged book content and order once computed.
- No new write path, endpoint or Git process; library hosts keep their `RepositoryDataSource`.
- Hosts keep the `book` view id, `initialView` and the `sdd:path-change` event.

## 3. Considered Options

- **Handbook first, book on request (one tab)**: the tab opens the handbook or an absence note and offers a
  "Living Spec book" control; one rail entry, no cold cost, one extra selection for the book.
- **Separate Handbook tab, Book on request**: two rail entries; the same costs, but the two reading modes of one
  question ("what is this repository") are split, and a repository without a handbook shows an empty tab.
- **Keep the book eager, add a Handbook tab**: no change for book readers; the cold cost stays for anyone who opens
  the book tab first.
- **Viewport rendering of the book** (`FB-viewer-book-rendering`): keeps the book first and cuts DOM and render
  work, but still pays the 0.6 s, 922-read index and risks jumps and heading tracking.
- **New backend endpoint for handbook pages**: a dedicated listing; duplicates `tree` and `blob`, which already read
  `handbook/` with the same path, symlink and `.git` guards, and needs a new method in every host's data source.

## 4. Decision Outcome

Chosen: handbook first, book on request, in one tab.

- **Tab** (pending `tab-shape`): the rail entry keeps the `book` id; its label becomes "Read" and its title
  "Handbook and Living Spec book".
- **Detection and reads**: the tab reads `handbook/manifest.json` through the existing `blob` read; `404
  VIEWER_PATH_NOT_FOUND` means no handbook. A readable manifest with `en` in `langs` opens the handbook; any other
  read or parse failure shows the error and the book control. Pages are read one at a time through `blob`; no new
  endpoint, Git process or data-source method.
- **Pages**: a page renders through the existing Markdown, frontmatter and DOMPurify path, without the Living Spec
  index. A relative link to another `.md` page under the same `handbook/<lang>/` opens that page in the tab; a link
  that leaves `handbook/<lang>/` or names a missing page is shown as unavailable, never read outside it.
- **Source links** (pending `source-links`): `https://github.com/<repository>/blob/<tag>/<path>` links stay external
  and open in a new browsing context.
- **Language**: a switch lists the manifest's `langs`; the viewer remembers the choice in browser storage for all
  repositories and otherwise starts with the browser language if listed, else `en`. Switching keeps the page's
  relative path, which `CAP-DLV-release-handbook` §3.1 rule 1 guarantees in every language.
- **No handbook**: the tab shows that the repository has no `handbook/manifest.json` and the book control.
- **Book on request**: no `indexDocuments` call and no `renderDocument` call happens in the tab before the control is
  selected. After it, the book is computed as today, with the same content and order. The choice of the book stays
  for the page session per repository and branch; its data follows the existing 30-second caches.
- **Deep links** (pending `book-deep-links`): a host request (`initialView` `book` with an `initialPath` under
  `docs/`) or an in-page jump into a Living Spec document counts as the request and computes the book; a path under
  `handbook/` opens that handbook page. `sdd:path-change` keeps `view: "book"` and carries the handbook page path in
  handbook mode.
- **Staleness**: `PADR-handbook-staleness-from-version`.
- **Contracts**: `CAP-VIEW-repository-viewer` §4 states the tab's default, the handbook source and the on-demand
  book; `CAP-DLV-release-handbook` §2 drops the viewer from Out-of-Scope.

## 5. Consequences

- Positive: the tab's cold load drops from about 1.1 s and 922 reads to two reads with a handbook, or one without;
  autohub gets the handbook through its existing data source.
- Negative: a reader who wants the current contracts selects the control once per session; the handbook's ID
  citations are not in-page links to the book.
- Risk: a deep link into a book chapter still costs the full book; Proposals and Specs keep the 0.6 s index
  (`FB-viewer-knowledge-anchor-loading` stays open).
- Follow-up: when book rendering after the request is reported as slow, revisit viewport rendering.

## 6. Confirmation

- Frontend tests in Development (`frontend/src/lib/features/knowledge/`): a manifest opens the handbook; its
  absence shows the note; no `tree` or `blob` call under `docs/` or `specs/` happens before the control; the computed
  book equals today's chapter list; a handbook link leaving `handbook/<lang>/` reads nothing.
- Integration test (`tests/integration/features/browse/`): `handbook/` pages and the manifest read through `blob`
  keep the symlink and `..` refusals.
- The cold-load probe of `MAT-viewer-handbook-cold-load` rerun against the change.
