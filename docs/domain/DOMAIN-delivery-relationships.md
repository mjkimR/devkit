---
id: DOMAIN-delivery-relationships
title: "Delivery relationships"
status: active
summary: "Distinguishes proposal and spec identity, milestone membership, prerequisites and provenance across delivery."
---

# [DOMAIN-delivery-relationships] Delivery relationships

## Question

How do proposal/spec identity, milestone membership, prerequisite and provenance differ when work moves into Development?

## Relationship overview

A proposal and a spec are different Unit anchors: Planning settles a proposal's direction; handoff creates the spec
bundle for Development. `CAP-DLV-proposal-lifecycle` §4.1 owns that transformation and its validation.
A direct spec starts without a proposal or milestone membership (`CAP-DLV-spec-bundles` §3 rule 7).

Three relationships answer different questions (`CAP-DOCS-document-model` §3.3):

| Relationship | Question answered | Representation and owner |
| --- | --- | --- |
| Milestone membership | Which milestone groups this proposed work? | A proposal's `milestone` names an MS anchor. SPEC milestone metadata supplies no membership reference; document-model §3.3 owns the grammar. |
| Unit prerequisite | Which other Unit does this Unit depend on? | `depends_on` on a proposal/spec anchor names exact PROP/SPEC anchors. Milestone dependencies form a separate MS graph; document-model §3.3 owns both grammars. |
| Provenance | Where did this Unit originate? | `proposal`, `decomposed_from` and Unit `supersedes` preserve origin outside the current reference graph. Document-model §3.3 owns their interpretation; `refs` does not expose them as current references. |

At handoff, outgoing Unit prerequisites are carried to the spec and live incoming prerequisite targets are relocated.
Milestone membership is not carried. The retained `proposal` field records origin, not a current prerequisite or
fulfillment claim. These transformations and their refusal behavior belong to `CAP-DLV-proposal-lifecycle` §4.1;
relationship grammar remains with `CAP-DOCS-document-model` §3.3.

## Membership-change walkthrough

This is a nonexecuted example. Suppose proposal A belongs to milestone Spring and depends on spec Foundation.
Moving A's membership to milestone Summer changes the grouping relationship. That move alone says nothing about
whether Foundation is complete or whether A still depends on it. It creates no proposal/spec origin relationship.
`CAP-DOCS-document-model` §3.3 remains the source for valid relationship fields and graph separation.

If A is then handed off, the resulting spec retains the prerequisite and the proposal origin, while milestone
membership stays outside the spec. The projected dependency validation and reference relocation follow
`CAP-DLV-proposal-lifecycle` §4.1. This example changes no files and prescribes no command.

## Authority boundary and next useful step

This entry composes relationships; it adds no validity rule, lifecycle permission or transformation contract.
For an invalid relationship or graph question, resolve `CAP-DOCS-document-model` and read §3.3.
For what handoff writes, validates or relocates, resolve `CAP-DLV-proposal-lifecycle` and read §4.1.
For creating a spec directly, resolve `CAP-DLV-spec-bundles` and read §3 rule 7.
Load the owner needed for that question; no architecture, class catalog or whole document layer is a prerequisite.
