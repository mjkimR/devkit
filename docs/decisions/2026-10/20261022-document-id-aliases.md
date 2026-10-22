---
id: ADR-document-id-aliases
title: Document ID aliases
summary: Every ID-bearing document may declare aliases, previous or alternate IDs with its own prefix, resolved by DocumentIndex through one alias-aware lookup; an alias reference in a current document is an error that devkit rules fix rewrites to the canonical ID.
proposal: SPEC-document-id-aliases-and-compaction
status: accepted
created_at: 2026-10-22
---

# [ADR-document-id-aliases] Document ID aliases

- **Status**: Accepted
- **Date**: 2026-10-22

---

## 1. Context & Problem Statement

A document is found only by its exact ID. Renaming a capability, story, architecture document, milestone or any other
ID-bearing document, or merging two of them, breaks every reference written with the old ID: `RULE-document-reference`
reports each one as unresolved, and `devkit spec resolve <old-id>` finds nothing. The only rename handled today is the
handed-off `PROP-<slug>` to `SPEC-<slug>` rewrite of the proposals lifecycle.

## 2. Decision Drivers

- A rename must not break references, and current documents must converge on the canonical ID.
- Relation fields are typed by the prefix written in them (`stories` takes `US-` IDs), so an alias must not change
  the kind a reference appears to have.
- Every identity check must agree on what an ID resolves to; a fallback in one caller leaves the others failing.
- One specification for every ID-bearing kind: a rule that depends on the kind is a second concept to learn.
- Records are never rewritten: historical files, and decision records that name a retired ID on purpose.
- No existing ADR file is edited by this work; refactoring or compacting the ADR ledger is out of scope.

## 3. Considered Options

1. **Exact IDs only**: the present state; a rename means editing every reference by hand.
2. **ADR-only aliases tied to deletion-based compaction**: withdrawn with the compaction direction in this Planning.
3. **Aliases on selected kinds only** (`CAP`, `US`, `ARCH`, `MS`), refusing `ADR`, `MAT` and the lifecycle kinds:
   rejected by the user; it ties the field to a per-kind list and leaves renamed decisions and materials without
   continuity.
4. **One aliases specification for every ID-bearing kind, resolved through one canonical mapping (chosen)**.

## 4. Decision Outcome

Option 4.

- **Kinds**: `aliases` is accepted on every ID-bearing document kind (`CAP`, `US`, `ARCH`, `ADR`, `MS`, `MAT`, `PROP`,
  `PADR`, `SPEC`, `PLAN`, `TASKS`, `REC`, `FB`; namespace documents included). No kind refuses it. A malformed field
  is a recorded issue that `RULE-document-reference` reports with its identity checks.
- **Where a kind has a gap**: alias shape issues and collisions are identity checks, run over every indexed document
  as the duplicate-ID check is, so a material's aliases are validated. `RULE-document-reference` does not check the
  references written inside materials, so such a reference (alias or not) is neither reported nor rewritten; a
  reference to a material's alias from a checked document resolves and is fixed like any other. Approved ADRs are
  append-only, so an ADR normally gains aliases when it is created (from its PADR, see Handoff), and an alias
  reference inside an ADR stays as written.
- **Shape**: a list of full IDs with the declaring document's own prefix, never its own ID, no item repeated, never a
  legacy date- or number-based form (the pattern `RULE-id-convention` reports, so the two rules never disagree).
  `aliases` entries are identity, not references: not a relation field, not counted as incoming references and never
  rewritten.
- **Precedence and collisions**: a declared ID always wins. An alias resolves only when exactly one document declares
  it and no document has it as its ID. Otherwise the collision is reported on every document involved, the target
  resolves as it would without the alias (or stays ambiguous), and `devkit rules fix` leaves the reference unchanged.
- **One canonical mapping**: `DocumentIndex` keeps the aliases beside the IDs and offers one mapping from a written
  target to its canonical document and whether an alias was used. `resolve()` itself uses it, as do `incoming()`,
  the `depends_on` cycle graphs, milestone membership in hygiene, the traceability reverse-link comparison, `refs`
  grouping and every caller that reads `by_id` or compares against `.id`. The devkit-agt rules catalog stays exact-ID.
- **Renaming**: a document whose ID derives from its path is renamed by moving the file, setting the new ID and
  keeping the old ID in `aliases`; renaming a spec bundle keeps an alias on every file whose ID derives from the
  bundle slug (`spec.md`, `plan.md`, `tasks.md`, `reconcile.md`). `CAP-DOCS-document-model` states the procedure.
- **References**: an alias reference resolves. In a current document it is an error that `devkit rules fix` rewrites
  to the canonical ID (frontmatter and prose, through the existing rewrite service). In historical files (completed
  spec bundles, done or dropped milestones) and in decision records (ADRs under `docs/decisions/` and PADRs, which
  graduate into ADRs) it resolves silently and `devkit rules fix` never rewrites it, so a record that names the
  retired ID as history keeps its meaning. (Decision records: replaced by `ADR-immutable-decisions-editable-records`,
  which rewrites alias references in ADRs and PADRs too.) A glossary Owner naming an alias is reported but not fixed.
- **Handoff**: carried aliases follow their document's handoff rename: a proposal's `PROP-` aliases become `SPEC-`
  aliases on `spec.md`, a promoted PADR's `PADR-` aliases become `ADR-` aliases on its ADR. A reference written with
  a carried alias is rewritten exactly like one written with the old ID, across the handoff's existing scan set (ADRs
  included, completed bundles excluded), because the translation removes the alias's only declaration; this is the
  handoff's own rename, not a `devkit rules fix` rewrite. The handoff refuses, before writing, when a graduating
  `ADR-<slug>` or `SPEC-<slug>`, or a translated alias, equals an existing ID or alias or another one graduating in
  the same handoff; scaffolding and the `PROP`/`SPEC` slug-pair check treat a `SPEC-<slug>` alias like a declared
  `SPEC-<slug>`, so the clash surfaces before Planning.
- **Output**: `devkit spec resolve <alias>` prints the canonical document with `alias=<alias>` in its `[DOCUMENT]`
  sentinel and an `alias` field in JSON; no notice is emitted. `devkit spec refs <canonical> --direction in` includes
  alias-written references, and `--direction out` groups an alias and its canonical ID as one target.
  `devkit spec search` pins an exact alias match like an exact ID.

## 5. Consequences

- A rename keeps the old ID in `aliases`, and one `devkit rules fix` moves current documents to the new ID.
- The handoff gains alias translation and an alias clash check (`CAP-DLV-proposal-incubation`).
- Aliases are identifiers, not search keywords; the playbook field of the same name follows this meaning
  (`ADR-playbook-aliases-as-identifiers`).
- ADR supersession stays as it is, and no file under `docs/decisions/` is edited by this work.
