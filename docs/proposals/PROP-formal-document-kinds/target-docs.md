---
id: PROP-formal-document-kinds-target
title: Formal document kinds target blueprint
summary: "Plans formal-kind contracts, canonical document migration and complete source/interface support matrices for design, domain and operations."
status: draft
proposal: PROP-formal-document-kinds
targets:
  - file: docs/capabilities/documents/CAP-DOCS-document-model.md
  - file: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
  - file: docs/capabilities/documents/CAP-DOCS-document-lookup.md
  - file: docs/capabilities/documents/CAP-DOCS-document-search.md
  - file: docs/capabilities/documents/CAP-DOCS-namespaces.md
  - file: docs/usecases/documents/UC-find-the-right-documents.md
  - file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
  - file: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
  - file: docs/steering/glossary.md
  - file: docs/README.md
---

# [PROP-formal-document-kinds-target] Target Living Spec structure for formal document kinds

This blueprint plans future contracts and migration for `PROP-formal-document-kinds`. Current documents continue
to describe the retained implementation until Development reconciles them. Proposed new IDs below are plain text;
Planning confirms their spelling and paths before creating references to them.

## 1. System capabilities plan

| Current owner | Planned change | Boundary preserved |
| --- | --- | --- |
| `CAP-DOCS-document-model` | Register design/domain/operations identity, schema, aliases, references, namespace and serialization contracts | Existing kind values and public compatibility |
| `CAP-DOCS-documentation-ownership` | Replace ID-free role clauses with canonical formal kinds, per-kind metadata and detail/artifact policy | One authoritative statement owner, architectural and behavioral responsibility boundaries |
| `CAP-DOCS-document-lookup`, `CAP-DOCS-document-search`, `CAP-DOCS-namespaces` | Cover list/filter/search/pinning/resolve/refs for every kind and namespace | Existing selection, ordering and output/error contracts |
| `CAP-DIST-sync-and-transactions` | Repair domain/design ingress to migrated IDs and detail destinations | Selection, receipt, transaction, recovery and readiness guarantees |
| `CAP-DLV-proposal-lifecycle` | Repair domain ingress to formal identity | Approval, dependency, provenance and handoff authority |

The target list must expand to every actual canonical migration and owner before handoff; it is not an example cap.

## 2. Use cases and formal document migration

Planning identifies existing author/search/resolve/reference use cases and records the applicable three-kind
scenarios. New use cases are warranted only for distinct goals; existing scenarios must include formal-kind
selection and expected results. Viewer screens and user interactions are owned by `PROP-design-document-viewer`.

| Current canonical content/input | Planned canonical identity | Migration work |
| --- | --- | --- |
| docs/designs/distribution-transactions.md | DESIGN-distribution-transactions | Formal frontmatter/H1/path and ID ingress |
| docs/designs/distribution-transactions/file-directory-replacement.md | Formal detail identity determined in Planning | Choose independently maintained formal Markdown node or parent-owned supporting detail, define one canonical identity and repair source/detail links |
| docs/domain/delivery-relationships.md | DOMAIN-delivery-relationships | Formal schema and ID ingress from delivery/glossary |
| docs/domain/bundle-selection-and-installation.md | DOMAIN-bundle-selection-and-installation | Formal schema and distribution/glossary ingress |
| Archived unmerged docs/operations/distribution-sync.md | OPS-distribution-sync | Reuse the symptom composition as input; create current formal operations document with existing action authorities |
| Any additional canonical design/domain/operations document found at Planning | Kind-appropriate formal ID | Include all current global/registered namespace role documents in migration ledger |

Confirm DESIGN, DOMAIN and OPS prefixes and their path grammar in Planning. Define nested design detail naming
and identity coherently before migration. Independent canonical role documents must migrate; parent-owned support
files have documented purpose and links without pretending to be separate formal nodes. CSV, diagrams, images and
other artifacts do not need document IDs. Archived materials, completed specs and dated pilot evidence retain
historical representation and provenance. No duplicate live ID-free canonical route remains.

## 3. Architecture and decision impact

- Review `ARCH-05-2-components` and the document subsystem architecture for Kind ownership, existing CLI/adapters,
  feature dependency edges and package independence. Runtime behavior remains in the docs package's existing
  document/governance features. Planning declares new edges if actually needed.
- Follow `ARCH-08-1-agent-output`, `CAP-ADV-agent-advisory-protocol` and `CAP-CLI-agent-cli-toolkit` for public output.
  Document CLI kind choices/help, public Python symbols and JSON kind strings as compatibility surfaces.
