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

`PROP-formal-document-kinds` is a hard implementation prerequisite, including the decision superseding ID-free
clauses in `ADR-documentation-ownership-and-linked-design-entries` and `ADR-linked-domain-relationship-views`.
Before implementation, pin its delivered commit and consume its Kind values, prefixes, directories, nested stem/H1
rules, status/summary schema, relation field applicability and scalar/list shapes, aliases, provenance/current refs,
statement supersession grammar, independent-detail policy and entrypoint applicability. Exact pending values are
coordination inputs; do not infer a competing schema from `related_capabilities` or add a viewer-only Kind.

The viewer remains browser-parsed and accepts unknown metadata without rejecting older/newer repositories.
Known formal fields get typed presentation and links. Unknown fields stay inspectable through metadata/raw source.
Malformed fields produce visible incomplete metadata/reference information, not fabricated targets or a successful
empty graph. Alias declarations establish identity; they never create graph edges. Alias navigation displays the
canonical ID and preserves the written alias in relation context. Duplicate/ambiguous identities are unavailable
links with the written ID, not an arbitrary first match. Structured current relations and prose refs appear as
incoming/outgoing graph rows with source/field context; provenance is a distinct labelled section and does not
claim present authority. Preserve existing historical spec/material representations and source labels.

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
| `CAP-VIEW-repository-viewer` §§4.3,6 | Explicit chapter order/labels, namespace visibility, three kinds in index/list/search and deep links, metadata/reference graph/artifact/error contracts; existing read budget/cache/security retained |
| UC-read-formal-document | Goal: find a formal document and follow its authority/detail/artifact context; 1 request Living Spec book, 2 choose namespace/group or search, 3 read formal node, 4 inspect incoming/outgoing relations, 5 follow detail/artifact, 6 return; extensions cover empty, unresolved, missing, unsupported and stale source |
| UX-browse-formal-documents, UX-formal-document-relations | Screens below, linked in both directions with new UC and existing CAP |
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
root use the same order; no formal role falls through to Overview. Formal independent nested detail nodes appear
under their own identity in the appropriate group. Parent-owned artifacts remain links and never become invented
formal IDs. README exclusions and historical material/proposal exclusions retain existing behavior.

Preserve `ADR-viewer-namespace-roadmap-discovery`: book visibility is structural file discovery, whereas registered
namespace validity is a core document contract. Do not claim that every visible docs/packages directory is registered
or invoke repository-local Python to validate it. Test registered namespace fixtures positively and unregistered
structural visibility separately. Preserve namespace selection, exact path/anchor deep links and source isolation.

Book/group list and its search include all three kinds and canonical/alias IDs as well as current supported title
and text fields. Reference/deep-link targets remain reachable when prior filters hide them; visibly select the
target context. Missing targets show their written ID/path with an unavailable explanation, never a silently empty
or Overview result. Unsupported unknown kinds retain readable generic files without claiming formal validity.

Resolve relative Markdown/detail/artifact links from the source document path and its source context; preserve
fragments, URI encoding, repository path/symlink guards and sanitization. Markdown examples, Mermaid/diagram source,
CSV/text and images use the existing supported render/raw/file route. Unsupported binary formats show the existing
unsupported state and an available file/raw/download action only when the data source supports it. No promise of a
new binary preview is made. Missing files retain context and a back action. A graph is complete only for the loaded
index; load/read errors remain visible with retry. Existing lazy index and handbook-first budgets remain intact.

## 5. Screens

Two arrangements were compared: (A) extend the existing Read chapter sidebar and place a relation panel below the
formal document header; (B) add a separate formal-documents rail tab with kind-filtered cards and a separate detail
page. A is recommended because the task already begins in the Living Spec book and keeps cross-kind references in
one source/index context. B meets formal standing but duplicates book navigation and adds a tab without a distinct
goal. Optional `ux-reviewer` review is offered for A before code; its use is not a gate. No visual style decision:
reuse `frontend/src/lib/features/knowledge/KnowledgeSidebar.svelte`, document components and `frontend/src/app/` styles.

### UX-browse-formal-documents (screen draft)

**Purpose:** Find and read a formal node. Facts: selected repository/branch, namespace, kind/group, canonical ID,
title, summary and status. Primary region: selected document/book; secondary: chapter navigation and filters.

**Content tree:** Repository/branch context; Read mode and Living Spec book control; namespace selector; chapter
navigation with Domain, Designs, Operations; matching document ID/title entries; selected formal node header and
body; linked independent details and supporting artifacts; UX-formal-document-relations panel.

| State | Representation and next action |
| --- | --- |
| handbook | Existing manifest/page and Living Spec book control; no docs scan before request |
| loading | Source-labelled loading state; back/switch remains available |
| populated | Explicit group entries and canonical node/body; follow a link or return |
| empty | No matching documents; clear search/select another group or namespace |
| error | Read/index failure with source context and retry; retain successfully loaded content |
| missing | Requested ID/path unavailable; show written target and back/retry |

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Request Living Spec book | UC-read-formal-document 1 | handbook | loading | | `CAP-VIEW-repository-viewer` | Index progress then chapters |
| Choose namespace/group or search | UC-read-formal-document 2 | populated | populated/empty | | `CAP-VIEW-repository-viewer` | Matching IDs/count, selected scope |
| Open formal node/alias/deep link | UC-read-formal-document 3 | populated/loading | populated/missing | | `CAP-VIEW-repository-viewer` | Canonical ID/title and selected context |
| Inspect relations | UC-read-formal-document 4 | populated | populated | UX-formal-document-relations | `CAP-VIEW-repository-viewer` | Source-aware reference rows |
| Follow detail/artifact | UC-read-formal-document 5 | populated | populated/missing/unsupported | file/detail surface | `CAP-VIEW-repository-viewer` | Target path/content or explanatory state |
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

## 6. Implementation and verification

The complete per-kind matrix and exact source/test owners are [support matrix](materials/support-matrix.md).
Every row must be completed for design/domain/operations, with actual new-kind fixtures and existing-kind controls.
Generic code reuse is permitted only with passing behavior evidence. Public TypeScript/HTTP contracts remain
backward compatible; new optional presentation data cannot become required host callbacks or exports.

Run Python lint and `just check`, `just test-affected` with its `mode=full` fallback. Run focused handbook regression.
Run the actual `[FRONTEND_CHECK: ...]` line from affected tests: `just viewer install`, `just viewer lint`,
`just viewer check`, `just viewer test`, `just viewer pack`, `just viewer build`. Use the declared generator for
committed static assets, then `uv run devkit generated check viewer-assets`; inspect packed library and Python
wheel contents and exercise a host importing the public exports with generic RepositoryDataSource fixtures.
No generated output is hand-edited. No release refresh, publishing, or downstream consumer write is in scope.
