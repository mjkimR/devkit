---
id: CAP-DOCS-document-model
title: Document Model
summary: "Defines Markdown document identity, references and indexing, including typed direct unit prerequisites, terminal completed targets and proposal-only milestone membership and plain body closure assertions."
area: documents
status: active
usecases:
  - UC-find-the-right-documents
  - UC-keep-the-living-spec-consistent
entrypoints:
  - packages/devkit-spec/src/devkit_spec/features/documents/
created_at: 2026-10-13
---

# [CAP-DOCS-document-model] Document Model

## 1. Summary

The document model decides which files are spec documents, how each one is identified and how documents reference
each other. `devkit_spec.features.documents` implements it as a workspace index rebuilt from the files on every load. The
lookup commands (`CAP-DOCS-document-lookup`), document search (`CAP-DOCS-document-search`), namespaces
(`CAP-DOCS-namespaces`) and spec rules (`CAP-GOV-spec-rules`) resolve document identities through this index.
`RULE-document-reference` also reads root glossary Owner cells through the rules workspace cache; the glossary
stays ID-free and unindexed, and its Owner references do not become graph edges.

## 2. Scope & Boundary

- **In-Scope**:
  - What a document is: location, frontmatter identity, exclusions.
  - The ID grammar and the kind each prefix names.
  - The reference forms (frontmatter relation fields, prose ID spans and brackets) and what prose excludes.
  - The `proposal`, `decomposed_from` and `supersedes` provenance fields.
  - Historical documents (completed spec bundle files except feedback, and done/dropped milestones).
  - The `summary` field as data of the model.
  - Document ID aliases (`aliases`): shape, precedence, collisions and the canonical mapping
    (`ADR-document-id-aliases`), and the rename procedure.
  - The index: loading, invalid files, ID and alias resolution, incoming and outgoing references, in-place
    rewriting.
- **Out-of-Scope** (Non-Goals):
  - Path and naming conventions per kind (dated partitions, `CAP-<AREA>-<slug>` stems, arc42 chapters). Scope
    Excluded: the index accepts any well-formed ID wherever it is declared. Rationale: conventions are checked and
    fixed by `RULE-id-convention` (`CAP-GOV-spec-rules`), which can report a misplaced file instead of hiding it.
  - Validity of references (unresolved, duplicated, wrong kind). Scope Excluded: the parser records references and
    skips malformed fields; `RULE-document-reference` reports them.
  - Namespace membership: `CAP-DOCS-namespaces`.
  - A persistent cache or database of documents. Scope Excluded: there is no second source of truth that can go stale.

## 3. Business Rules & Policies

### 3.1 Documents

1. **Location**: A document MUST be a Markdown file (`*.md`) under `docs/` or `specs/` of the workspace root.
2. **Exclusions**: `README.md`, templates (`*-template.md`, `*_template.md`), files under a directory whose name
   starts with `.`, and symbolic links (files or directories) MUST NOT be indexed.
3. **Identity**: A file is a document only when its frontmatter declares a well-formed ID (section 3.2) in `id`, or
   in `reconcile_id` for a reconcile record. A file without frontmatter, without an ID, or with an ID outside the
   grammar is not a document (a README, a glossary, a guide) and is silently left out.
4. **Frontmatter grammar**: The frontmatter MUST follow devkit's grammar (`devkit_core.core.frontmatter`); `id`,
   `reconcile_id` and `status`, when present, MUST be strings. A file that cannot be read as UTF-8, or whose
   frontmatter breaks either requirement, MUST be left out of the index and reported as a `SPEC_DOCUMENT_INVALID`
   warning; every other document MUST stay usable.
5. **Uniqueness**: IDs are repository-wide and MUST be unique across `docs/`, `specs/` and every namespace docs root.
   The index keeps every declaration of an ID, so a duplicate is detectable (`SPEC_ID_DUPLICATE`). Aliases share
   this namespace (section 3.5).
6. **Summary**: `summary` is one or two English sentences saying what the document defines. It is REQUIRED on
   capabilities, use cases, decisions, architecture documents, milestones, `proposal.md` and `spec.md` (`RULE-document-summary`)
   and is the main signal of document search (`CAP-DOCS-document-search`). Titles and bodies MAY use any language.
