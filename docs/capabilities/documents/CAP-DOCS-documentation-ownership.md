---
id: CAP-DOCS-documentation-ownership
title: Documentation ownership and linked entries
summary: "Assigns one normative owner per documentation responsibility and question-specific routes to maintained ID-free design and domain explanations, without extending document identity or runtime support."
area: documents
status: active
usecases: []
---

# [CAP-DOCS-documentation-ownership] Documentation ownership and linked entries

## 1. Summary

Documentation responsibilities determine ownership. Domain meaning, current implementation design and operations
composition are distinct roles alongside architecture and behavioral contracts. A role does not require its own
indexed Kind. `ADR-documentation-ownership-and-linked-design-entries` records the representation decision.

## 2. Scope & Boundary

- **In-Scope**: shared semantic ownership, architecture overlap and question-specific ID-free design and domain navigation.
- **Out-of-Scope**: identity/index/placement grammar (`CAP-DOCS-document-model`), search
  (`CAP-DOCS-document-search`), lookup (`CAP-DOCS-document-lookup`) and namespaces (`CAP-DOCS-namespaces`).
  Operations home, lifecycle and viewer support remain with `PROP-formal-document-kinds`, `PROP-design-document-lifecycle` and `PROP-design-document-viewer`.

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

### 3.3 Representation

1. **Entry**: Authors SHOULD maintain current design explanations as ID-free `docs/designs/<slug>.md` entries,
   with analogous `designs/` under a registered package's docs root.
2. **Independent usefulness**: Authors SHOULD make the entry useful alone for its question, mechanism overview,
   authority boundary and next action, and each detail independently understandable.
3. **Supporting content**: WHEN useful content exceeds the entry's question, authors SHOULD link only the needed
   detail, diagrams, examples or datasheets, optionally under `<slug>/`.
4. **Discovery**: Authors SHOULD add selected question-specific links from existing owners to needed design entries.
5. **No identity borrowing**: Authors MUST keep ID-free design entries and supporting files outside indexed document identity.

A small design may need only its entry. No empty hierarchy, all-pairs links, reciprocal registry, whole-layer reading
prerequisite or fixed hop cap is required. Full IDs cite indexed owners; ordinary Markdown links reach ID-free
content. `docs refs` retains indexed reverse lookup; ordinary design links create no index/search/resolve/refs node.

### 3.4 Domain representation

1. **Domain home**: Authors SHOULD maintain conceptual relationship entries as ID-free `docs/domain/<slug>.md`,
   with analogous `domain/` under a registered package's docs root.
2. **Independent usefulness**: Authors SHOULD give each entry its reader question, relationship overview,
   authority boundary and next useful step, splitting only useful supporting detail.
3. **Discovery**: Authors SHOULD add selected question-specific links from existing owners to needed domain entries.
4. **No identity borrowing**: Authors MUST keep ID-free domain entries and supporting files outside indexed document identity.

Domain entries compose concepts, identity, relationships and lifecycles alongside structure and contracts.
They need no class catalog, schema catalog, fixed authoring order, reciprocal registry, all-pairs links,
whole-layer prerequisite or fixed hop cap. Full IDs cite indexed owners; ordinary links reach ID-free entries.
Existing owner lookup/search and indexed reverse references remain available; domain entries create no independent
index/search/resolve/refs node. `ADR-linked-domain-relationship-views` records the representation choice.

## 4. Interfaces & Data Contracts

The optional `.devkit/managed/docs/templates/design-template.md` is an authoring aid, not a schema or generator.
The docs bundle supplies generic instructions and this template through its existing templates asset.
Semantic ownership, source agreement and ordinary navigation are **Review only**; document rules check applicable
identity/frontmatter/references without validating these semantics or ID-free ordinary links.
