---
id: ADR-documentation-ownership-and-linked-design-entries
title: Documentation ownership and linked design entries
summary: "For distinct documentation responsibilities, we retain unique owners and linked ID-free design entries, to expose mechanisms without widening identity contracts, accepting discovery through selected owner links."
proposal: SPEC-design-document-foundation
status: accepted
created_at: 2026-11-16
---

# [ADR-documentation-ownership-and-linked-design-entries] Documentation ownership and linked design entries

## 1. Context & Problem Statement

A contract-only reader lacks a direct route to the retained transaction mechanism detail. Supplied design entries
work, and existing indexed owners are searchable/resolvable. Distinct domain, design and operations roles require
clean boundaries with architecture and behavioral contracts. A separate role does not by itself require a Kind.

## 2. Decision Drivers

- Preserve one normative owner per statement and unchanged safety/recovery authority.
- Give agents a question-specific entry with useful overview and next action.
- Keep local mechanism explanation distinct from system architecture.
- Add no identity/runtime surface without a demonstrated required outcome.

## 3. Considered Options

- Linked ID-free design entry and optional detail: separate content responsibility, selected owner-linked discovery,
  no design index identity. Recommended.
- Existing ARCH entry plus optional details: indexed and appropriate for system responsibilities, but routes local
  implementation mechanisms through the architecture taxonomy.
- New design Kind: independent indexed discovery with at least an enum member and definition row. Many consumers
  are data-driven; exact kind-specific grammar/rule changes need inspection. No required indexed outcome is demonstrated.
- Existing capability/reference as design entry: cheap routing, but mixes contract/reference and mechanism ownership
  if the explanation itself is made authoritative there.

## 4. Decision Outcome

Choose linked ID-free design entries, conditional on required independent global/package walkthroughs during
Development. Failed navigation is corrected or returned for scope review; it does not imply new runtime authority.

- Each normative statement retains one primary owner; concise orientation cites that owner. Domain, design and
  operations remain separate responsibilities, with no rigid authoring order. → `CAP-DOCS-documentation-ownership` §3.1 (MUST/SHOULD).
- Architecture retains structure, system interactions, deployment, architectural constraints, cross-cutting
  technical concepts, quality and risk. Local mechanisms use design unless they establish an architectural boundary.
  → `CAP-DOCS-documentation-ownership` §3.2 (SHOULD).
- Current mechanism explanations use ID-free `docs/designs/<slug>.md` entries with optional supporting files, and
  selected question-specific owner links. Package-local examples use the analogous namespace docs root.
  → `CAP-DOCS-documentation-ownership` §3.3 (SHOULD/MUST).
- No new Kind, identity grammar, relation, registry, CLI/MCP/runtime feature or viewer support is selected.
- Domain and operations homes remain with `SPEC-domain-model-documents` and `PROP-operations-documents`.

`ADR-document-system` remains in force: document identity/index and implementation ownership do not change.
No accepted ADR is superseded, wholly or partially.

## 5. Consequences

The smallest real implementation adds a maintained design entry/detail and one contract link. Other owners and
pilot evidence remain intact. ID-free entries/details are absent from document search/resolve/refs, and ordinary
link integrity and semantic source agreement need review. Required indexed design discovery would trigger a later
scope decision only when demonstrated navigation cannot meet an agreed requirement. Viewer and lifecycle work
remain with their existing proposals.

## 6. Confirmation

Review only for semantic owner uniqueness and question-specific navigation. Execute F1–F6 in `SPEC-design-document-foundation`,
including withheld-entry global and package-fixture paths, source asset distribution and relative-link checks.
Scoped document rules verify applicable identity/frontmatter/reference contracts; they do not prove ID-free link
integrity or ownership semantics. `CAP-DOCS-documentation-ownership` restates the lasting clauses.
