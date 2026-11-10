---
id: SPEC-viewer-decision-supersession
title: Show decision supersession in the Living Spec viewer
summary: "Display both ADR replacement directions and exact replacement scope in Read and Files, with proposed PADR replacements and explicit incomplete-source states."
status: in-progress
created: 2026-11-10
namespace: global
depends_on: [SPEC-partial-adr-supersession-statements]
related_capabilities: [CAP-VIEW-repository-viewer]
related_usecases: [UC-read-decision-supersession]
workflow: sdd-spec-feature
---

# [SPEC-viewer-decision-supersession] Show decision supersession in the Living Spec viewer

## 1. Problem Statement & Motivation

Decision readers need both replacement directions and the replaced clauses beside the decision they are reading.
`ADR-viewer-indexed-decision-supersession` selects browser derivation and an inline summary. The delivered
`SPEC-partial-adr-supersession-statements` defines source statement semantics. Planning evidence is retained under
`docs/materials/2026-11/20261110-viewer-decision-supersession/`.

## 2. User Stories

- **US-1**: As a repository reader, I can inspect an ADR's replacement state in Read or Files and follow a related decision.
- **US-2**: As a proposal reader, I can distinguish proposed PADR replacement from applied ADR decisions.

## 3. Non-Goals

- **Scope Excluded**: server endpoints, Python dependencies, public repository source-interface changes or feature edges.
- **Scope Excluded**: general reference graphs, transitive replacement, governance validation, document repairs or approvals.
- **Scope Excluded**: incoming PADR impact previews, unrelated navigation redesign or document hygiene.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Both ADR directions

- **Given** ADRs with outgoing/incoming whole and partial relations.
- **When** Read or rendered Files displays a decision.
- **Then** both groups show ID, title, status, scope and replacement text in deterministic ID order with same-view links.

### [AC-02] Canonical and unavailable identities

- **Given** canonical IDs, aliases, missing targets and ambiguous identities.
- **When** relations are derived.
- **Then** aliases resolve; unresolved written IDs remain visible without links; ambiguous identities never choose arbitrary targets.

### [AC-03] Source statement parity

- **Given** visible multiline/list statements and hidden Markdown examples.
- **When** replacement text is parsed.
- **Then** results match the delivered query fixtures for fences, indented code, comments, strikethrough, inline code, CRLF and item/heading boundaries; missing text says Replacement scope not recorded.

### [AC-04] Proposed PADR source

- **Given** a PADR from checkout or its Planning bundle.
- **When** its decision is rendered.
- **Then** only outgoing proposed replacements appear with actual source context; proposal-detail target links open checkout ADRs in Files; PADRs never become applied incoming superseders.

### [AC-05] Independent loading and freshness

- **Given** pending/failed indexing or a saved subject opened inside the index TTL.
- **When** the body renders or relations reload.
- **Then** the body stays usable; partial reads are labelled Incomplete with failed paths and retry; aborted/source-switched loads cannot publish; relations use the exact displayed subject version.

### [AC-06] Read budgets

- **Given** raw mode, an ordinary file, handbook-only navigation or a rendered decision.
- **When** the view opens.
- **Then** this feature starts indexing only for rendered decisions; Read reuses its existing index and Files indexes lazily.

### [AC-07] Safe content

- **Given** hostile titles, metadata and replacement markup.
- **When** the summary renders.
- **Then** all supplied text remains escaped and no injected HTML executes; sanitized document rendering and library interfaces remain compatible.

### [AC-08] Retained UX and artifacts

- **Given** the approved Screens drafts and completed implementation.
- **When** Development completes.
- **Then** the capability, one decision-reading use case, two UX documents and object register reflect the behavior; generated viewer assets are current.

## 5. Detailed Contract


- Derive relations in the browser from the existing document index. Add no server endpoint, Python dependency,
  `RepositoryDataSource` method or cross-feature edge. `ADR-repository-viewer` already selects browser parsing.
- Read canonical decision IDs and aliases. Ambiguous IDs or aliases are unavailable targets, never arbitrary links.
  Keep this relation lookup separate from generic prose-reference linking.
- Outgoing edges come only from the subject's `supersedes` string or string-list entries. Incoming edges come only
  from ADR documents whose canonicalized `supersedes` names the subject. A reciprocal body pointer alone creates
  no edge. Sort each direction by canonical ID, then written ID/path for ties.
- A relation is `whole` only when the earlier decision has `status: superseded` and its `superseded_by` resolves to
  this later ADR. Otherwise its scope is `partial`, including unresolved outgoing targets, matching the delivered
  query. Preserve the related decision's actual status and show unresolved targets without a navigation link.
