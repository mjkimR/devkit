---
id: SPEC-viewer-handbook-first-knowledge
title: Handbook-first knowledge view with on-demand book
summary: Makes the repository viewer's knowledge tab open the release handbook when a repository has one and compute the Living Spec book only on request, so cold loads skip rendering every document.
status: planned
created: 2026-10-26
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---
<!-- devkit:skeleton -->

# [SPEC-viewer-handbook-first-knowledge] Handbook-first knowledge view with on-demand book

## 1. Problem Statement & Motivation

Handed off from proposal PROP-viewer-handbook-first-knowledge on 2026-10-26.
- **Preserved Materials**: `docs/materials/2026-10/20261026-viewer-handbook-first-knowledge`

### 1. Background & Hypothesis

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

## 2. User Stories

- **US-1**: As a developer/agent, I want to implement Handbook-first knowledge view with on-demand book so that system capabilities are extended.

## 3. Non-Goals

1. **Scope Excluded**: <what this change will not do>

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] <scenario>
- **Given** <precondition>
- **When** <action>
- **Then** <expected result>

## 5. Carried Proposal Notes

Sections of the proposal that did not map to a spec section. Trim or promote them while drafting; they are not contracts.

### 2. Technical Spike Questions

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

### 3. Proposed Design & Impact

- A repository with `handbook/manifest.json` opens the knowledge tab on the handbook, in the selected language, with
  its release tag and a staleness note.
- A repository without one opens the same tab on a note that it has no `handbook/manifest.json`. In any repository,
  the book is computed only after the viewer selects a "Living Spec book" control; Proposals and Specs are unchanged.
- The book keeps its current content and order once computed; only when it is computed changes.
- Backend: no new endpoint. The existing `tree` and `blob` reads already serve `handbook/` with the working-tree
  path, symlink and `.git` guards; Development adds integration tests for them and no write path.
- Contracts: `CAP-VIEW-repository-viewer` states the knowledge tab's default view, the handbook source and the
  on-demand book; `CAP-DLV-release-handbook` §2 drops "showing the handbook in the repository viewer" from its
  Out-of-Scope list; the viewer reference and README follow.
- Interaction: `PROP-ux-documentation` and `PROP-table-driven-document-kinds` also own viewer frontend paths;
  this proposal is developed first (§5).

Scope excluded: generating or refreshing the handbook, changing its format, removing the book, and viewport-level
virtualization unless Q6 shows on-demand computation is not enough.

### Source feedback

- `FB-viewer-book-rendering`: addressed for the cold load only; its rendering after the request stays in its own
  scope (Planning decisions, §5).
- `FB-viewer-knowledge-anchor-loading`: not addressed; Proposals and Specs keep their index.

### 4. Lifecycle & Retirement Criteria

- Planning settles Q1-Q6 with a cold-load measurement and decides the fate of `FB-viewer-book-rendering` and
  `FB-viewer-knowledge-anchor-loading` (absorbed, kept or dismissed).
- Acceptance requires:
  - the handbook default only where a manifest exists, and the absence note otherwise;
  - before the explicit control, a frontend test shows at most the read budget (manifest, `VERSION` and one page
    with a handbook; the manifest alone without), no `tree` or `blob` under `docs/` or `specs/` and no
    `section.chapter` element, also after Proposals loaded the index;
  - unchanged book content and order once computed;
  - read-only handbook serving with path safety;
  - the cold-load probe of `MAT-viewer-handbook-cold-load` rerun against the change, showing the reduction in blob
    reads and DOM nodes;
  - the viewer frontend checks (`just viewer lint`, `check`, `test`, `build`) with the committed page rebuilt.
- Retire when the knowledge tab contract in `CAP-VIEW-repository-viewer` states the handbook-first default and the
  on-demand book.

### 5. Planning Findings

Evidence: `MAT-viewer-handbook-cold-load` (cold-load baseline), `ADR-handbook-first-book-on-request`,
`ADR-handbook-staleness-from-version`.

