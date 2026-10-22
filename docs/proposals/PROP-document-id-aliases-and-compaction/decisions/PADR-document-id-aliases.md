---
id: PADR-document-id-aliases
title: Document ID aliases
summary: Living Spec documents may declare aliases, previous or alternate IDs of their own kind, resolved by DocumentIndex through one alias-aware lookup; an alias reference in a current document is an error that devkit rules fix rewrites to the canonical ID.
proposal: PROP-document-id-aliases-and-compaction
status: draft
created_at: 2026-10-22
---

# [PADR-document-id-aliases] Document ID aliases

- **Status**: Draft
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

A Living Spec document is found only by its exact ID. Renaming a capability, story, architecture document or
decision, or merging two of them, breaks every reference written with the old ID: `RULE-document-reference`
reports each one as unresolved, and `devkit spec resolve <old-id>` finds nothing. The only rename handled today is
the handed-off `PROP-<slug>` to `SPEC-<slug>` rewrite of the proposals lifecycle.

## 2. Decision Drivers

- A rename must not break references, and current documents must converge on the canonical ID.
- Relation fields are typed by the prefix written in them (`stories` takes `US-` IDs), so an alias must not change
  the kind a reference appears to have.
- Every identity check must agree on what an ID resolves to; a fallback in one caller leaves the others failing.
- Historical files (completed spec bundles, done or dropped milestones) are records and are never rewritten.
- No ADR file and no ADR ledger rule changes with this decision.

## 3. Considered Options

1. **Exact IDs only**: the present state; a rename means editing every reference by hand.
2. **ADR-only aliases tied to deletion-based compaction**: withdrawn with the compaction direction in this Planning.
3. **Aliases on Living Spec documents, resolved by one alias-aware lookup (chosen)**.

## 4. Decision Outcome

Option 3.

- **Field**: a document may declare `aliases`, a list of full IDs (previous or alternate IDs of the same document).
  Accepted on the Living Spec kinds `CAP`, `US`, `ARCH`, `ADR`, `MAT` and `MS` (namespace documents included).
  Refused on proposal and spec-bundle kinds (`PROP`, `PADR`, `SPEC`, `PLAN`, `TASKS`, `REC`, `FB`), whose IDs follow
  the delivery lifecycle and its handoff rename.
- **Shape**: each alias is a well-formed ID with the declaring document's own prefix (a `CAP-` document aliases only
  `CAP-` IDs), never its own ID, and no alias appears twice. A malformed field is a recorded issue that
  `RULE-document-reference` reports.
- **Uniqueness**: an alias equals no declared ID of any status and no alias of another document; a collision is
  reported on both documents. An old file that still exists therefore cannot be aliased.
- **Index**: `DocumentIndex` keeps the aliases beside the IDs and offers one alias-aware lookup returning the
  document and whether it was reached through an alias. Every identity check uses it: the rule's resolution and
  handed-off checks, traceability, dependencies, browse, roadmap, scaffold, specs, handoff and the proposals rewrite
  service. The devkit-agt rules catalog stays exact-ID.
- **References**: an alias reference resolves. In a current document it is an error that `devkit rules fix`
  rewrites to the canonical ID (frontmatter and prose, through the existing rewrite service); in a historical file
  it resolves silently and is never rewritten.
- **CLI**: `devkit spec resolve <alias>` reports the canonical ID and the alias it was reached through;
  `devkit spec refs <canonical> --direction in` includes references written with an alias; `devkit spec search`
  pins an exact alias match like an exact ID.
- **Handoff**: a graduating PADR's `ADR-<slug>` is refused when it equals a declared alias, as for a declared ID.

## 5. Consequences

- A rename keeps the old ID in `aliases`, and one `devkit rules fix` moves current documents to the new ID.
- Aliases are identifiers, not search keywords; the playbook field of the same name follows this meaning
  (`PADR-playbook-aliases-as-identifiers`).
- ADR supersession stays as it is: `supersedes` and `superseded_by` on ADRs remain unchecked, and no ADR file is
  edited by this work.