- Extract the later document's first matching visible `Supersedes in part` statement, not the earlier pointer.
  Require the colon; stop at a blank line, another list item, heading or hidden block. Exclude examples in fenced
  or indented code, HTML comments and struck-out or code-span prose. Preserve source inline markup as escaped text;
  neither statement text nor metadata is inserted as HTML. No missing statement is invented from the title.
- A relation without statement text says `Replacement scope not recorded`. A whole relation still says `whole`
  when its historical ADR has no statement. The viewer reports source facts; it does not enforce the governance
  rule, repair documents or declare the source valid.

### Surfaces and scope

- Use one shared supersession summary below the decision header and above the Markdown body in the Read book and
  rendered Files decision view. Raw mode remains the original source. Neither an extra tab nor a permanently
  occupied side panel is needed for a secondary fact of the document being read.
- Read reuses its complete source/branch document index, before namespace or view filters. Files requests that
  index lazily only after opening a rendered ADR or PADR. For every surface, replace the same-path subject entry
  in the relation input with the exact document currently displayed, including its raw metadata and statement.
  Relation reload retains that displayed subject and refreshes only the other indexed documents; opening/reloading
  the subject itself updates its body and relation input together. Related-document freshness follows the index
  cache policy. An ordinary file, raw view, dashboard or handbook alone
  does not trigger this feature's scan. Existing cache expiry and abort/generation guards apply; loading relations
  never blocks the selected document body. A `Reload relations` action invalidates and reloads the source index.
- On ADR pages the groups are `Supersedes` and `Superseded by`. Show both directions with ID, title when resolved,
  source status, whole/partial scope and replacement text. An empty completed direction says `None recorded`.
- On PADR pages show outgoing relations under `Proposed supersession`, with the existing Planning source badge
  when applicable. Resolve outgoing targets against the checkout index while taking the PADR body from its actual
  bundle source. PADRs never appear as applied incoming superseders on an ADR page. Do not add PADR reverse lists.
- A scan with read failures retains successful relations but labels the summary `Incomplete`; an empty incoming
  list then says `No incoming relations found in the documents read`, not `None recorded`. Keep failed paths
  visible and offer `Reload relations`. Source/branch switches and aborted loads cannot publish old results.
- A resolved relation link opens the target document in the same viewer: Read scrolls to the target chapter,
  clearing a namespace filter when needed; Files loads the target path. A PADR link from proposal detail opens
  the checkout target ADR in Files within the same viewer, never inside the proposal bundle or from its Planning
  source. No link is offered for an unresolved or
  ambiguous target. Keyboard users use ordinary focusable links and buttons.


## 6. Assumptions

- Retain the approved inline summary rather than a dedicated sidebar; existing navigation keeps its space.
- Planning UX rounds 1 and 2 were completed before code; the final round closed all findings. Screens below retain that result, so another UX round is unnecessary.
- Related documents follow the existing index cache policy; the displayed subject overrides its cached copy.
- No new dependency or feature edge is required.

## Screens


New IDs below are planned and therefore plain text until spec-sync creates them.

### UX-view-decision — Decision reading view

- **Area:** viewer. **Element:** screen. **Use case:** UC-read-decision-supersession.
  **Capability:** `CAP-VIEW-repository-viewer`.

#### 1. Purpose

- **Primary task:** Read a decision and judge its remaining scope.
- **Facts to commit:** decision identity/title/status, the checked-out branch or Planning source context, the
  replaced clauses and any uncertainty from source reads.
- **Secondary items:** relations sit below the decision header; the existing navigation stays beside the body.
  Source/raw controls remain with the document header. This draft covers the decision-reading slice of Read,
  Files and proposal detail, not the other tasks of those host screens.

#### 2. Content

The decision body remains the primary reading region. UX-decision-supersession is a secondary panel between the
header and body, so it is discoverable before the reader relies on old clauses. Existing host navigation and theme
controls retain their placement.

- Decision (header: ID, title, actual status and source context).
- Supersession relations (panel UX-decision-supersession, shown for rendered ADR/PADR documents).
- Decision (body: sanitized Markdown; raw source instead when raw mode is selected).
- Repository navigation (existing tree/book/proposal controls).

#### 3. States

- **loading:** selected body load follows the existing view; relation loading has its own panel state. The reader
  can navigate away.
