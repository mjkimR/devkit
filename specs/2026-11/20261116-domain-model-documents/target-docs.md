---
id: PROP-domain-model-documents-target
title: Target Living Spec Structure for Domain-model documentation
summary: "Defines the two maintained domain relationship entries, selected discovery links, generic source guidance and independent global and package validation."
status: draft
proposal: SPEC-domain-model-documents
created_at: 2026-11-16
targets:
- file: docs/domain/delivery-relationships.md
- file: docs/domain/bundle-selection-and-installation.md
- file: docs/capabilities/documents/CAP-DOCS-documentation-ownership.md
- file: docs/capabilities/delivery/CAP-DLV-proposal-lifecycle.md
- file: docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md
- file: docs/steering/glossary.md
- file: docs/decisions/2026-11/20261116-linked-domain-relationship-views.md
- file: packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md
---

# [Blueprint] PROP-domain-model-documents: Target Living Spec Structure

## Exact Development scope

| File | Change |
| --- | --- |
| `docs/domain/delivery-relationships.md` | New ID-free entry answering how proposal/spec identity, milestone membership, prerequisite and provenance differ; include a membership-change walkthrough. |
| `docs/domain/bundle-selection-and-installation.md` | New ID-free entry adapting the pilot: available bundle → requested assets → managed/projected destinations → receipt evidence. Distinguish stable conceptual identity from physical paths. |
| `CAP-DOCS-documentation-ownership` | Add domain home/representation clauses and update deferred-home scope text. Retain the common ownership matrix unchanged. |
| `CAP-DLV-proposal-lifecycle` | Add one selected ordinary link near Handoff Steps for membership/prerequisite/provenance understanding; change no handoff rule. |
| `CAP-DIST-sync-and-transactions` | Add one selected ordinary link near selection/receipt explanation; change no transaction, readiness or recovery rule. |
| `docs/steering/glossary.md` | Add concise ordinary links beside distribution and delivery term groups. Keep existing term definitions and authority columns. |
| ADR-linked-domain-relationship-views (planned) | Promote the PADR through handoff; date partition follows actual handoff date if different from the listed candidate. |
| `packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/instructions/living-spec-writing.md` | Add the consumer-generic domain home, question/overview/authority/next-step and selected-owner-link convention beside existing design guidance. No repository IDs or duplicate matrix. |

New files use nearest existing parents `docs/` and `docs/decisions/` in proposal boundaries; this table limits them
to the exact leaves. No existing architecture, document-model/lookup/search/namespaces contract, delivery rule,
manifest, synonym file or production implementation is changed. No package-specific production entry is invented.
No screens are drafted. The source instruction is shared with operations Planning: collect both scopes and
implement sequentially, preserving the resulting other-role guidance; no concurrent authoring of the shared file.

## Content and authority audit

Delivery: cite `CAP-DOCS-document-model` §3.3 for relation grammar and provenance, `CAP-DLV-spec-bundles` §3 rule 7
for direct specs, and `CAP-DLV-proposal-lifecycle` §4.1 for handoff. Walk through a proposal moving membership:
which relationship changes, which prerequisite/provenance does not follow from that change, and which contract
owns validity/command behavior. No change is executed; examples are non-normative.

Distribution: cite `CAP-DIST-content-packages` for availability, `CAP-DIST-manifest-spec` for assets/presets,
`CAP-DIST-agent-projections` for projected kinds/destinations and `CAP-DIST-sync-and-transactions` §§1–2 for selection
and receipt evidence. Explain that one conceptual asset can be represented by managed and host paths and that
recorded selection is evidence rather than another selection input. Link exact syntax/mechanism only as needed.
The pilot remains historical evidence; adapt current content and verify current owner passages.

Every substantive summary names its normative owner. Transfer count is zero; no unchanged invariant is relabeled
as a separate conceptual/behavioral authority. Glossary keeps terms; entries add relationship understanding.

## Development acceptance and evidence

| ID | Scenario and pass evidence |
| --- | --- |
| D1 | Review both entries against the owner passages above. Each entry alone answers its question with an overview, authority boundary and next useful step. Record a statement-to-owner audit and glossary checks. No Python-class or database-schema prerequisite. |
| D2 | A fresh independent reader receives only the global lifecycle owner ID and membership/prerequisite/provenance question, without entry names, materials, inventories or prior reader output. Resolve the owner, follow its selected link, explain the relationship difference and locate the needed validity/handoff source. Repeat with a fresh reader for the distribution owner and availability/selection/projection/receipt question. Log opened sections, avoidable reads, unclear next steps and wrong-owner answers. Pass when the reader finds the entry, gives the distinction correctly and reaches needed authority without a whole-layer prerequisite. |
| D3 | In one ignored disposable fixture with global, registered alpha and unrelated beta namespaces, place a representative package-local domain entry and selected owner link, using actual namespace registration and commands. A fresh independent reader starts only with alpha source cwd, package owner ID and relationship question, resolves the owner and follows to entry/needed contract. Entry filenames/results are withheld. Verify default list/search sees global+alpha, global-only excludes alpha, all-namespaces includes beta, and ordinary relative links resolve at actual depth. No actual package content/config is created. |
| D4 | Verify both entries have no ID, remain absent as indexed nodes in list/search/resolve/refs, while owner lookup/search/refs retain existing behavior. Search can find owner wording; make no assertion that it discovers the entry directly. Check ordinary link destinations and source agreement manually, since document rules do not prove these semantics. |
| D5 | Sync source guidance to an isolated consumer through the existing instruction asset and confirm delivered bytes, generic wording and no generated domain scaffold/identity. Reuse existing distribution checks; no new template inventory or runtime test tier is selected. |
| D6 | Scoped document/asset rules, source hygiene, whitespace and applicable workflow/envelope checks pass. Run relevant existing docs distribution checks and required lint/type/affected checks if Development changes executable/test code; keep affected full fallback. Record qualitative outcomes without timing/count improvements. |

Development may create probes only within its Host-assigned ignored root. Planning does not create fixture repos.
Freeze author writes and HEAD during each read-only reader/reviewer; compare full tracked plus nonignored-untracked
snapshots before/after. Explicit scopes and snapshots substitute for native confinement; report any outside read.
A failed route is corrected and independently rerun. A still-unmet outcome returns to the Host before expanding
scope; it does not authorize a Kind or runtime implementation.

## Restatement and exclusions

The PADR's lasting domain location/entry/navigation clauses are restated in `CAP-DOCS-documentation-ownership`,
Domain representation subsection (SHOULD), with ID-free identity boundary (MUST). Generic source instructions
implement these clauses; they add no authority matrix. Existing ownership and transfer rules already apply.
Lifecycle automation, viewer support, recovery procedures, broad normative migration and repository-wide modeling
are excluded. Review only covers owner uniqueness, relationship adequacy and ordinary navigation.