7. **Historical documents**: The files of a spec bundle (`specs/<YYYY-MM>/<bundle>/...`) whose `spec.md` has
   `status: completed` are historical: work history kept in place. Browsing and search MUST hide them unless
   `--history` is passed; the rules check them only when they are named as explicit targets. The bundle's
   `feedback/` directory is the exception: observations may remain open after the bundle completes,
   so feedback of every status MUST stay current whatever the bundle's status (`SPEC-open-feedback-and-progress`). Milestones whose status is done or dropped are also historical: hidden from browsing/search by default, resolvable and available with `--history`; rules check them only when explicitly targeted. A user-decided merge into a broader theme milestone MAY delete one; its ID then resolves as an alias of the theme (`ADR-milestone-merging`).

Proposal-local feedback also stays current while a rejected proposal awaits cleanup. Handoff carries open feedback
into the spec; Host deletion without handoff preserves it in the month-level backlog
(`CAP-DLV-proposal-incubation`). Existing discovery, resolution and namespace rules apply before and after moves.

### Milestone completion assertions

Milestone bodies carry a `Completion review` section with exactly two plain assertions:
`Decomposition: pending` and `Direct proposal work: pending`. A current user-owned Backlog close decision writes
both as confirmed with status done in one commit. Missing assertions on open documents mean unconfirmed; stored
assertions alone do not authorize a later close. These are body content, not parsed fields, checklist items,
reference edges or a machine-certified delivery contract. Actual semantic scope changes reset both to pending; normal handoff does not;
existing done records remain historical without migration. `CAP-HARN-agent-guidance` owns review, invalidation,
interruption and reopen procedures (`ADR-roadmap-and-milestones`).

### Feedback lifecycle

Feedback status is `open`, `promoted`, `resolved`, `dismissed` or `forwarded`
(`ADR-feedback-lifecycle`). Only open feedback is actionable. Promotion closes feedback by handing it to
identified follow-up work, whose progress is tracked at the destination; it never implies implementation success.
Resolution closes an observation directly fixed and verified without promotion, by a session or spec task. Both
are terminal: completing promoted work does not convert its source to resolved. Dismissal records a reason and
forwarding requires an actual authorized submission.

Capture writes open observations and never changes status. Completion resolves only explicitly linked open
sources directly addressed and verified, with outcome and evidence in their Disposition. Partial or unverified
direct fixes stay open. Terminal references require no completion update. Generic list/status filters discover
all states; use `--status open` for the actionable backlog. Spec completion never closes feedback automatically.

### 3.2 IDs and Kinds

An ID is `<PREFIX>-<slug>`: one of the prefixes below, a dash, then a letter or digit followed by letters, digits,
`_` and `-`. The prefix names the kind. The location column is where `RULE-id-convention` requires the document to
live; the index itself does not check it.

| Prefix | Kind | Location (checked by the rules) |
| --- | --- | --- |
| `CAP` | `capability` | `docs/capabilities/<area>/CAP-<AREA>-<slug>.md` |
| `UC` | `usecase` | `docs/usecases/<area>/UC-<slug>.md` |
| `ARCH` | `architecture` | `docs/architecture/ARCH-[<NN>[-<n>]-]<slug>.md` |
| `ADR` | `decision` | `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md` |
| `PROP` | `proposal` | `docs/proposals/...` |
| `PADR` | `proposal-decision` | `docs/proposals/...` |
| `SPEC`, `PLAN`, `TASKS`, `REC` | `spec`, `plan`, `tasks`, `reconcile` | `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/{spec,plan,tasks,reconcile}.md` |
| `FB` | `feedback` | `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/feedback/<slug>.md`, `specs/<YYYY-MM>/feedback/<YYYYMMDD>-<slug>.md`, `docs/proposals/PROP-<slug>/feedback/<slug>.md` |
| `MAT` | `material` | `docs/materials/...` |
| `MS` | `milestone` | `docs/roadmap/MS-<slug>.md` (global only) |

The table order is the kind order: `devkit spec list` sorts by it. Living Spec documents of a namespace live under
`docs/packages/<name>/` with the same layout (`CAP-DOCS-namespaces`).

### 3.3 References

