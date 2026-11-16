---
id: SPEC-design-document-viewer
title: First-class formal documentation in the repository viewer
summary: "Makes formal design, domain and operations directly readable through canonical and alias links, reference context, source-safe artifacts and shipped viewer output."
status: in-progress
created: 2026-11-16
depends_on: [SPEC-formal-document-kinds]
related_capabilities: [CAP-VIEW-repository-viewer, CAP-DLV-release-handbook]
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-design-document-viewer] First-class formal documentation in the repository viewer

## 1. Problem Statement & Motivation

The delivered formal core supplies identities and ownership. The browser viewer still lacks formal groups,
alias links, retirement controls, current reference context and byte-safe supporting files. Generic loading
alone does not establish support. The accepted blueprint `PROP-design-document-viewer-target` and its
[complete matrix](../../../docs/materials/2026-11/20261116-design-document-viewer/support-matrix.md) control V1–V4.

## 2. User Stories

- **US-1**: As a reader, I find each formal kind and follow canonical, alias and incoming/outgoing references.
- **US-2**: As a reader, I inspect a linked detail, image or datasheet and return to its exact source context.
- **US-3**: As a host, I consume the public library and shipped page with existing source callbacks.

## 3. Non-Goals

1. **Scope Excluded**: Core schema/governance or lifecycle changes; the core and lifecycle units own them.
2. **Scope Excluded**: Editors, recovery actions, new required host callbacks or Python document-engine dependency.
3. **Scope Excluded**: Handbook refresh/publication or automatic pages for every formal document.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Identity and navigation
- **Given** DESIGN, DOMAIN and OPS nodes in global and structural package roots, aliases and independent details
- **When** a reader browses, searches or follows a prose, code or direct reference
- **Then** explicit Domain/Designs/Operations groups and canonical/alias resolution work with core permissive IDs; ambiguous/missing targets stay unavailable and artifacts stay outside canonical navigation.

### [AC-02] Current and historical reading
- **Given** active and retired formal nodes, filters and namespace selection
- **When** normal browsing or a direct canonical/alias/reference link opens a node
- **Then** normal navigation hides retired nodes, Include retired exposes them, and a hidden direct target alone is materialized with its status and source context.

### [AC-03] Reference context and cold Files
- **Given** any indexed source with current typed/prose references and separately labelled provenance
- **When** a formal node opens in Read or cold rendered Files
- **Then** one shared panel shows metadata, incoming/outgoing canonical references, unresolved/ambiguous and incomplete/error/retry states; raw/artifact/handbook reads do not trigger an identity scan.

### [AC-04] Source-safe supporting files
- **Given** relative Markdown, image, CSV/diagram text or unsupported links from a document
- **When** they are read through the existing data source
- **Then** URI/path/source/abort context and bytes are preserved, safe images display, URLs are disposed, missing/unsupported states retain path and Back, and Planning never falls back to checkout.

### [AC-05] Source controls and maintenance routes
- **Given** a formal node and artifact after rename/root move/split/reclassification or retirement
- **When** a reader follows an alias or ordinary path and toggles raw/rendered or Back
- **Then** aliases find current identities, ordinary obsolete paths remain missing, source coordinates remain labelled, and parent context is retained without changing permissions.

### [AC-06] Backend, public and packaged parity
- **Given** the generic tree/blob backend and public RepositoryDataSource interface
- **When** actual formal/namespace/artifact fixtures, frontend checks, library packaging and wheel inspection run
- **Then** guards and bytes remain correct, public callbacks remain compatible, generated static output matches source and all required checks pass.

### [AC-07] Handbook and UX
- **Given** formal canonical IDs/aliases cited by a handbook author and the accepted screen drafts
- **When** source lookup/staleness and implemented reading interactions are checked
- **Then** all prefixes are recognized while CAP/UC required coverage and ADR/SPEC generated membership remain unchanged; use cases, UX register and current viewer contracts agree.

### [AC-08] Delivered bundle and area grammar
- **Given** the design bundle and domain area grammar delivered by `SPEC-design-bundle-layout` at `002241b56fd8e5a446cbfa4f2e4bf42d25484455`
- **When** current formal documents, supporting files and area/root/rename moves are read in Read, Files and handbook source lookup
- **Then** designs and domain nodes are grouped by area, design anchors display their canonical bundle ID, all non-anchor bundle files are parent-owned support, Domain/OPS retain their applicable support paths, and current real retained documents and public source callbacks work without a second identity registry.

## 5. Screens

The following accepted drafts existed and received two independent UX rounds before production code. Specify
initially linked them; build-verify carries their bodies here to correct that record-placement omission. The
arrangement is unchanged, and the implementer's closure checks all retained findings against actual behavior.


