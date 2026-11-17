---
id: DOMAIN-delivery-relationships
title: "Delivery relationships"
status: active
area: delivery
summary: "Distinguishes proposal and spec identity, milestone membership, prerequisites and provenance across delivery."
related_capabilities: [CAP-DOCS-document-model, CAP-DLV-proposal-lifecycle, CAP-DLV-spec-bundles]
---

# [DOMAIN-delivery-relationships] Delivery relationships

When work moves into Development, readers confuse proposal/spec identity, milestone membership, prerequisite and
provenance: each answers a different question, and handoff carries, relocates or drops each differently.

## Relationship overview

A proposal and a spec are different Unit anchors: Planning settles a proposal's direction; handoff creates the spec
bundle for Development. `CAP-DLV-proposal-lifecycle` §4.1 owns that transformation and its validation.
A direct spec starts without a proposal or milestone membership (`CAP-DLV-spec-bundles` §3 rule 7).

Three relationships answer different questions (`CAP-DOCS-document-model` §3.3):

| Concept or relationship | Distinction | Authoritative owner |
| --- | --- | --- |
| Milestone membership | Answers which milestone groups this proposed work: a proposal's `milestone` names an MS anchor. SPEC milestone metadata supplies no membership reference. | `CAP-DOCS-document-model` §3.3 owns the grammar. |
| Unit prerequisite | Answers which other Unit this Unit depends on: `depends_on` on a proposal/spec anchor names exact PROP/SPEC anchors. Milestone dependencies form a separate MS graph. | `CAP-DOCS-document-model` §3.3 owns both grammars. |
| Provenance | Answers where this Unit originated: `proposal`, `decomposed_from` and Unit `supersedes` preserve origin outside the current reference graph; `refs` does not expose them as current references. | `CAP-DOCS-document-model` §3.3 owns their interpretation. |

At handoff, outgoing Unit prerequisites are carried to the spec and live incoming prerequisite targets are relocated.
Milestone membership is not carried. The retained `proposal` field records origin, not a current prerequisite or
fulfillment claim. These transformations and their refusal behavior belong to `CAP-DLV-proposal-lifecycle` §4.1.

## Membership-change walkthrough

Suppose proposal A belongs to milestone Spring and depends on spec Foundation.
Moving A's membership to milestone Summer changes the grouping relationship. That move alone says nothing about
whether Foundation is complete or whether A still depends on it. It creates no proposal/spec origin relationship.

If A is then handed off, the resulting spec retains the prerequisite and the proposal origin, while milestone
membership stays outside the spec. The projected dependency validation and reference relocation follow
`CAP-DLV-proposal-lifecycle` §4.1.

## Update triggers

- `CAP-DOCS-document-model` §3.3 changes a relationship field or its graph.
- `CAP-DLV-proposal-lifecycle` §4.1 changes how handoff carries, relocates or drops a relationship.
- `CAP-DLV-spec-bundles` §3 rule 7 changes how a spec starts without a proposal.
