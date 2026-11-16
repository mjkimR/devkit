---
id: PROP-formal-document-coverage
title: Formal document coverage across capability areas
summary: "Adds one DESIGN, one DOMAIN and four OPS documents, written from the current code and Living Spec, for the delivery, host, mcp, distribution and search reader questions no existing owner answers, in three parallel Development units."
status: accepted                     # draft | reviewing | accepted | rejected
created_at: 2026-11-16
target_area: documents/
priority: medium                      # critical | high | medium | low
size: M                               # S | M | L | XL (XL: would need two or more specs or task kinds; decompose before Planning)
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - docs/designs/
    - docs/domain/distribution/
    - docs/operations/
    - docs/proposals/PROP-formal-document-coverage/
  excludes:
    - packages/
    - docs/capabilities/
    - docs/architecture/
    - docs/decisions/
    - docs/development/
    - docs/steering/
    - docs/domain/delivery/
    - docs/designs/distribution/
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
---

# [PROP-formal-document-coverage] Formal document coverage across capability areas

## 1. Background & Hypothesis

The formal kinds (DESIGN, DOMAIN, OPS), their area-scoped paths (`ADR-area-scoped-design-bundles`) and their
templates and writing instructions (`ADR-problem-first-formal-document-openings`) are delivered. Five formal
documents exist, all in the distribution and delivery areas: `DESIGN-distribution-file-directory-replacement`,
`DESIGN-distribution-transactions`, `DOMAIN-bundle-selection-and-installation`, `DOMAIN-delivery-relationships` and
`OPS-distribution-sync`. The Living Spec has 18 capability areas under `docs/capabilities/`; the other areas have no
implementation explanation, conceptual model or operations routing beyond capabilities, architecture and reference.

`CAP-DOCS-documentation-ownership` §3.3 asks for one reader question per formal document and to drop a document that
has none, so coverage is not one document per kind per area.

Hypothesis: an inventory of reader questions per area, answered from the current code and Living Spec, yields a
bounded set of formal documents that agents and maintainers use instead of reading source to recover mechanisms,
concept distinctions and symptom routing.

## 2. Technical Spike Questions

- **Q1**: Which areas have a reader question that only a DESIGN (local mechanism), DOMAIN (concepts readers
  confuse) or OPS (symptom → owner routing) document answers, and which existing owner already answers the rest?
- **Q2**: How should the work split into Development units (by area group, disjoint `docs/` paths) so workers run in
  parallel, and is any unit XL?

## 3. Proposed Design & Impact

Documentation only. Each new document follows its kind's delivered template and writing instruction
(`design-writing`, `domain-writing`, `operations-writing`), states its authority boundary by full ID and moves no
normative statement out of its current owner (`CAP-DOCS-documentation-ownership` §3.1). No code, capability,
architecture, reference or ADR changes; a gap found in those is recorded as feedback.

### 3.1 Inventory (answers Q1)

IDs of documents this proposal creates are written without code spans until they exist.
Four parallel scouts covered all 18 capability areas plus architecture, reference and source; one challenger round
tested the result. Six documents survive; the other 13 areas have no reader question an existing owner leaves open.
The full table, sources, owners not to duplicate, writing conditions and the dropped list (with each owner) are in
[the inventory](materials/inventory.md).

| ID | Kind | Unit | One reader question (short) |
| --- | --- | --- | --- |
| DESIGN-workflow-stage-evaluation | DESIGN, `docs/designs/delivery/` | A | In what order does `devkit workflow next` evaluate one sample Unit, and why does it report only the first unmet stage? |
| OPS-assignment-attention-routing | OPS | A | Which evidence and owner fit an adaptive assignment `list` attention value? |
| OPS-host-hook-dispatch-routing | OPS | B | A configured host hook shows no warning and no observation: which evidence selects the owner? |
| OPS-mcp-runtime-refusals | OPS | B | Some MCP tools run while others refuse, or a registration is inactive: which surface's evidence selects the owner? |
| DOMAIN-override-lifecycle | DOMAIN, `docs/domain/distribution/` | C | Which capability state is a project override in, how does it differ from `ORPHAN_LEFT`, and what changes it? |
| OPS-search-mode-and-model-routing | OPS | C | Search ran lexical-only or failed with a `SEARCH_*` model error: which evidence selects the owner? |

