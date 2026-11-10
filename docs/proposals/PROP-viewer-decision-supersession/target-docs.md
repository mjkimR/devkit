---
id: PROP-viewer-decision-supersession-target
title: Viewer decision supersession target documents
summary: "Blueprint for the viewer supersession contract, a decision-reading use case, the retained screen and summary panel, and their object register rows."
status: draft
proposal: PROP-viewer-decision-supersession
---

# [PROP-viewer-decision-supersession-target] Viewer decision supersession target documents

## Living Spec targets

- Modify `CAP-VIEW-repository-viewer`: add bidirectional ADR relation derivation, statement semantics, proposed PADR
  distinction, Read/Files scan triggers, loading/incomplete states, safe rendering and navigation. Add the use case
  backlink. Preserve server/library interface and handbook budgets.
- Create UC-read-decision-supersession under `docs/usecases/viewer/`: the flow below, linked to
  `CAP-VIEW-repository-viewer`, with Given/When/Then examples for outgoing/incoming whole/partial, aliases and
  unavailable targets, missing statement, PADR source, partial reads, reload and source switches.
- Create UX-view-decision and UX-decision-supersession under `docs/ux/viewer/` from the Screens drafts below.
- Create `docs/steering/ux-objects.md` with the rows below. No visual style system is introduced.
- Promote `PADR-viewer-indexed-decision-supersession` through handoff; no accepted ADR is superseded.

## Use case draft: UC-read-decision-supersession

**Goal:** Judge which clauses of a decision remain in force and open a related decision when needed.
**Actor:** A developer reading a repository. **Precondition:** a repository is selected in the viewer.

1. The reader opens an ADR in Read or rendered Files, or a PADR in Files or its proposal bundle.
   Screen: UX-view-decision. Capability: `CAP-VIEW-repository-viewer`.
2. The viewer displays the decision title, identity, source context and body without waiting for relation loading.
   Screen: UX-view-decision. Capability: `CAP-VIEW-repository-viewer`.
3. The reader inspects the relation summary: both applied ADR directions, or outgoing proposed PADR replacements.
   Screen: UX-view-decision and panel UX-decision-supersession. Capability: `CAP-VIEW-repository-viewer`.
4. The reader follows a resolved related decision; Read and Files retain their view, while a PADR in proposal
   detail opens the checkout target ADR in Files within the same viewer. The viewer updates its
   title/body/summary. Screen: UX-view-decision and panel UX-decision-supersession.
   Capability: `CAP-VIEW-repository-viewer`.
5. The reader finishes after seeing the replacement scope or source uncertainty.
   Screen: UX-view-decision. Capability: `CAP-VIEW-repository-viewer`.

Extensions:

- **3a**: While relations load, show loading text and keep the body available. If any indexed document fails, show
  `Incomplete`, the failed paths and the relations found; `Reload relations` repeats step 3 using the exact
  displayed subject version and refreshed related documents. Opening or reloading the subject updates body and
  relation input together, even within a cached index TTL.
  Screen: UX-view-decision and panel UX-decision-supersession.
- **3b**: If a target is missing or ambiguous, display its written ID without a link. If its statement is absent,
  show `Replacement scope not recorded`. The reader can continue reading and finish at step 5.
  Screen: UX-view-decision and panel UX-decision-supersession.
- **4a**: On a source/branch switch, cancel the former request and open the new source's document context; no old
  relation result is published. Screen: UX-view-decision.

**Postcondition:** the repository is unchanged; the reader sees only relations supported by the available source.

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

## Retained and rejected candidates

Retain the inline summary. A dedicated relations sidebar would occupy the same secondary region as existing
navigation and require a selection to inspect replacement text. This draft leaves visual styling to the existing
viewer and does not redesign the outer screens. The optional UX review is offered before implementation.