- **populated:** the decision body and relation panel are available; the reader may follow a relation or finish.
- **error:** a document-read error retains existing navigation so another document can be opened.
- **raw:** original source is displayed without the summary; switch to rendered mode to inspect relations.

#### 4. Interactions

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Open a decision from existing navigation | UC-read-decision-supersession 1 | populated, loading, error, raw | loading | UX-view-decision | `CAP-VIEW-repository-viewer` | Selected decision title and body replace the prior one |
| Select rendered mode | UC-read-decision-supersession 3 | raw | populated | | `CAP-VIEW-repository-viewer` | Relation loading or summary appears |
| Select raw mode where the host offers it | global: inspect the document source | populated | raw | | `CAP-VIEW-repository-viewer` | Original document source replaces the rendered body |
| Choose another repository or branch | UC-read-decision-supersession 4a | populated | loading | UX-view-decision | `CAP-VIEW-repository-viewer` | Previous context clears; selected source loads |
| Finish reading | UC-read-decision-supersession 5 | populated | populated | end | `CAP-VIEW-repository-viewer` | No repository change; decision remains readable |

### UX-decision-supersession — Decision supersession summary

- **Area:** viewer. **Element:** panel. **Use case:** UC-read-decision-supersession.
  **Capability:** `CAP-VIEW-repository-viewer`.

#### 1. Purpose

- **Primary task:** Inspect replacement relations and their scope without leaving the current decision.
- **Facts to commit:** relation direction, target ID/title/status, whole/partial scope, literal replaced-scope text
  and whether available documents establish a complete list.
- **Secondary items:** a reload action and failed paths follow the relation groups.

#### 2. Content

Both directions remain visible in document order rather than a hidden tab. Each group lists its related decisions
in deterministic ID order. Text wraps to the available width; no separate geometry or visual token is prescribed.

- Supersession relations (section heading and loading/incomplete context).
  - `Supersedes` group (ADR only) or `Proposed supersession` group (PADR only).
    - Related decision (written/canonical ID, title and status when resolved; target link only when unambiguous; proposal-detail PADR links open the checkout ADR in Files).
    - Replacement scope (`whole` or `partial`; PADR group additionally says proposed).
    - Replacement text (escaped source text, or `Replacement scope not recorded`).
  - `Superseded by` group (ADR only, later ADRs only; same row facts).
  - Source failures (paths, only when scan errors exist).
  - `Reload relations` action.

A completed empty direction says `None recorded`. An incomplete empty incoming direction says
`No incoming relations found in the documents read`. This is source evidence, not a declaration that a partly
superseded ADR is wholly invalid. An unresolved or ambiguous ID has no link and says why it is unavailable.

#### 3. States

- **loading:** `Loading supersession relations…`; body remains available and navigation can cancel the request.
- **populated:** at least one relation is present; follow a resolved link or keep reading.
- **empty:** completed scan found no relations; `None recorded` and reload remain available.
- **incomplete:** successful relations plus `Incomplete`, failed paths and reload; no claim of an empty complete
  reverse list.
- **error:** no usable index result; show failure details and reload, while retaining the decision body.

#### 4. Interactions

| Trigger | Step | From | To | Target | Capability | Feedback |
| --- | --- | --- | --- | --- | --- | --- |
| Follow an unambiguous resolved decision link | UC-read-decision-supersession 4 | populated, incomplete | loading | UX-view-decision | `CAP-VIEW-repository-viewer` | Target title/body/summary appears; Read reveals its namespace, Files keeps its view, proposal-detail PADR opens checkout ADR in Files |
| Reload relations | UC-read-decision-supersession 3a | populated, empty, incomplete, error | loading | | `CAP-VIEW-repository-viewer` | Source index reloads and replaces summary or shows failure |
| Continue reading after an unavailable target | UC-read-decision-supersession 3b | populated, incomplete | populated, incomplete | | `CAP-VIEW-repository-viewer` | Written ID and missing-scope text remain visible without a broken control |

## Object register draft

`docs/steering/ux-objects.md` is created at spec-sync. Rows name existing document concepts; no new generic domain
term or glossary rename is required.

| Object | Role | Representations | Calls to action |
| --- | --- | --- | --- |
| Decision (ADR) | Developer reading repository | Header, Markdown body, raw source, related decision link | Open decision, view raw, follow related decision |
| Proposed decision (PADR) | Developer reading proposal | Source-labelled header, proposed supersession rows, Markdown body | Open proposal decision, follow target ADR |
| Supersession relation | Developer reading decision | Direction, related ID/title/status, whole/partial scope, replacement text, unavailable target | Follow related decision, reload relations |