- Create a new ADR that supersedes the ID-free design clauses of
  `ADR-documentation-ownership-and-linked-design-entries` and domain clauses of
  `ADR-linked-domain-relationship-views`. State retained responsibility/authority clauses and their current
  restatements. Do not rewrite historical decisions to conceal the direction change.
- Treat the archived operations decision/source as superseded-direction evidence. Its unmerged implementation
  is not current main. Existing recovery, journal compatibility and readiness contracts are unchanged.

## 4. Development conventions, governance and source interfaces

| Surface | Core planned ownership | Required result |
| --- | --- | --- |
| Kind enum/definition/coverage; ID parsing and Living Spec grammar | packages/devkit-docs document model and governance | Three registered kinds with explicit prefix/directory/schema/status/summary/relations and applicable entrypoints |
| Metadata and references | Document parser/model and reference rules | Alias identity, prose/structured refs, provenance and applicable supersession remain distinct |
| Index/list/search/pinning/resolve/refs | Existing docs repositories, browse/search use cases and CLI | Complete new-kind behavior in global and registered namespaces; public Python/JSON/CLI compatibility |
| ID, format, summary and entrypoint policy | Existing governance rules/use cases/tests | Positive/negative metadata/path/prefix/H1/alias/reference tests; appropriate per-kind applicability |
| Authoring assets | packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/ | Formal design/domain/operations templates and writing instructions, registered in bundle.toml/core; neutral guidance |
| Hierarchy/pointers | Source AGENTS.md, seed/docs/README.md, repo docs/README.md, architecture-writing and living-spec-writing | Formal role homes and read/write routing agree; remove current ID-free denial of index standing |
| Distribution | Docs integration inventories and installed-consumer E2E | Shipped template-directory asset and instruction inventory agree; sync/get-context visibility, docs-only wheel without spec |
| SDD/adaptive lifecycle | Required dependent lifecycle proposal | spec-plan/spec-sync/spec-entrypoints, proposal scaffold, adoption and adaptive documenter integrate formal impact targets |
| Viewer/public frontend/static/handbook | Required dependent viewer proposal | Groups, IDs/deep links, prose refs, metadata/graph, artifacts, namespaces and packaged assets; deliberate handbook inclusion policy |

No document MCP server is currently published by `devkit-docs`. Verify existing published surfaces; do not create
one merely to fill an assumed interface row. Required runtime or CLI changes are authorized Planning scope,
not automatically excluded. A required cross-package extension must name its boundary/owner and dependency.

## 5. System before and after

| Dimension | Before | Required after |
| --- | --- | --- |
| Identity | Maintained design/domain entries are ID-free; operations exists only in halted worktree | All canonical role documents have formal identity and applicable schema |
| Discovery | Indexed owners link to role files; role nodes absent from search/resolve/refs | All three kinds participate directly in index/list/search/pin/resolve/refs and namespaces |
| Governance | Existing explicit Living Spec grammar omits these kinds | Every applicable identity/format/summary/reference/entrypoint rule supports them |
| Authoring | Optional ID-free design template and role text | Registered per-kind formal templates/instructions, seed/pointers and shipped consumer evidence |
| Maintenance | Owner-led link review with historical ID-free pilot evidence | Formal migration and complete SDD/adaptive create/update/split/rename/retire integration |
| Viewer | Generic reading plus hardcoded prefix/group/related-field lists | Full formal-kind navigation, IDs, references, metadata, artifacts and shipped static parity |
| Handbook | Limited recognized prefixes can silently exclude a source | Recognized formal identities/source lookup and explicit inclusion policy |

## 6. Required acceptance matrices

Planning produces a row for each of design, domain and operations across every surface in §4, including public
Python/JSON compatibility and CLI help. Each cell states applicability, implementation owner, changed/reused
mechanism and exact verification. Reuse requires new-kind evidence. No cell passes through an indexed owner link.

The verification matrix must cover F1–F6 in the proposal, including valid/invalid metadata/path/prefix/H1/alias
and relations; global plus registered namespace list/filter/search/exact-ID/pinning/resolve/incoming/outgoing refs;
source authoring to migration to sync/get-context consumer to maintenance; all canonical migration paths;
old-kind regressions and docs-only built-wheel consumption. Record lifecycle L1–L4 and viewer V1–V4 as required
milestone dependencies with their owners, not unowned deferred gaps. The audit in
[materials](materials/support-audit.md) is source inspection, not passing implementation evidence.