1. **Full IDs only**: A document MUST reference another by its full ID, never by a Markdown path.
2. **Relation fields** (frontmatter): `usecases`, `capabilities`, `related_usecases`, `related_capabilities` hold a list
   of IDs; `spec` and `plan` hold one ID. Proposal anchors may declare `milestone`, one MS ID; SPEC milestone metadata is ignored and yields no membership reference. Milestones may declare `depends_on`, a list of MS IDs; proposal/spec anchors may declare a list of exact PROP/SPEC anchor IDs. Omit an empty optional field; an explicit empty list is valid. Auxiliary documents cannot declare unit prerequisites. Completed SPEC targets remain resolvable and are terminal for unit cycle traversal; the MS and unit graphs stay separate. A field of the wrong shape (a scalar where a list is expected, a non-string
   item) is recorded as an issue and skipped; `RULE-document-reference` reports it.
3. **Prose references**: a single-backtick code span holding exactly one ID (the canonical form) or the same ID in
   square brackets (the bracket form, which `devkit rules fix` converts to the canonical form).
4. **Prose exclusions**: fenced code blocks (a run of three or more backticks or tildes indented at most three
   spaces, closed by a run of the same character at least as long), lines indented four or more spaces, HTML
   comments, backslash escapes, every other inline code span, `~~strikethrough~~`, and link or image labels
   (`[label](...)`, `[label][ref]`, `[label]:`, `![alt]`) MUST NOT yield references. An inline span may continue on
   the following lines of its paragraph; an opener nothing closes is literal text.
5. **Self heading**: on a heading line starting with `# `, the document's own ID (the `# [<ID>] Title` token) is not a
   reference.
6. **Provenance**: `proposal` (the proposal a spec was handed off from), and `decomposed_from`/`supersedes` on Unit anchors, are provenance, not current references. They are kept apart from the reference graph: `refs` does not show them and reference rules do not require their sources to exist. New origin fields are scalar PROP IDs; wrong shapes and kinds are errors.
7. **Positions**: every reference MUST keep its field (`body` for prose), its 1-based line and column, and the
   character offsets of the ID in the file (quotes included for a quoted frontmatter value), so a fix rewrites
   exactly what was read and nothing else.

### 3.4 Index

1. **Rebuilt per load**: `DocumentIndex.load` walks `docs/` and `specs/` (sorted, symbolic links skipped) or reads the
   file list a caller supplies; the rules supply the run's workspace cache, so a snapshot run (`check --staged`,
   `--ci`) indexes the snapshot and a fix is seen by the recheck.
2. **Parse reuse**: a parsed document is reused while its path and text are unchanged, so the rules of one run parse
   every file once.
3. **Resolution**: resolving an ID MUST go through the canonical mapping (section 3.5) and return the one document
   it names, else raise `SPEC_ID_UNRESOLVED` (no document) or `SPEC_ID_DUPLICATE` (several declare the ID, or
   several declare the alias; `[TARGET]` lists their paths).
4. **Reference queries**: outgoing references are grouped by canonical target ID (an alias with its document) and
   incoming references, written with the document's ID or a resolving alias, by source ID, both in ID order. A target
   that no single document declares stays in the result (a dangling or ambiguous reference).
5. **Rewriting**: `rewrite` replaces only parsed references whose target a mapping names, never other occurrences
   of the ID. A quoted frontmatter value keeps its quote style; a bracket reference becomes a code-span reference
   (mapping an ID to itself converts the notation only).

### 3.5 Aliases

1. **Field**: any ID-bearing document (`CAP`, `UC`, `ARCH`, `ADR`, `MS`, `MAT`, `PROP`, `PADR`, `SPEC`, `PLAN`,
   `TASKS`, `REC`, `FB`; namespace documents included) MAY declare `aliases`, a list of previous or alternate IDs of
   itself. No kind refuses it.
2. **Shape**: each item MUST be a full ID with the declaring document's own prefix, MUST NOT be its own ID, MUST NOT
   repeat, and MUST NOT have a legacy date- or number-based form (the forms `RULE-id-convention` reports). A
   malformed field or item is left out of the index and recorded as an identity issue that `RULE-document-reference`
   reports on every document, materials and completed specs included.
3. **Identity, not reference**: `aliases` is not a relation field. Its entries are not references, are not counted as
   incoming references and are never rewritten.
4. **Canonical mapping**: `DocumentIndex.canonical` maps a written target to its document and the alias used. A
   declared ID always wins; an alias resolves only when exactly one document declares it and no document has it as
   its ID. Otherwise the alias collides: the collision is reported on every document involved, and the target
   resolves as it would without the alias, or stays ambiguous. Resolution, reference queries, the `depends_on` cycle
   graphs, milestone membership, traceability and every identity check use this mapping.
