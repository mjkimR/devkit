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
milestone, or merging two of them, breaks every reference written with the old ID: `RULE-document-reference`
reports each one as unresolved, and `devkit spec resolve <old-id>` finds nothing. The only rename handled today is
the handed-off `PROP-<slug>` to `SPEC-<slug>` rewrite of the proposals lifecycle.

## 2. Decision Drivers

- A rename must not break references, and current documents must converge on the canonical ID.
- Relation fields are typed by the prefix written in them (`stories` takes `US-` IDs), so an alias must not change
  the kind a reference appears to have.
- Every identity check must agree on what an ID resolves to; a fallback in one caller leaves the others failing.
- Records are never rewritten: historical files, and decision records that name a retired ID on purpose.
- No ADR file and no ADR ledger rule changes with this decision; approved ADRs stay append-only.

## 3. Considered Options

1. **Exact IDs only**: the present state; a rename means editing every reference by hand.
2. **ADR-only aliases tied to deletion-based compaction**: withdrawn with the compaction direction in this Planning.
3. **Aliases on renameable Living Spec documents, resolved through one canonical mapping (chosen)**.

## 4. Decision Outcome

Option 3.

- **Kinds**: `aliases` is accepted on `CAP`, `US`, `ARCH` and `MS` documents (namespace documents included). It is
  refused on `ADR` (approved ADRs are never renamed or deleted, so an ADR alias could never be used without breaking
  the append-only ledger), on `MAT` (`RULE-document-reference` does not check materials, so their aliases could not
  be validated) and on proposal and spec-bundle kinds (`PROP`, `PADR`, `SPEC`, `PLAN`, `TASKS`, `REC`, `FB`), whose
  IDs follow the delivery lifecycle and its handoff rename. A refused or malformed field is a recorded issue that
  `RULE-document-reference` reports.
- **Shape**: a list of full IDs with the declaring document's own prefix, never its own ID, no item repeated.
  `aliases` entries are identity, not references: not a relation field, not counted as incoming references and never
  rewritten.
- **Precedence and collisions**: a declared ID always wins. An alias resolves only when exactly one document declares
  it and no document has it as its ID. Otherwise the collision is reported on every document involved, the target
  resolves as it would without the alias (or stays ambiguous), and `devkit rules fix` leaves the reference unchanged.
- **One canonical mapping**: `DocumentIndex` keeps the aliases beside the IDs and offers one mapping from a written
  target to its canonical document and whether an alias was used. `resolve()` itself uses it, as do `incoming()`,
  the `depends_on` cycle graphs, milestone membership in hygiene, the traceability reverse-link comparison, `refs`
  grouping and every caller that reads `by_id` or compares against `.id`. The devkit-agt rules catalog stays exact-ID.
- **References**: an alias reference resolves. In a current document it is an error that `devkit rules fix`
  rewrites to the canonical ID (frontmatter and prose, through the existing rewrite service). In historical files
  (completed spec bundles, done or dropped milestones) and in decision records (ADRs under `docs/decisions/` and
  PADRs, which graduate into ADRs) it resolves silently and is never rewritten, so a record that names the retired
  ID as history keeps its meaning. A glossary Owner naming an alias is reported but not fixed.
- **Output**: `devkit spec resolve <alias>` prints the canonical document with `alias=<alias>` in its `[DOCUMENT]`
  sentinel and an `alias` field in JSON; no notice is emitted. `devkit spec refs <canonical> --direction in` includes
  alias-written references, and `--direction out` groups an alias and its canonical ID as one target.
  `devkit spec search` pins an exact alias match like an exact ID.

## 5. Consequences

- A rename keeps the old ID in `aliases`, and one `devkit rules fix` moves current documents to the new ID.
- No handoff change: with ADRs refused and the own-prefix rule, no alias can equal a graduating `ADR-<slug>`.
- Aliases are identifiers, not search keywords; the playbook field of the same name follows this meaning
  (`PADR-playbook-aliases-as-identifiers`).
- ADR supersession stays as it is, and no ADR file is edited by this work.
