---
id: CAP-DOCS-documentation-ownership
title: Documentation ownership and linked entries
summary: "Assigns one normative owner per responsibility and per fact type, keeps capabilities to observable contracts, and sets question-specific navigation among formal design, domain and operations documents, independent detail and parent-owned support."
area: documents
status: active
usecases: []
entrypoints:
  - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md
---

# [CAP-DOCS-documentation-ownership] Documentation ownership and linked entries

## 1. Summary

Documentation responsibilities determine ownership. Domain meaning, current implementation design and operations
composition are distinct roles alongside architecture and behavioral contracts. All three have formal indexed Kinds and prefixes. `ADR-formal-role-document-identities` records the representation decision, and `ADR-area-scoped-design-bundles` the design bundle and domain area paths.

## 2. Scope & Boundary

- **In-Scope**: shared semantic ownership, architecture overlap and question-specific formal design, domain and operations navigation.
- **Out-of-Scope**: identity/index/placement grammar (`CAP-DOCS-document-model`), search
  (`CAP-DOCS-document-search`), lookup (`CAP-DOCS-document-lookup`) and namespaces (`CAP-DOCS-namespaces`).
  Delivery integration belongs to `CAP-DLV-delivery-workflows`; viewer reading belongs to `CAP-VIEW-repository-viewer`.

## 3. Business Rules & Policies

### 3.1 Ownership

1. **Unique authority**: Authors MUST assign each normative statement one primary owner.
2. **Orientation**: WHEN repeating a concise non-normative summary, authors SHOULD cite its authoritative owner.
3. **Transfer**: WHEN transferring a normative statement, authors MUST remove or replace the previous normative
   restatement in the same change while naming the receiving owner.
4. **Role separation**: Authors MUST retain domain meaning, implementation design and operations composition as
   distinct responsibilities without imposing a fixed authoring order.
5. **Responsibility routing**: Authors SHOULD select the owner by the statement's responsibility in the table below.

| Responsibility / reader question | Primary owner |
| --- | --- |
| Observable behavior, validity, safety or externally visible limits | Capability |
| Actor goal, scenario and success contract | Use case |
| Human interface element and interaction | UX |
| Concepts, identity, relationships and lifecycles as a conceptual basis alongside structure/contracts | Domain model; glossary for term definitions |
| System structure, interactions, deployment and architectural constraints | Architecture |
| Cohesive implementation method, local mechanism, worked example or datasheet | Current design explanation; source executes behavior |
| Enduring choice, alternatives and rationale | ADR |
| Historical experiment, assumption or measurement | Materials |
| Exact command/API/config syntax or error mapping | Reference |
| Contributor development activity | Development guide |
| Symptom and evidence → existing action owner → normal-state observation | Operations composition |
| Executable recovery steps and permissions | Existing instruction, playbook, advisory or executable owner |

6. **Operational authority**: Operations compositions MUST route actions to their existing owners rather than
   introduce duplicate recovery procedures or permissions.
7. **Fact-type routing**: Authors SHOULD route each fact by its type in the table below; a fact with two parts
   splits between the owners named. An order or tie-break a consumer can observe is a capability rule; an internal
   order is design. The docs bundle's `living-spec-writing` instruction carries the same rows for agents.

| Fact type | Owner |
| --- | --- |
| Behavior, limit, output order or tie-break a consumer can observe | Capability |
| That a code is raised, and when, as a guarantee | Capability rule; trigger condition, level and fix in a reference code table |
| Command, flag, configuration key or payload field syntax | Reference; the capability lists the interface |
| Data that a later run, another process or another tool reads back: location pattern, encoding, fields, example | Design datasheet; a format consumers author or parse is also a capability interface |
| How an ID, key, hash, token or name is derived | Design; what the identity means belongs to the domain model |
| Internal processing order, algorithm or pseudocode | Design, or the source alone |
| Concept meaning, identity and lifecycle | Domain model; glossary for terms |
| Rationale and rejected options | ADR |
| Measurement or experiment | Materials |

8. **Observable contract**: A capability SHOULD state what a consumer can observe or rely on, and SHOULD leave out
   implementation pseudocode, internal algorithm steps, formats only the implementation reads back and paragraphs
   another document owns, routing them by rule 7. The docs bundle's `capability-writing` instruction ("What Stays
   Out") and capability template carry this guidance; no check enforces it.