5. **Renaming**: a document whose ID derives from its path (`CAP`, `UC`, `ARCH`, `SPEC`, `PLAN`, `TASKS`, `REC`,
   `FB`) is renamed by moving the file, setting the new ID and keeping the old ID in `aliases`; renaming a spec bundle
   keeps an alias on every file whose ID derives from the bundle slug (`spec.md`, `plan.md`, `tasks.md`,
   `reconcile.md`). An ADR gains aliases from its PADR at handoff (`CAP-DLV-proposal-incubation`) or, as a compaction
   replacement, lists the IDs of the ADRs it retires (`ADR-immutable-decisions-editable-records`). One `devkit rules fix` then moves current documents to the new ID.
6. **Declaration across contracts**: wherever another contract refuses or reports an ID that a document declares (a
   taken spec or proposal slug, a duplicate PADR, a graduating ADR), an alias declaration counts as a declaration;
   wherever a command takes an ID argument that it resolves through the index (`devkit spec resolve`, `refs`,
   `entrypoints --target`, `proposal new --milestone`), an alias resolves to its canonical document.

## 4. Interfaces & Data Contracts

### 4.1 Frontmatter Fields Read by the Model

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | The document ID. |
| `reconcile_id` | string | The ID of a reconcile record (used when `id` is absent). |
| `status` | string | Lifecycle status; `completed` on a `spec.md` makes its bundle historical, its feedback aside. |
| `title` | string | Display title (any language). |
| `summary` | string | One or two English sentences; embedded by search. |
| `area` | string | Area of a capability or use case (its directory). |
| `usecases`, `capabilities`, `related_usecases`, `related_capabilities` | list of IDs | Relation fields. |
| `spec`, `plan` | ID | Relation fields. |
| `proposal` | ID | Provenance of a handed-off spec. |
| `aliases` | list of IDs | Previous or alternate IDs of the document itself (section 3.5); identity, not references. |
| `namespace` | string | Namespace of a spec or proposal bundle (`CAP-DOCS-namespaces`). |
| `entrypoints` | list of paths | Code entrypoints of a capability or use case (`CAP-TRACE-code-entrypoints`). |

### 4.2 Document Record (JSON)

Commands that print documents in JSON use the record `id`, `kind`, `path` (workspace-relative), `status`, `title`,
`area`, `summary`; an absent or non-string value is `""`. A reference is `target`, `source`, `path`, `field`, `line`,
`column`, `bracket` (`true` for the bracket form).

### 4.3 Error Codes

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `SPEC_DOCUMENT_INVALID` | `WARNING` | `DocumentInvalidWarning` | A file under `docs/` or `specs/` cannot be read as UTF-8 or has malformed frontmatter (including a non-string `id`, `reconcile_id` or `status`); it is left out of the index. Returned under `notices`; exit `0`, `1` under `--strict`. |
| `SPEC_ID_UNRESOLVED` | `ERROR` (`INPUT_ERROR`) | `UnresolvedIdError` | No document declares the ID. |
| `SPEC_ID_DUPLICATE` | `ERROR` (`MAINTENANCE`) | `DuplicateIdError` | More than one document declares the ID, or (no document declaring it as its ID) the alias; `[TARGET]` lists them. |

### 4.4 Library

```python
from devkit_spec.features.documents import DocumentIndex, Kind, is_id, kind_of, rewrite

index = DocumentIndex.load(root)  # documents, by_id, by_alias, problems (SPEC_DOCUMENT_INVALID), historical
document = index.resolve("CAP-CORE-search")  # an ID or an alias; UnresolvedIdError, DuplicateIdError
document, alias = index.lookup("CAP-CORE-old")  # alias is None for a declared ID
index.canonical("CAP-CORE-old")  # (document, alias) or None when no document or several match
index.canonical_id("CAP-CORE-old")  # the canonical ID, else the written value
index.alias_collisions()  # [(alias, [every document involved]), ...]
index.outgoing(document)  # {canonical target ID: [Reference, ...]}
index.incoming(document.id)  # {source ID: [Reference, ...]}, alias-written references included
index.is_historical(document)  # a file of a completed spec bundle outside its feedback/
```

`parse_document(path, text)` reads one document (`None` without a well-formed ID); `visible_lines` is the prose
scanner behind reference extraction; `SOURCE_DIRECTORIES`, `is_document_file` and `in_source_directory` expose the
file selection.
