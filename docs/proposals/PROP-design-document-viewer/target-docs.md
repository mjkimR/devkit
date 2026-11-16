---
id: PROP-design-document-viewer-target
title: Formal document viewer target blueprint
summary: "Plans complete formal-kind reading, references, artifacts, namespace navigation and public/static viewer delivery."
status: draft
proposal: PROP-design-document-viewer
targets:
  - file: docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
  - file: docs/usecases/viewer/UC-read-formal-document.md
  - file: docs/ux/viewer/UX-browse-formal-documents.md
  - file: docs/ux/viewer/UX-formal-document-relations.md
  - file: docs/ux/viewer/UX-read-supporting-artifact.md
  - file: docs/steering/ux-objects.md
  - file: docs/development/reference/viewer.md
  - file: docs/capabilities/delivery/CAP-DLV-release-handbook.md
---

# [PROP-design-document-viewer-target] Formal document viewer target blueprint

This is a future contract for `PROP-design-document-viewer`; current owner documents remain unchanged in Planning.
New UC/UX identifiers below are proposed names, not references to existing documents.

## 1. Direction and options

| Complete-support option | Evidence and cost | Risk | Disposition |
| --- | --- | --- | --- |
| Explicit browser consumer table and shared rendering | Existing browser parser and allowlists; extend local prefix/group/relation consumers and test against delivered core examples | Drift if later core changes bypass consumer tests | Selected: retains `ADR-repository-viewer` version-tolerant repository reads and public data-source contract |
| Server-published kind registry drives browser | Requires a versioned metadata endpoint, public host capability negotiation and schema transport; generic blob/tree sources lack it | Breaks or bifurcates third-party sources without a fallback, adds contract beyond current need | Not selected; reconsider only if core later publishes such transport as its own supported contract |

Both provide formal Kind/ID standing. Neither treats ID-free linked content as a substitute. A local consumer table
is presentation/recognition data, not authority to create new relations or loosen core syntax. It can share a small
frontend module where that removes inconsistent recognizers. No package, feature or test tier is added.

## 2. Core interface and sequencing

`SPEC-formal-document-kinds` is a hard implementation prerequisite, including the decision superseding ID-free
clauses in `ADR-documentation-ownership-and-linked-design-entries` and `ADR-linked-domain-relationship-views`.
The selected future core contract is pinned in [core contract](materials/core-contract.md). Artifact adapter is
`local`, repository namespace `7a98ea4b0c7772e588edcd66b2dc51119340c3fcb7b9cb304c1e67ffbe3d8302`, source commit
`504e2e12006ab3e2aad2b8ce470607646ad4c4ac`, generation `074444d7a3e0468892b50274650c69f2`, content SHA-256
`1d724834426991e04904fd9f1677f60235de49764d9a1863ad9c8d112c55f413`. Adapter/namespace/source/hash were compared
with the Host pin; local copy bytes match. This is selected contract data, not current-runtime proof. Development
must consume the delivered core implementation and reconcile any material difference before dependent verification.

| Kind / prefix / directory | Canonical shape | Applicable data |
| --- | --- | --- |
| design / DESIGN / designs | `<root>/designs/DESIGN-<word-led-slug>.md` | Optional source `entrypoints`; formal independent details use peer files with their own IDs |
| domain / DOMAIN / domain | `<root>/domain/DOMAIN-<word-led-slug>.md` | Concept/identity/relationship/lifecycle knowledge; no entrypoints field |
| operations / OPS / operations | `<root>/operations/OPS-<word-led-slug>.md` | Symptom/evidence/action-owner/normal-state routing; no entrypoints field |

Roots are global docs or registered docs/packages/<name>. Required nonempty id/title/status/summary; H1 and stem
match ID; no area field. Status draft/active/retired; default list/search hides retired, explicit history/status and
direct reference resolution retain it. Aliases are same-prefix IDs, globally unique across namespaces. All indexed
source kinds may use target-typed list fields related_designs, related_domains, related_operations, alongside
applicable existing CAP/UC fields. Preserve generic spec/plan current references. Role documents reject delivery
proposal/decomposed_from/depends_on/milestone and ADR supersedes/superseded_by fields. Role retirement is a status,
prose replacement explanation and optional related_* successor, not ADR supersession. Existing provenance on its
owning kinds remains distinct. No reciprocal relation requirement is introduced.

Artifacts live under `<root>/<role-directory>/<PARENT-ID>/artifacts/<relative-path>` and link from their identified
parent. ID-free Markdown artifacts must remain outside canonical node lists, kind counts/search and reference graph
identity, even though the generic file scanner reads Markdown. They stay accessible as supporting files. An ID-bearing
artifact is invalid core input; viewer can still expose its file/raw content with uncertainty, never claim it is a
valid peer canonical node. Independent details are flat formal peer files, not nested inherited identities.