Domain meaning supplies a conceptual basis; it is not a prerequisite document layer. Design may include diagrams,
examples and numerical datasheets as the question needs. Document length and numerical content do not route ownership.

### 3.2 ARCH boundary

1. **System responsibility**: Authors SHOULD keep system structure, system interactions, deployment, architectural
   constraints, cross-cutting technical concepts, quality scenarios and risk in architecture.
2. **Local mechanism**: Authors SHOULD place local implementation mechanisms in design unless the statement
   itself establishes a system responsibility or architectural constraint.

A strategy states the chosen structural approach; the ADR retains its rationale and alternatives. A building block
states responsibility/dependencies rather than every internal algorithm. Runtime views show system interactions;
use cases retain actor goals. Cross-cutting technical concepts differ from domain meaning and observable capability
contracts. Deployment states topology; operations selects existing diagnosis/recovery owners. Quality and risk
already belong to arc42. These are responsibility boundaries, not a chapter tutorial.

### 3.3 Formal roles and useful detail

1. **Formal standing**: Authors MUST give independently maintained design, domain and operations Markdown its own
   DESIGN, DOMAIN or OPS ID and canonical path in the corresponding global or registered package docs root: a design
   bundle `designs/<area>/DESIGN-<slug>/design.md`, a domain file `domain/<area>/DOMAIN-<slug>.md` or a flat
   operations file `operations/OPS-<slug>.md` (`CAP-DOCS-document-model`, `RULE-id-convention`).
2. **Independent usefulness**: Before writing, authors SHOULD settle the one reader question a document answers and
   split or drop a document that has none. The document SHOULD open with the problem it answers (the problem the
   mechanism solves, the concepts readers confuse or the observed symptom) with no question section or label, and
   close with its authority boundary, naming what it does not settle and the owner that does by full ID, and its
   maintenance trigger and next useful action (`ADR-problem-first-formal-document-openings`). An independent detail,
   worked example or datasheet has its own question/maintenance seam and formal peer ID.
3. **Supporting artifacts**: A design's parent-owned support MUST live inside its bundle beside `design.md`, at any
   depth; domain and operations support MUST live under `<PARENT-ID>/artifacts/` beside the parent file, with one
   canonical same-kind parent in the same root. Supporting Markdown MUST be ID-free and name that parent;
   non-Markdown files need no fake identity. Independent detail is a peer bundle or file with its own ID; design
   bundles never nest. An alias does not authorize an orphan old-ID subtree or bundle (`RULE-id-convention`).
4. **Maintenance**: WHEN renaming, moving areas or roots, splitting or reclassifying content, authors MUST retain one
   canonical support owner and repair ordinary links; an area move keeps the ID and updates `area`; a cross-kind
   predecessor remains retired with its replacement named.
5. **Navigation**: Authors SHOULD use selected full-ID links or typed related_* lists for the reader's question;
   no reciprocal registry, all-pairs links, whole-layer prerequisite or fixed hop count is required.
6. **Datasheets**: WHEN a mechanism writes data that a later run, another process or another tool reads back, its
   design SHOULD carry a datasheet stating the location pattern, encoding, fields or layout, identity derivation,
   ordering and one example. No section is required, because no check can tell a datasheet from prose.

Domain owns conceptual knowledge alongside structure and contracts. Design owns implementation explanation,
examples and datasheets. Operations selects existing diagnosis/action owners from evidence and normal-state
observations; it does not gain their recovery authority. A normative behavioral statement keeps its existing owner
unless transferred explicitly under §3.1. This migration transfers no distribution or delivery guarantees.

## 4. Interfaces & Data Contracts

The docs bundle supplies formal design/domain/operations templates and corresponding writing instructions; each
template opens with the problem lead, carries its guidance in HTML comments and closes with `## Authority boundary`
and `## Maintenance and next action`. Formal nodes participate directly
in index/list/search/resolve/refs with `CAP-DOCS-document-model` identity and typed relation rules. Semantic ownership,
source agreement and ordinary artifact/source link destinations are Review only; applicable structural rules do
not prove those semantic or ordinary-link properties. `ADR-formal-role-document-identities` defines the schema and
`ADR-area-scoped-design-bundles` the design and domain paths.
