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

- **Tab** (decided by the user): the rail entry keeps the `book` id; its label becomes "Read" and its title
  "Handbook and Living Spec book".
- **Detection**: the tab reads `handbook/manifest.json` through the existing `blob` read. A rejection whose message
  matches the existing absent-path convention `/^HTTP 404(?:\b|:)/` (`scanDocuments` in `api/documents.ts`) means no
  handbook; `CAP-VIEW-repository-viewer` §6 states that a host's `blob` signals an absent file that way. A readable
  manifest with `en` in `langs` opens the handbook; any other failure shows the error and the book control.
- **Read budget before the control**: with a handbook, the manifest, `VERSION` and one page; without one, the manifest
  alone. No `tree` or `blob` under `docs/` or `specs/`. No new endpoint, Git process or data-source method.
- **Pages**: a page renders through the existing Markdown and DOMPurify path, without the Living Spec index.
  - A relative link to another `.md` page under the same `handbook/<lang>/` opens that page in the tab; a link that
    leaves `handbook/<lang>/` is shown as unavailable and reads nothing. A missing page shows an error with the home
    entry.
  - A fragment resolves to an element whose `id` equals it, else to the prefixed heading slug, so the English
    heading slugs and the Korean raw anchors (`<a id="journeys">`) both scroll.
- **Navigation**: in handbook mode the sidebar shows a "Handbook home" entry (`README.md`), the language switch, the
  book control and the current page's headings; it needs no extra read. Every page's generated table of contents
  provides the page list.
- **Source links** (decided by the user): `https://github.com/<repository>/blob/<tag>/<path>` links stay external
  and open in a new browsing context.
- **Language**: the switch lists the manifest's `langs`; the viewer remembers the choice in browser storage for all
  repositories and otherwise starts with the browser language if listed, else `en`. Switching keeps the page's
  relative path, which `CAP-DLV-release-handbook` §3.1 rule 1 guarantees in every language.
- **No handbook**: the tab shows that the repository has no `handbook/manifest.json` and the book control; Proposals
  and Specs are separate rail tabs and unchanged.
- **Two gates in the shared component**: one `KnowledgeViews` instance serves Book, Proposals and Specs.
  - Book rendering runs only while `view === 'book'` and the book was requested; an index loaded by Proposals or
    Specs never renders the book on its own.
  - The index runs from a latch set by the first Proposals or Specs view or by the book request; it never resets on a
    view change, so switching between the three views starts no second scan.
- **Request state**: the book request lives in `SddViewer` for its lifetime and is passed to `KnowledgeViews` as a
  bindable prop, so it survives rail switches and resets with a repository or branch switch, which the page already
  remounts. A standalone `KnowledgeViews` host binds the prop to keep it. The data follows the existing 30-second
  caches.
- **Deep links** (decided by the user; library hosts only, since the standalone page opens on the Dashboard
  and no Dashboard card targets `book`): a host request with `initialView` `book` and an `initialPath` naming a file
  under `docs/`, not the default `docs/`, counts as the book request; a path under `handbook/` opens that page.
  `sdd:path-change` keeps `view: "book"` and carries the handbook page path in handbook mode.
- **Staleness**: `PADR-handbook-staleness-from-version`.
- **Contracts**: `CAP-VIEW-repository-viewer` §4 states the tab's default, the handbook source and the on-demand
  book, and §6 the absent-file signal; `CAP-DLV-release-handbook` §2 drops the viewer from Out-of-Scope.

## 5. Consequences

- Positive: the tab's cold load drops from about 1.1 s and 922 reads to three small reads with a handbook, or one
  without; autohub gets the handbook through its existing data source.
- Negative: a reader who wants the current contracts selects the control once per viewer session; the handbook's ID
  citations are not in-page links to the book; tag-pinned source links fail until the tag is pushed.
- Risk: after the request the book costs what it costs today, and returning to the tab re-renders it (about 0.47 s);
  Proposals and Specs keep the 0.6 s index (`FB-viewer-knowledge-anchor-loading` stays open).
- Follow-up: `FB-viewer-book-rendering` stays open, rescoped to rendering after the request; revisit it when that
  rendering is reported as slow.

## 6. Confirmation

- Frontend tests in Development (`frontend/src/lib/features/knowledge/`, `frontend/src/lib/SddViewer.test.ts`):
  - a manifest opens the handbook within the read budget; its absence shows the note and the control;
  - no `tree` or `blob` under `docs/` or `specs/` and no `section.chapter` element before the control, also after
    Proposals loaded the index;
  - Book, Proposals and Book again start one index scan;
  - the request survives a Dashboard visit;
  - the computed book equals today's chapter list;
  - a handbook link leaving `handbook/<lang>/` reads nothing; a cross-page fragment scrolls in `en` and `ko`.
- Integration test (`tests/integration/features/browse/`): `handbook/` pages and the manifest read through `blob`
  keep the symlink and `..` refusals.
- The cold-load probe of `MAT-viewer-handbook-cold-load` rerun against the change, with the tab label and readiness
  selector as arguments.