Updated core maintenance semantics are part of viewer fixtures. A same-kind rename moves the parent-owned
`<OLD-ID>/artifacts/` subtree to `<NEW-ID>/artifacts/`; a docs-root move carries it into the selected new root.
Identity aliases resolve only document IDs, never stale artifact paths or orphan old-ID folders. Follow repaired
ordinary links from the current canonical parent and preserve current source context. Split/cross-kind artifact
transfers have exactly one receiving canonical parent; cross-kind old nodes remain retired with an explicit
replacement reference. The viewer displays historical materials/prose coordinates as historical, without implying
an old path is a live artifact or source entrypoint. Retired DESIGN nodes remain rule-checked; deleted source
entrypoints are removed/replaced by core/lifecycle maintenance, while useful live anchors remain visible. No new
viewer recovery, path redirect or schema rule is introduced.

Require fixture walkthroughs after same-kind rename and namespace/root move, split and cross-kind artifact transfer:
old ID alias opens the canonical node and its moved artifacts; old ordinary file paths show missing rather than
alias magic; parent identity/source is correct after every transition. A retired DESIGN fixture with removed source
contains no obsolete live entrypoint, retains explicit source-commit prose when useful, and remains reachable by
ID/alias/ref/history. Include malformed stale-entrypoint/orphan-artifact controls as invalid core input and visible
unavailable file/source states; the viewer does not silently repair or validate repository governance.

The viewer remains browser-parsed and accepts unknown metadata without rejecting older/newer repositories.
Known formal fields get typed presentation and links. Unknown fields stay inspectable through metadata/raw source.
Malformed fields produce visible incomplete metadata/reference information, not fabricated targets or a successful
empty graph. Alias declarations establish identity; they never create graph edges. Alias navigation displays the
canonical ID and preserves the written alias in relation context. Duplicate/ambiguous identities are unavailable
links with the written ID, not an arbitrary first match. Structured current relations and prose refs appear as
incoming/outgoing graph rows with source/field context; provenance is a distinct labelled section and does not
claim present authority. Preserve existing historical spec/material representations and source labels.

Identity recognizers match the core permissive `ID_SOURCE`: `<known-prefix>-[A-Za-z0-9][A-Za-z0-9_-]*`.
Do not replace this with canonical word-led path/slug governance. Explicit tests include underscore IDs and same-kind
aliases in prose and ADR statements for DESIGN, DOMAIN and OPS, plus malformed controls. Core owns path/H1 validity.
Use the core's visible-reference rules for comments, fenced/indented code, exact inline IDs, and statement-level
supersession. Extend `supersession.ts` target-ID recognition for all three prefixes. Retain ADR/PADR-only decision
summary UI unless the delivered core explicitly changes the domain rule; formal-node reference rows are not a
claim that every document is a decision.

No Python feature edge is introduced: `.devkit/architecture.toml` viewer `feature_dependencies.browse` remains
`devkit_dist.features.project`, `devkit_dist.features.shared`. The selected design adds no docs-model import.
If that changes, stop and declare the exact `devkit_docs.features.documents` edge under the viewer package's
`feature_dependencies.browse`, dependency/public-module contracts and `ARCH-05-2-components` before implementation.

## 3. Capability and documentation ownership

| Target | Future contract |
| --- | --- |
| `CAP-VIEW-repository-viewer` §§4.3,6 | Explicit chapter order/labels, namespace visibility, three kinds in index/list/search and deep links, metadata/reference graph/artifact/error contracts; extend the lazy index trigger to rendered formal Files nodes; existing unrelated budgets/cache/security retained |
| UC-read-formal-document | Goal: find a formal document and follow its authority/detail/artifact context; 1 request Living Spec book, 2 choose namespace/group or search, 3 read formal node, 4 inspect incoming/outgoing relations, 5 follow detail/artifact, 6 return; extensions cover empty, unresolved, missing, unsupported and stale source |
| UX-browse-formal-documents, UX-formal-document-relations, UX-read-supporting-artifact | Screens below, linked in both directions with new UC and existing CAP |
| `UC-read-decision-supersession`, `UX-view-decision`, `UX-decision-supersession` | Recheck ADR/PADR interaction and unavailable-state regression; change only statements actually affected by shared panel/link behavior |
| docs/steering/ux-objects.md | Add shared formal Design, Domain, Operations, Reference and Supporting artifact rows using the core glossary terms; retain Decision/Proposed decision/Supersession relation rows |
| docs/development/reference/viewer.md and `CAP-DLV-release-handbook` | Public library examples, navigation/deep links, source lookup/inclusion policy and verification commands |