### 3.2 Development split (answers Q2)

One spec (`sdd-spec-feature`, size M, not XL: one task kind and one contract kind). Three units with disjoint paths
run as parallel workers inside that spec's Development; each unit is one task group whose `_Boundary:_` is its files.

| Unit | Areas | `_Boundary:_` (paths to create) |
| --- | --- | --- |
| A | delivery | `docs/designs/delivery/DESIGN-workflow-stage-evaluation/design.md`, `docs/operations/OPS-assignment-attention-routing.md` |
| B | host, mcp | `docs/operations/OPS-host-hook-dispatch-routing.md`, `docs/operations/OPS-mcp-runtime-refusals.md` |
| C | distribution, search | `docs/domain/distribution/DOMAIN-override-lifecycle.md`, `docs/operations/OPS-search-mode-and-model-routing.md` |

A unit's `related_*` fields name only IDs that already exist or that the same unit writes; cross-unit links are
optional and are added only after the units are integrated.

### 3.3 Planning decisions

- DESIGN-envelope-return-timestamp-ordering is dropped: `CAP-DLV-human-interaction` §5 already states timestamp
  precision and same-second voiding; its example becomes one step of DESIGN-workflow-stage-evaluation.
- DESIGN-workflow-stage-evaluation is kept while a DOMAIN comparison of gate sources is dropped: the DOMAIN would
  restate the list in `CAP-DLV-human-interaction` §5, whereas no owner shows the evaluation order on a concrete Unit,
  which is the design worked-example role in `CAP-DOCS-documentation-ownership` §3.1.
- OPS-host-hook-dispatch-routing and OPS-mcp-runtime-refusals stay separate: different symptoms and capability
  owners (`CAP-HOST-lifecycle-observation`, `CAP-MCP-runtime-registration`).
- OPS-search-mode-and-model-routing is written only with its explicit `--mode hybrid` evidence row; without it the
  document is dropped and the drop is reported.
- No PADR: no decision meets the `decision-writing` admission criteria; these are inclusion choices within the
  approved intent.

### 3.4 Design, domain and operations impact

The change adds one design, one domain and four operations documents as listed; it edits no existing formal document.
`DOMAIN-delivery-relationships`, `DOMAIN-bundle-selection-and-installation`, `OPS-distribution-sync` and both
distribution designs are unaffected: no new document changes their statements, and links to them are optional
`related_*` entries. Each statement in a new document keeps its existing owner named by full ID.

### 3.5 Acceptance criteria

- **AC-1**: Each of the six documents exists at its §3.2 path with its kind's delivered template structure: a
  problem-first lead paragraph without a question section, the kind's required section (`## Relationship overview`
  table for DOMAIN, `## Routing` and `## Normal-state observation` for OPS), `## Authority boundary` and
  `## Maintenance and next action`, and no template HTML comment.
- **AC-2**: Each document answers the one reader question its inventory row names, and its authority boundary names by
  full ID every owner that inventory row lists as "must not duplicate".
- **AC-3**: No document contains an RFC 2119 keyword as its own rule, copies recovery steps or advisory FIX/ACTION
  text, or defines a glossary term; every rule it relies on is cited by full ID and section.
- **AC-4**: Each document satisfies its inventory writing condition: DESIGN-workflow-stage-evaluation is a worked
  example on one sample Unit; OPS-assignment-attention-routing prescribes no action choice;
  OPS-host-hook-dispatch-routing has one trust/PATH row with evidence "devkit reports `unknown`";
  OPS-mcp-runtime-refusals has only cross-surface rows naming owners by code row or ID; DOMAIN-override-lifecycle
  uses only the capability's states and codes and distinguishes `ORPHAN_LEFT`; OPS-search-mode-and-model-routing
  has the explicit-mode row or is dropped with the drop reported.
- **AC-5**: Every factual claim about behavior (state, code, field, order) is checked against the current source or
  capability at the Development head, and every cited source path exists.
- **AC-6**: `uv run devkit rules check` passes on each new document, `git diff --check` is clean, and no file outside
  the §3.2 boundaries changes except spec records and feedback.

## 4. Lifecycle & Retirement Criteria

Retired when the accepted inventory's documents are delivered by the handed-off spec units.
