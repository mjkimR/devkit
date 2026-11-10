---
id: PROP-viewer-decision-supersession
title: Show decision supersession in the Living Spec viewer
summary: "Show on a decision's viewer page which earlier ADRs it supersedes and which later ADRs supersede it, with the replaced scope from the partial-supersession statements, so a reader sees a partly replaced decision's state without running a command."
status: accepted
created_at: 2026-11-10
target_area: capabilities/viewer/
namespace: global
priority: low
size: M
planning_effort: medium
dev_effort: medium
depends_on: [SPEC-partial-adr-supersession-statements]
boundaries:
  owns:
    - packages/devkit-viewer/
    - docs/capabilities/viewer/CAP-VIEW-repository-viewer.md
    - docs/usecases/
    - docs/ux/
    - docs/steering/
  excludes:
    - packages/devkit-spec/
    - docs/decisions/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-viewer-decision-supersession] Show decision supersession in the Living Spec viewer

## 1. Background & Hypothesis

`SPEC-partial-adr-supersession-statements` makes the replaced scope of a partial supersession a fixed statement in the
later ADR and adds `devkit docs supersession` for agents. Its Planning left the viewer out: the viewer change is a
separate package, capability and verification chain (its retained `materials/planning-evidence.md` section 6).

The viewer's decision page shows `id`, `status`, `priority`, `milestone`, `target_area` and the title. It shows no
`supersedes`, and it has no list of the documents that reference the page. A reader of a partly replaced ADR sees the
"Superseded in part by" lines in its body and has to open each later ADR to see the rest.

### Hypothesis

A decision page that lists both directions (the earlier ADRs this decision supersedes, and the later ADRs that
supersede it, each with `whole` or `partial` and the statement text) lets a reader judge a decision's state on one
page.

## 2. Planning Decisions

Evidence is pinned to `7ed35b755138e9460e1de6f42d10b390886f448b`; see
[planning evidence](materials/planning-evidence.md). `SPEC-partial-adr-supersession-statements` is completed on that
head. Planning uses `medium` effort, with a scout and a challenger; Development remains `medium`.

### Data and compatibility

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

### UX candidates

| Candidate | Benefit | Cost | Recommendation |
| --- | --- | --- | --- |
| Inline summary below the decision header | Both directions and replaced scope are visible with the decision body | Long relation lists add vertical space | Recommended; follows the reader's current document |
| Dedicated relations sidebar with a selected-detail pane | Keeps body height stable for large histories | Competes with existing navigation and requires selection to see text | Reject for this bounded decision-reading task |

The retained candidate and the contrasting candidate go to `plan-accept`; no user preference is fabricated.
Screens are drafted in `target-docs.md` before code. The optional UX reviewer is offered by the Host.
`PADR-viewer-indexed-decision-supersession` records the data-source and placement choice.

## 3. Proposed Design & Impact

### Development scope

- Frontend pure relation parser/index, a shared summary component, Read/Files/PADR integration and focused Vitest
  fixtures under `packages/devkit-viewer/frontend/`; generated app assets under
  `packages/devkit-viewer/src/devkit_viewer/static/`.
- Update `CAP-VIEW-repository-viewer` with data-source, scope, loading/error, navigation and source-isolation
  contracts. Its `usecases` gains the narrow decision-reading use case.
- Create UC-read-decision-supersession at `docs/usecases/viewer/UC-read-decision-supersession.md`,
  UX-view-decision at `docs/ux/viewer/UX-view-decision.md`, and UX-decision-supersession at
  `docs/ux/viewer/UX-decision-supersession.md`. Add only their object rows to
  `docs/steering/ux-objects.md`, creating that register. The boundary declarations use existing parent directories;
  only these exact new documents are intended within those directories.
- Promote the PADR through normal handoff. No existing ADR decision is replaced.

### Acceptance checks for the Development spec

1. **AC-1**: Given ADRs with outgoing, incoming, whole and partial relations, when either Read or rendered Files
   opens one, then both groups show deterministic ID/title/status/scope/text and same-view links.
2. **AC-2**: Given canonical IDs, aliases, unresolved and ambiguous identities, when deriving edges, then aliases
   resolve, unresolved written IDs remain visible without links, and ambiguity never selects an arbitrary target.
3. **AC-3**: Given visible multiline/list statements and hidden examples, when parsing, then the statement text and
   whole/partial classification match the delivered query fixtures; missing text remains explicit. Include fences,
   indented code, comments, strikethrough, inline-code examples, CRLF and adjacent heading/list boundaries.
4. **AC-4**: Given a PADR from checkout or a Planning bundle, when viewed, then only outgoing proposed replacement
   is shown with source context; a proposal-detail link opens the checkout ADR in Files, and no PADR becomes an
   applied incoming ADR superseder.
5. **AC-5**: Given pending, partial or failed indexing, when a decision body renders, then the body remains usable
   and relation loading/incompleteness is explicit; reload retries, and changed sources cannot receive stale results.
   A saved subject edit opened within the index TTL uses its displayed metadata/statement. Reloading relations
   keeps the subject version aligned with the visible body.
6. **AC-6**: Given raw mode, an ordinary file or handbook-only navigation, when viewed, then this feature starts no
   document scan; Read reuses its index and Files scans only for a rendered decision.
7. **AC-7**: Given hostile title or statement markup, when rendered, then metadata and replacement text remain
   escaped; existing sanitized Markdown behavior and all package/library interfaces remain compatible.
8. **AC-8**: Given the retained Screens draft, when Development completes, then its UX documents, step citations,
   object register and capability links are reflected and pass document rules; generated viewer assets are current.

### Verification

- Pure relation/parser fixtures and shared-component behavior tests; Read and Files integration tests cover both
  directions, cross-namespace navigation, source/branch changes, incomplete/reload states and raw/handbook budgets.
- Require `just viewer lint`, `just viewer check`, `just viewer test` and `just viewer build`. Build the committed
  static assets and check `uv run devkit generated check viewer-assets` with the required Node runtime.
- Run `just test-affected --base <development-start>` with its full fallback and named FRONTEND_CHECK commands,
  plus required rules/lint/types. No backend production change is planned. No speed claim requires a benchmark;
  request-count fixtures establish the stated scan trigger and reuse behavior.

### Non-Goals

- New server endpoints, Python dependencies, package/feature edges, or public source-interface fields.
- A general reference graph, transitive supersession, governance validation, document repair or approval actions.
- Incoming proposed PADR impact previews, arbitrary other-branch ADR reads or combining several Planning sources.
- Rebuilding the viewer navigation, styling system, or unrelated document hygiene/splitting.

### Unverified areas

Browser/parser parity is source-inspected, not executed yet. Development must supply fixtures for the delivered
Python query behavior and the intentional PADR display distinction. No host-wide API survey or performance
measurement was made. UX reviewer scoring is recorded separately from the mandatory challenger findings.

## 4. Lifecycle & Retirement Criteria

`SPEC-partial-adr-supersession-statements` is delivered; Planning can proceed. On acceptance, hand off through the
normal proposal lifecycle at the retained `medium` Development effort. No source decisions or records are edited
by this Planning turn. No separate deferred feature is required by the accepted scope.