Core/lifecycle workers may touch neutral owner contracts and glossary. Viewer does not rewrite their schema or
canonical role documents. Host schedules any overlapping reference/architecture edits after core; Planning can be
parallel, while implementation and reconciliation consume the delivered core. This is not a mandatory all-layer
update for every future code change. No operations recovery, proprietary editor or new approval action is added.

## 4. Navigation and source behavior

Chapter order: Overview, Architecture, Domain, Capabilities, Use Cases, UX, Designs, Operations, Steering, Decisions,
Development. The three labels are explicit: Domain, Designs, Operations. Global and each structural package docs
root use the same order; no formal role falls through to Overview. Formal independent detail peer nodes appear
under their own identity in the appropriate group. Parent-owned artifacts remain links and never become invented
formal IDs. README exclusions and historical material/proposal exclusions retain existing behavior.

Preserve `ADR-viewer-namespace-roadmap-discovery`: book visibility is structural file discovery, whereas registered
namespace validity is a core document contract. Do not claim that every visible docs/packages directory is registered
or invoke repository-local Python to validate it. Test registered namespace fixtures positively and unregistered
structural visibility separately. Preserve namespace selection, exact path/anchor deep links and source isolation.

Book/group list and its search include all three kinds and canonical/alias IDs as well as current supported title
and text fields. Default book navigation/search excludes retired formal nodes; Include retired exposes them. Keep the complete
loaded identity index for direct ID/alias links and graph targets. Direct opening a retired node shows its retired
status and the selected target without silently enabling other hidden history. Reference/deep-link targets remain reachable when prior filters hide them; visibly select the
target context. Missing targets show their written ID/path with an unavailable explanation, never a silently empty
or Overview result. Unsupported unknown kinds retain readable generic files without claiming formal validity.

Resolve relative Markdown/detail/artifact links from the source document path and its source context; preserve
fragments, URI encoding, repository path/symlink guards and sanitization. Add a repository-source artifact resolver for relative `a[href]` and `img[src]`: current renderDocument only
rewrites indexed Markdown anchors and does not load supporting blobs. Resolve assets using the existing
RepositoryDataSource.blob contract, preserving UTF-8/base64 bytes and source context. Display safe image formats
through bounded object URLs, revoke URLs on replacement/disposal, and retain DOMPurify plus explicit MIME/format
handling. Markdown examples and Mermaid use existing rendering; CSV/diagram source use readable text/raw.
No binary body is blindly decoded as UTF-8. A dedicated supporting-file surface uses the shared renderer/raw
components, not a new editing engine. Images must be reachable and display when supported. Unsupported binary formats show the existing
unsupported state and an available file/raw/download action only when the data source supports it. No promise of a
new binary preview is made. Missing files retain context and a back action. A graph is complete only for the loaded
index; load/read errors remain visible with retry. Extend the existing lazy index trigger from rendered ADR/PADR Files nodes to rendered DESIGN/DOMAIN/OPS Files
nodes. A cold Files read must load the same canonical ID links, metadata and reference panel as Read without a prior
book request. Share the formal panel across Read and Files. Raw files, supporting artifacts and handbook reads do
not trigger an identity index merely by opening; switching a formal Files node from raw to rendered may request
it. Preserve existing cache generations, cancellation and unrelated handbook-first/index budgets. Test cold Files
access for each kind, direct/alias links, relation failure/retry, source switches and raw-mode no-index reads.

## 5. Screens

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

## 6. Implementation and verification

The complete per-kind matrix and exact source/test owners are [support matrix](materials/support-matrix.md).
Cold Files participation and permissive underscore-ID/alias recognition are required alongside book paths.
Every row must be completed for design/domain/operations, with actual new-kind fixtures and existing-kind controls.
Generic code reuse is permitted only with passing behavior evidence. Public TypeScript/HTTP contracts remain
backward compatible; new optional presentation data cannot become required host callbacks or exports.

Run Python lint and `just check`, `just test-affected` with its `mode=full` fallback. Run focused handbook regression.
Run the actual `[FRONTEND_CHECK: ...]` line from affected tests: `just viewer install`, `just viewer lint`,
`just viewer check`, `just viewer test`, `just viewer pack`, `just viewer build`. Use the declared generator for
committed static assets, then `uv run devkit generated check viewer-assets`; inspect packed library and Python
wheel contents and exercise a host importing the public exports with generic RepositoryDataSource fixtures.
No generated output is hand-edited. No release refresh, publishing, or downstream consumer write is in scope.