- **Q1**: the Book rail tab (`view` id `book`) can detect a handbook by reading `handbook/manifest.json` through the
  existing `blob` read (a rejection matching the existing `/^HTTP 404/` absent-path convention when absent) and read
  pages one at a time the same way. Path, symlink and `.git` guards already apply; library hosts need no new
  `RepositoryDataSource` method.
- **Q2**: pages render through the existing Markdown and DOMPurify path without the Living Spec index; the
  `sources` and `translated_from` frontmatter maps are not displayed by the existing headers. Relative links and
  fragments stay inside `handbook/<lang>/`; a "Handbook home" entry and the page headings form the sidebar; the
  language switch lists the manifest's `langs`, is remembered in browser storage and keeps the page path, which
  parity guarantees. Source links stay external, tag-pinned GitHub links (user decision), which fail until the tag is pushed.
- **Q3**: "on request" is a "Living Spec book" control. The shared `KnowledgeViews` instance gets two gates: book
  rendering only while the Book view is shown and requested, and an index latch that never resets on a view change.
  The request lives in `SddViewer` for its lifetime, as a bindable prop, so it survives rail switches; its data
  follows the existing 30-second caches. A library host request with `initialView` `book` and a file path under `docs/` (not the default `docs/`) counts
  as the request and computes the full book (user decision).
- **Q4**: without a manifest the tab shows the absence (no `handbook/manifest.json`) and the book control; Proposals
  and Specs are separate rail tabs and are unchanged.
- **Q5**: both `VERSION` and the latest Git tag trail the manifest between a refresh and its release (`v0.1.4`
  manifest against `0.1.3` and `v0.1.3` at Planning time), so equality reports a fresh snapshot as stale. The
  user chose ordering the manifest tag against `v<VERSION>`, read as a file without Git
  (`CAP-VIEW-repository-viewer` §2): ahead is a snapshot for the upcoming release, behind shows the note.
- **Q6**: on this repository the Book tab cold takes about 1.1 s, 922 blob reads and 124k DOM nodes, of which about
  0.47 s is rendering; the handbook's first read is three small reads (two measured under 10 ms). On-demand computation removes all of it
  from the cold load, so viewport rendering is not needed. The 0.6 s, 922-read index remains the cold cost of
  Proposals and Specs.

#### Planning decisions

- User decisions (historical Git `8d58c58713a72e7a0439e71dd0143fade2c32734:docs/proposals/PROP-viewer-handbook-first-knowledge/envelopes/answer-01.yaml`): one tab keeps the `book` id with the label "Read"; a library host's
  deep link into a `docs/` file computes the full book; source links stay external and tag-pinned; staleness orders
  the manifest tag against `v<VERSION>`; `FB-viewer-book-rendering` stays open.
- `FB-viewer-book-rendering`: kept open by the user's decision, rescoped to rendering after the request (about
  0.47 s per return to the tab), because on-demand computation removes its cold-load cost but not the rendering it
  describes (`source-feedback` resolves only a fully addressed source).
- `FB-viewer-knowledge-anchor-loading`: kept open. Proposals and Specs still index all of `docs/` and `specs/`
  (about 0.6 s, 922 reads); this proposal does not change that.
- Sequencing: develop this proposal before `PROP-table-driven-document-kinds` and `PROP-ux-documentation`, both
  draft, which own the same frontend paths through `bookGroup`/`bookGroups`; the table-driven change keeps outputs
  identical and can move the book grouping afterwards.
- Boundary: `docs/capabilities/delivery/CAP-DLV-release-handbook.md` joins `owns` for its Out-of-Scope line only.
- Baseline: `MAT-viewer-handbook-cold-load` is the base measurement, taken on the Planning machine; Development
  reruns its probe against the change and compares blob counts and DOM nodes, and milliseconds on the same machine.