Two arrangements were compared: (A) extend the existing Read chapter sidebar and place a relation panel below the
formal document header; (B) add a separate formal-documents rail tab with kind-filtered cards and a separate detail
page. A is recommended because the task already begins in the Living Spec book and keeps cross-kind references in
one source/index context. B meets formal standing but duplicates book navigation and adds a tab without a distinct
goal. Optional `ux-reviewer` review is offered for A before code; its use is not a gate. No visual style decision:
reuse `frontend/src/lib/features/knowledge/KnowledgeSidebar.svelte`, document components and `frontend/src/app/` styles.

### UX-browse-formal-documents (screen draft)

**Purpose:** Find and read a formal node. Facts: selected repository/branch, namespace, kind/group, canonical ID,
title, summary and status. An Include retired control exposes historical formal nodes. Primary region: selected document/book; secondary: chapter navigation and filters.

**Content tree:** Repository/branch context; Rendered/Raw source control; Read mode and Living Spec book control; namespace selector; chapter
navigation with Domain, Designs, Operations; Include retired control; matching document ID/title entries; selected formal node header and
body; linked independent details and supporting artifacts; UX-formal-document-relations panel.

| State | Representation and next action |
| --- | --- |
| handbook | Existing manifest/page and Living Spec book control; no docs scan before request |
| loading | Source-labelled loading state; back/switch remains available |
| populated | Explicit group entries and canonical node/body; follow a link or return |
| empty | No matching documents; clear search/select another group or namespace |
| error | Read/index failure with source context and retry; retain successfully loaded content |
| missing | Requested ID/path unavailable; show written target and back/retry |
| raw | Original source and metadata; Rendered control returns to the same document position |
| unsupported | Artifact path/format and explanation; supported raw/download action when available; Back retains prior document context |

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Request Living Spec book | UC-read-formal-document 1 | handbook | loading | | `CAP-VIEW-repository-viewer` | Index progress then chapters |
| Include retired | UC-read-formal-document 2 | populated/empty | populated/empty | | `CAP-VIEW-repository-viewer` | Historical nodes labelled retired; direct links still open without requiring this toggle |
| Choose namespace/group or search | UC-read-formal-document 2 | populated | populated/empty | | `CAP-VIEW-repository-viewer` | Matching IDs/count, selected scope |
| Open formal node/alias/deep link | UC-read-formal-document 3 | populated/loading | populated/missing | | `CAP-VIEW-repository-viewer` | Canonical ID/title and selected context |
| Inspect relations | UC-read-formal-document 4 | populated | populated | UX-formal-document-relations | `CAP-VIEW-repository-viewer` | Source-aware reference rows |
| Follow formal detail | UC-read-formal-document 5 | populated | populated/missing | UX-browse-formal-documents | `CAP-VIEW-repository-viewer` | Independent canonical detail header/body |
| Follow supporting file | UC-read-formal-document 5 | populated | loading | UX-read-supporting-artifact | `CAP-VIEW-repository-viewer` | Artifact path and source context |
| View raw / Rendered | global: inspect original source and unknown metadata | populated/raw | raw/populated | | `CAP-VIEW-repository-viewer` | Source or rendered body at retained context |
| Change repository/branch | UC-read-formal-document *a | populated/loading/error | loading | | `CAP-VIEW-repository-viewer` | Cancel old reads/context; show selected source loading, then handbook state; offer Living Spec book to resume step 1 |
| Return | UC-read-formal-document 6 | populated/missing/unsupported | populated | back | `CAP-VIEW-repository-viewer` | Prior reading context restored |

### UX-formal-document-relations (panel draft)

**Purpose:** Follow current authority and supporting context. Facts: subject canonical ID/source, relation direction,
written target ID, canonical title/status, field/origin, completeness. Primary region: current references; provenance
below it. Content tree: subject identity/metadata; outgoing/current references; incoming/current references;
provenance-labelled rows; independent detail/support links; incomplete-index notice and retry when needed.

| State | Representation and next action |
| --- | --- |
| loading | Pending reference scan; keep body readable; back remains available |
| populated | Direction/field-labelled linked rows; follow target or return |
| empty | No applicable references in complete loaded index; return to body |
| incomplete/error | Source/read/parse errors and retry; never claim no references |
| unresolved/ambiguous | Written ID with unavailable reason; no arbitrary navigation; retry/back |
| unsupported | Preserve unknown metadata in raw source; return to body |

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Open current relation or provenance target | UC-read-formal-document 4 | populated | populated/missing | UX-browse-formal-documents | `CAP-VIEW-repository-viewer` | Target canonical header and written-reference context |
| Retry incomplete index | UC-read-formal-document 4a | incomplete/error | loading | | `CAP-VIEW-repository-viewer` | Progress and fresh completeness state |
| Return to body | UC-read-formal-document 6 | populated/empty/unresolved/unsupported | populated | back | `CAP-VIEW-repository-viewer` | Reading position retained |

Register draft rows: Design/Domain/Operations, Developer reading repository, group entry/canonical header/body,
open document/view raw/follow reference; Reference, same role, direction/field/source/written ID/unavailable row,
follow target/retry; Supporting artifact, same role, parent link/path/format/status, open file/back. Core glossary
spelling is the final authority. Existing decision register rows remain.

