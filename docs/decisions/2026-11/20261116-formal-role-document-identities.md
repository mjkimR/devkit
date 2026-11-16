---
id: ADR-formal-role-document-identities
title: Formal role documents with canonical identities
summary: "For independently maintained role documents, we register design, domain and operations with canonical IDs and complete tool support, to enable direct discovery and references, accepting schema and migration work."
proposal: SPEC-formal-document-kinds
supersedes: [ADR-documentation-ownership-and-linked-design-entries, ADR-linked-domain-relationship-views]
status: accepted
created_at: 2026-11-16
---

# [ADR-formal-role-document-identities] Formal role documents with canonical identities

- **Status**: Accepted
- **Date**: 2026-11-16

---

## 1. Context & Problem Statement

Independently maintained conceptual, implementation and operational knowledge requires direct identity,
discovery and references. Existing ID-free role entries cannot meet that requirement. Existing ownership
boundaries remain useful, but their identity restrictions are superseded by the required formal standing.

This decision meets admission criteria: it changes public identity/schema contracts and lasting role policy,
affects multiple kinds and dependent consumers, and compares viable formal layouts.

## 2. Decision Drivers

- Give each canonical role document equal direct tool standing.
- Express conceptual and implementation cohesion without mandatory whole-layer reading.
- Preserve one primary authority per statement and existing behavioral guarantees.
- Keep global identity compatible with package namespace selection.
- Deliver complete schema, discovery, authoring and migration contracts independent of delivery approach.

## 3. Considered Options

All viable options register formal Kind/prefix/ID. ID-free canonical content is outside the decided goal.

- Flat prefixed filenames, optional target-typed relations: direct topic naming and namespace partitioning;
  catalogs scale through list/search and selected links rather than a forced area taxonomy. Selected.
- Area-scoped formal filenames and required area: good for stable exclusive areas; cross-area concepts require
  artificial identity ownership and area moves alter IDs. No exclusive role-area taxonomy exists for these inputs.
- Topic-grouped formal filenames with independent stem IDs: physical detail cohesion; path and pin migrations
  are needed on regrouping, and the folder taxonomy adds classification separate from globally unique identity.

Status, relation-field and source-entrypoint comparisons are recorded in [the contract](../../materials/2026-11/20261116-formal-document-kinds/core-contract.md).
No option is selected for implementation minimization.

## 4. Decision Outcome

Choose flat formal role documents with independent detail IDs and complete existing-tool integration.

- Design, domain and operations have DESIGN, DOMAIN and OPS prefixes, public kind values design, domain and
  operations, flat canonical prefixed stems under designs, domain and operations in every docs root, and equal
  direct identity/discovery/reference support. → `CAP-DOCS-document-model` §§3.1–3.2,4 (MUST).
- All canonical role documents have required id/title/status/summary and first-H1 identity; draft/active/retired
  is their strict vocabulary, retired is browsing-terminal, and aliases retain same-prefix rename identity.
  → `CAP-DOCS-document-model` §§3.2,3.5,4 (MUST).
- Target-typed optional related_designs, related_domains and related_operations fields carry current references;
  identity aliases, delivery provenance and ADR supersession retain distinct meanings. → `CAP-DOCS-document-model`
  §§3.3,3.5 (MUST).
- Independent Markdown details own formal identities; parent-owned support artifacts use the explicit identified
  parent artifact subtree and no fake IDs. → `CAP-DOCS-documentation-ownership` §3.3 (MUST/SHOULD).
- Domain owns conceptual knowledge, design owns implementation explanation and operations owns evidence routing;
  existing behavioral/action authorities remain until an explicit same-change transfer removes duplicate
  restatements. No reciprocal registry, fixed reading order or whole-layer prerequisite is required.
  → `CAP-DOCS-documentation-ownership` §§3.1–3.3 (MUST/SHOULD).
- Design accepts optional source file/directory entrypoints for liveness and reverse lookup; domain and operations
  use body/owner links. Entrypoints establish neither behavioral correctness nor public adapter standing.
  → `CAP-TRACE-code-entrypoints` §§3.1–3.3 (MAY/MUST).
- Neutral formal templates/instructions ship in docs independently of spec; lifecycle and viewer integration are
  required separately owned phases of the milestone. → `CAP-DOCS-document-model` Document asset distribution
  (MUST).

Supersedes in part `ADR-documentation-ownership-and-linked-design-entries`: the ID-free design representation, exclusion from indexed identity and selected absence of Kind, identity grammar, relations and runtime support.

Supersedes in part `ADR-linked-domain-relationship-views`: the ID-free domain representation, exclusion from indexed identity and selected absence of Kind, template, namespace and runtime support.

Both earlier ADRs retain unique authority, conceptual/implementation separation and selective navigation clauses.
They remain accepted with matching partial-supersession pointers. Their past
choice and evidence remain historical; their denial of viewer/lifecycle selection is superseded for these roles
by the required dependent phases, not permission to rewrite their rationale. The archived unmerged operations
choice is historical input; no nonexistent accepted main operations ADR is claimed or superseded.

## 5. Consequences

Every canonical retained role document, including independent detail, is migrated and can be found directly.
Strict role schema and artifact exceptions require model/governance tests. Flat catalogs rely on descriptive
slugs and search; an actual stable-area organization need triggers a later explicit compatibility decision.
Rename keeps aliases; cross-kind transfer retains a retired old node. Historical path records remain resolvable
through pinned source history, while live ingress is rewritten to IDs. Existing guarantees are not transferred.
Lifecycle and viewer phases must consume this contract before milestone completion.

## 6. Confirmation

`SPEC-formal-document-kinds` verifies F1–F6 through actual global/package role nodes, positive/negative schema and
reference tests, composed artifact maintenance, real snapshot parent/source deletion, public compatibility,
separate-process persistent memo and a docs-only installed-wheel consumer. The [core development evidence](../../materials/2026-11/20261116-formal-document-kinds/development-evidence.md)
records the five canonical migrations and ordinary-link checks. RULE-id-convention, RULE-spec-format,
RULE-document-summary, RULE-document-reference and RULE-code-entrypoints enforce applicable structure.
Semantic ownership, source agreement, independent-detail classification and ordinary artifact links remain Review
only. Required `SPEC-design-document-lifecycle` L1–L4 and `PROP-design-document-viewer` V1–V4 proof remains pending;
core verification alone does not complete the milestone.
