---
id: SPEC-formal-document-coverage
title: Formal document coverage across capability areas
summary: Adds one DESIGN, one DOMAIN and four OPS documents, written from the current code and Living Spec, for the delivery, host, mcp, distribution and search reader questions no existing owner answers, in three parallel Development units.
status: planned
created: 2026-11-16
related_capabilities: []
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-formal-document-coverage] Formal document coverage across capability areas

## 1. Problem Statement & Motivation

Handed off from proposal PROP-formal-document-coverage on 2026-11-16.
- **Preserved Materials**: `docs/materials/2026-11/20261116-formal-document-coverage`

The formal kinds (DESIGN, DOMAIN, OPS), their area-scoped paths (`ADR-area-scoped-design-bundles`) and their
templates and writing instructions (`ADR-problem-first-formal-document-openings`) are delivered. Five formal
documents exist, all in the distribution and delivery areas: `DESIGN-distribution-file-directory-replacement`,
`DESIGN-distribution-transactions`, `DOMAIN-bundle-selection-and-installation`, `DOMAIN-delivery-relationships` and
`OPS-distribution-sync`. The other capability areas have no implementation explanation, conceptual model or
operations routing beyond capabilities, architecture and reference.

`CAP-DOCS-documentation-ownership` §3.3 asks for one reader question per formal document and to drop a document that
has none. The accepted Planning inventory
([inventory](../../../docs/materials/2026-11/20261116-formal-document-coverage/inventory.md)) found six reader
questions no existing owner answers (IDs are plain text until the documents exist); the other areas are answered by their listed owners.

| ID | Kind and path | Unit | One reader question (short) |
| --- | --- | --- | --- |
| DESIGN-workflow-stage-evaluation | DESIGN, `docs/designs/delivery/` | A | In what order does `devkit workflow next` evaluate one sample Unit, and why does it report only the first unmet stage? |
| OPS-assignment-attention-routing | OPS, `docs/operations/` | A | Which evidence and owner fit an adaptive assignment `list` attention value? |
| OPS-host-hook-dispatch-routing | OPS, `docs/operations/` | B | A configured host hook shows no warning and no observation: which evidence selects the owner? |
| OPS-mcp-runtime-refusals | OPS, `docs/operations/` | B | Some MCP tools run while others refuse, or a registration is inactive: which surface's evidence selects the owner? |
| DOMAIN-override-lifecycle | DOMAIN, `docs/domain/distribution/` | C | Which capability state is a project override in, how does it differ from `ORPHAN_LEFT`, and what changes it? |
| OPS-search-mode-and-model-routing | OPS, `docs/operations/` | C | Search ran lexical-only or failed with a `SEARCH_*` model error: which evidence selects the owner? |

## 2. User Stories

- **US-1**: As an agent or maintainer, I want a formal document for each of these reader questions so that I recover
  a mechanism, a concept distinction or a symptom's owner without reading source.

## 3. Non-Goals

1. **Scope Excluded**: no code, capability, architecture, reference, steering or ADR change, and no edit of an existing
   formal document's statements; a gap found in an owner is recorded as feedback.
2. **Scope Excluded**: no formal document for a dropped inventory candidate, and no normative statement moved out of
   its current owner (`CAP-DOCS-documentation-ownership` §3.1).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] Template structure
- **Given** the six documents at their §1 paths
- **When** each is read against its kind's delivered template
- **Then** it has a problem-first lead paragraph without a question section, the kind's required section
  (`## Relationship overview` table for DOMAIN, `## Routing` and `## Normal-state observation` for OPS),
  `## Authority boundary` and `## Maintenance and next action`, and 0 template HTML comments

### [AC-02] One reader question and its owners
- **Given** the inventory row of a document
- **When** the document is read
- **Then** it answers that row's one reader question, and its authority boundary names by full ID every owner that
  row lists as "must not duplicate"

### [AC-03] No restated authority
- **Given** each document
- **When** it is searched for RFC 2119 keywords, recovery steps, advisory FIX/ACTION text and term definitions
- **Then** 0 RFC 2119 keywords are its own rule, 0 recovery steps or FIX/ACTION texts are copied, 0 glossary terms are
  defined, and every rule it relies on is cited by full ID and section

### [AC-04] Writing conditions
- **Given** the inventory writing conditions
- **When** each document is read
- **Then** DESIGN-workflow-stage-evaluation is a worked example on one sample Unit; OPS-assignment-attention-routing
  prescribes no action choice; OPS-host-hook-dispatch-routing has exactly 1 trust/PATH row with evidence "devkit
  reports `unknown`"; OPS-mcp-runtime-refusals has only cross-surface rows naming owners by code row or ID;
  DOMAIN-override-lifecycle uses only the capability's states and codes and distinguishes `ORPHAN_LEFT`;
  OPS-search-mode-and-model-routing has the explicit `--mode hybrid` row, or is absent with the drop reported

### [AC-05] Current facts
- **Given** the Development head
- **When** each behavior claim (state, code, field, order) is compared with the current source or capability
- **Then** every claim matches, and every cited source path exists

### [AC-06] Checks and boundary
- **Given** the final diff against the handoff commit
- **When** `uv run devkit rules check --ci --base main` and `git diff --check` run
- **Then** both exit 0, and no file outside the task boundaries changes except spec records and feedback

## 5. Assumptions

- The skeleton boundary `docs/proposals/PROP-formal-document-coverage/` no longer exists after acceptance; it is
  dropped from the boundaries.
- The three Planning units A, B and C run as one task group each inside this spec's single Development turn, drafted in
  parallel and committed by one worker, since their paths are disjoint.
- Cross-unit `related_*` links are optional; a link to an existing document outside the boundaries is added only as a
  link repair in `docs/designs/`, `docs/domain/distribution/` or `docs/operations/`.

## 6. Source feedback

- None carried from Planning; Planning recorded `FB-capabilities-readme-area-tree-incomplete` and
  `FB-search-module-layout-omits-layers` as owner gaps outside this scope.