### UC-read-formal-document flow draft

Main scenario: 1. Request Living Spec book in UX-browse-formal-documents. 2. Select namespace/group or search in
that screen. 3. Read selected canonical formal node there. 4. Inspect and follow current/provenance context in
UX-formal-document-relations, returning to UX-browse-formal-documents for a target. 5. Open an independent formal
detail in UX-browse-formal-documents or a supporting file in UX-read-supporting-artifact. 6. Return to the source
node/context using Back. Success: the reader reaches the intended identified node or support file and understands
its authority and source.

| Extension | Flow and resume point | Screen |
| --- | --- | --- |
| 2a empty results | Show selected filters and no matches; clear/change filters, resume 2 | UX-browse-formal-documents |
| 3a unavailable requested ID/path | Show written target and missing/ambiguous reason; Back resumes 2, retry resumes 3 | UX-browse-formal-documents |
| 4a incomplete/read error | Keep body and partial rows with completeness warning; Retry resumes 4 | UX-formal-document-relations |
| 4b unresolved/ambiguous target | Show written ID/unavailable reason; no arbitrary target; retry resumes 4 or Back resumes 3 | UX-formal-document-relations |
| 5a missing/unsupported file | Show artifact path/format/explanation; raw/download only when supported; Back resumes 3 | UX-read-supporting-artifact |
| *a source change | Cancel old reads/assets; show selected repository/branch; reset book request per existing CAP; complete loading into selected source handbook state and offer Living Spec book; resume 1 | UX-browse-formal-documents and UX-read-supporting-artifact |

### UX-read-supporting-artifact (screen draft)

**Purpose:** Read a parent-linked supporting file. Facts: parent formal ID, repository/branch/source, target path
and format. Primary region: supported content; secondary: source/raw/download controls and Back to parent.
**Content tree:** Parent ID/title and Back; artifact path/format/source; safe supported image or Markdown/Mermaid
preview, text/CSV/diagram source; Raw/download only for available blob bytes; failure explanation and Retry.
Reuse existing document/file renderer styles and source guards; no proprietary editing controls.

| State | Representation and next action |
| --- | --- |
| loading | Path and source with progress; Back cancels pending file load |
| populated | Supported content and file identity; view raw/download if applicable or Back |
| raw | Exact readable source; Rendered returns to preview, Back returns to parent |
| missing/error | Path and read failure; Retry or Back to parent |
| unsupported | Path/format and explanation; available blob download or readable raw only; Back preserves source position |

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Open file | UC-read-formal-document 5 | loading | populated/missing/error/unsupported | | `CAP-VIEW-repository-viewer` | Content or explicit path/format explanation |
| Retry | UC-read-formal-document 5a | missing/error | loading | | `CAP-VIEW-repository-viewer` | Fresh read progress |
| Raw / Rendered | global: inspect supporting source when readable | populated/raw | raw/populated | | `CAP-VIEW-repository-viewer` | Same artifact source/preview |
| Download | UC-read-formal-document 5a | populated/unsupported | populated/unsupported | | `CAP-VIEW-repository-viewer` | Download started when supported |
| Back | UC-read-formal-document 6 | populated/raw/loading/missing/error/unsupported | populated | UX-browse-formal-documents | `CAP-VIEW-repository-viewer` | Parent reading position restored; file read cancelled |
| Change repository/branch | UC-read-formal-document *a | populated/loading/error | handbook | UX-browse-formal-documents | `CAP-VIEW-repository-viewer` | Old file and URLs disposed; selected source shown |

Register row refinement: Supporting artifact uses path/format/source/content/unsupported explanation, open file,
view raw/download/Back. Original source control is represented in the formal node screen and toggles raw/rendered.


## 6. Baseline and measurement

Baseline 5d1cb2661871cd3fe12cf806b58ac2515a3ffaf4 has zero explicit formal groups and no shared formal panel.
The head has three explicit groups and the shared Read/Files panel, verified through all three kinds. This is
functional coverage, not a performance claim. Source-specific commands and package evidence are in
[development evidence](../../../docs/materials/2026-11/20261116-design-document-viewer/development-evidence.md).

## Source feedback

`FB-viewer-adopts-bundle-grammar` is a direct-fix source. Consume the delivered core path/area/support policy in
viewer navigation, metadata, graph and supporting-file discovery, handbook source lookup, tests and current UX.
Resolve it only after verified implementation and reconciliation; the core grammar itself remains core-owned.

## Delivered core reconciliation

The initial flat-contract pin remains immutable Planning provenance. The published core at
`002241b56fd8e5a446cbfa4f2e4bf42d25484455` and `ADR-area-scoped-design-bundles` now supply the current path and
area policy. This compatibility work preserves the accepted reading goals, IDs, source isolation and public
callbacks. A separate delivered-interface record distinguishes the current contract from the historical pin.
