---
id: CAP-DOCS-document-model
title: Document Model
summary: "Markdown identity, references, indexing and parsing, including flat terminal milestone storage, and the independent docs bundle of shared formats, writing guidance and document rules."
area: documents
status: active
usecases:
  - UC-find-the-right-documents
  - UC-keep-the-living-spec-consistent
entrypoints:
  - packages/devkit-docs/src/devkit_docs/features/documents/
  - packages/devkit-core/src/devkit_core/core/frontmatter.py
  - packages/devkit-core/src/devkit_core/core/yaml.py
  - packages/devkit-docs/src/devkit_docs/bundles/docs/bundle/bundle.toml
created_at: 2026-10-13
---

# [CAP-DOCS-document-model] Document Model

## 1. Summary

The document model decides which files are spec documents, how each one is identified and how documents reference
each other. The devkit-docs wheel owns it (`ADR-document-package`): `devkit_docs.features.documents` implements it
as a workspace index built from the files on every load, reusing a file's parse result, also between processes, only
while its path and text are unchanged. The lookup commands (`CAP-DOCS-document-lookup`), document search (`CAP-DOCS-document-search`), namespaces
(`CAP-DOCS-namespaces`) and spec rules (`CAP-GOV-spec-rules`) resolve document identities through this index.
`RULE-document-reference` also reads root glossary Owner cells and the IDs cited in steering files through the rules
workspace cache; these files stay ID-free and unindexed, and their references do not become graph edges.

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
  - A persistent source of truth for documents. Scope Excluded: the files are the only input to a load; the parse
    memo (section 3.4) keeps derived parse results keyed by each file's text and never decides which files exist or
    what they hold (`ADR-content-keyed-document-parse-memo`).

## 3. Business Rules & Policies

### 3.1 Documents

1. **Location**: A document MUST be a Markdown file (`*.md`) under `docs/` or `specs/` of the workspace root.
2. **Exclusions**: `README.md`, templates (`*-template.md`, `*_template.md`), files under a directory whose name
   starts with `.`, and symbolic links (files or directories) MUST NOT be indexed.
3. **Identity**: A file is a document only when its frontmatter declares a well-formed ID (section 3.2) in `id`, or
   in `reconcile_id` for a reconcile record. A file without frontmatter, without an ID, or with an ID outside the
   grammar is not a document (a README, a glossary, a guide) and is silently left out.
4. **Frontmatter grammar**: The frontmatter MUST follow devkit's grammar (`devkit_core.core.frontmatter`) and
   MUST be parsed through the shared LibYAML safe boundary (`devkit_core.core.yaml`). The parser preserves Python
   value types and rejects duplicate keys. `id`, `reconcile_id` and `status`, when present, MUST be strings. A file
   that cannot be read as UTF-8, or whose frontmatter breaks either requirement, MUST be left out of the index and
   reported as a `DOCS_DOCUMENT_INVALID` warning; every other document MUST stay usable. Parser marks, when
   available, MUST be reported as 1-based document lines and columns. IF the PyYAML LibYAML binding is unavailable,
   THEN a YAML-reading operation MUST fail with `YAML_BINDING_UNAVAILABLE` and exit `2` before reusing a memoized
   parse result; it MUST NOT fall back to Python parsing or report the binding failure as `DOCS_DOCUMENT_INVALID`.
   These contracts are verified by `packages/devkit-core/tests/unit/core/test_frontmatter.py` and
   `packages/devkit-docs/tests/integration/features/documents/test_memo_index.py`.
5. **Uniqueness**: IDs are repository-wide and MUST be unique across `docs/`, `specs/` and every namespace docs root.
   The index keeps every declaration of an ID, so a duplicate is detectable (`DOCS_ID_DUPLICATE`). Aliases share
   this namespace (section 3.5).
6. **Summary**: `summary` is one or two English sentences saying what the document defines. It is REQUIRED on
   capabilities, use cases, UX documents, decisions, architecture documents, milestones, `proposal.md` and `spec.md` (`RULE-document-summary`)
   and is the main signal of document search (`CAP-DOCS-document-search`). Titles and bodies MAY use any language.
7. **Historical documents**: The files of a spec bundle (`specs/<YYYY-MM>/<bundle>/...`) whose `spec.md` has
   `status: completed` are historical: work history kept in place. Browsing and search MUST hide them unless
   `--history` is passed; the rules check them only when they are named as explicit targets. The bundle's
   `feedback/` directory is the exception: observations may remain open after the bundle completes,
   so its feedback MUST NOT become historical through the bundle's status (`SPEC-open-feedback-and-progress`); open
   feedback stays current, and feedback of a terminal status is historical by rule 8. Milestones whose status is done or dropped are also historical: hidden from browsing/search by default, resolvable and available with `--history`; rules check them only when explicitly targeted. A user-decided merge into a broader theme milestone MAY delete one; its ID then resolves as an alias of the theme (`ADR-milestone-merging`).
8. **Terminal statuses**: a document whose own status is terminal for its kind, compared case-insensitively, is
   historical for browsing and search whatever bundle holds it: feedback `resolved`, `promoted`, `dismissed` and
   `forwarded`, decision `superseded`, proposal `rejected` (`ADR-terminal-statuses-are-historical`). Browsing and
   search MUST hide it unless `--history` is passed (or `list --status` names its status, `CAP-DOCS-document-lookup`);
   its ID stays resolvable and its references queryable. Unlike rule 7, the rules keep checking it on every run.

9. **Steering documents**: `docs/steering/` holds project-wide background that is neither a contract nor evidence
   (`ADR-steering-documents-directory`): one Markdown file per topic directly in the directory, with only `title` and
   `summary` frontmatter and no `id`, so by rule 3 none is a document, and none is a search candidate. The glossary
   (`glossary.md`, with the search synonyms `glossary.yaml`) is its first member. There is no namespace copy; a
   package glossary stays at `docs/packages/<name>/glossary.md`. `devkit get-context spec` lists every steering file's
   `title` and `summary` (`CAP-DIST-context-and-playbooks`), `RULE-steering-documents` bounds the directory and
   `RULE-document-reference` resolves the IDs it cites (`CAP-GOV-spec-rules`).

Proposal-local feedback also stays current while a rejected proposal awaits cleanup. Handoff carries open feedback
into the spec; Host deletion without handoff preserves it in the month-level backlog
(`CAP-DLV-proposal-planning`). Existing discovery, resolution and namespace rules apply before and after moves.

### Milestone placement

Global planned/active milestones MUST use the roadmap root; done/dropped MUST use its one flat `_archive/`
directory with the same filename, ID and aliases (`ADR-archive-terminal-milestones-in-roadmap`).
Other nesting and namespace roadmaps are invalid. Placement creates no new status or registry.
The index MUST retain invalid archived live documents so governance can report their placement.
Existing lookup, alias, reference and status-derived history semantics apply across both locations.
Checks: `RULE-id-convention`, `test_milestones.py`.

### Milestone completion assertions

Milestone bodies carry a `Completion review` section with exactly two plain assertions:
`Decomposition: pending` and `Direct proposal work: pending`. A current user-owned Backlog close decision writes
both as confirmed with status done in one commit. Missing assertions on open documents mean unconfirmed; stored
assertions alone do not authorize a later close. These are body content, not parsed fields, checklist items,
reference edges or a machine-certified delivery contract. Actual semantic scope changes reset both to pending; normal handoff does not;
existing done records retain their historical assertions during content-preserving archive moves. `CAP-HARN-agent-guidance` owns review, invalidation,
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
| `UX` | `ux` | `docs/ux/<area>/UX-<slug>.md` |
| `ARCH` | `architecture` | `docs/architecture/ARCH-[<NN>[-<n>]-]<slug>.md` |
| `ADR` | `decision` | `docs/decisions/<YYYY-MM>/<YYYYMMDD>-<slug>.md` |
| `PROP` | `proposal` | `docs/proposals/...` |
| `PADR` | `proposal-decision` | `docs/proposals/...` |
| `SPEC`, `PLAN`, `TASKS`, `REC` | `spec`, `plan`, `tasks`, `reconcile` | `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/{spec,plan,tasks,reconcile}.md` |
| `FB` | `feedback` | `specs/<YYYY-MM>/<YYYYMMDD>-<slug>/feedback/<slug>.md`, `specs/<YYYY-MM>/feedback/<YYYYMMDD>-<slug>.md`, `docs/proposals/PROP-<slug>/feedback/<slug>.md` |
| `MAT` | `material` | `docs/materials/...` |
| `MS` | `milestone` | `docs/roadmap/MS-<slug>.md` (planned/active) or `docs/roadmap/_archive/MS-<slug>.md` (done/dropped), global only |

The table order is the kind order: `devkit docs list` sorts by it. Living Spec documents of a namespace live under
`docs/packages/<name>/` with the same layout (`CAP-DOCS-namespaces`).

The kind definition table in the documents models is the single definition of kinds
(`ADR-kind-definition-table-keyed-on-the-declared-kind-enum`): one row per `Kind` member, in the order above, holds
the prefix and the per-kind facts the index and the rules read (its directory, Living Spec membership, area scoping,
the `RULE-spec-format` scope, whether a first H1 carries an ID token, the summary requirement, whether it bears
`entrypoints`, its terminal statuses, its fix-time default status and the relation fields that take its IDs). The
ID pattern and prefix map derive from the rows. A table with a missing, extra or reordered row, a prefix or relation
field in two rows, or an inconsistent row MUST fail with `KindTableError`; a consumer that lacks a fact a kind needs
MUST fail the same way instead of applying another kind's. Path grammars and lifecycles stay kind-specific code.

The `ux` row (`ADR-ux-screen-documents`) is a Living Spec, area-scoped kind with an always-required summary, a heading
token, no `entrypoints`, no terminal status (statuses `draft`, `active`, `deprecated`) and no relation field that
takes its IDs: a use case cites a UX ID in step prose, and `RULE-ux-links` and `RULE-ux-coverage` check those
citations against the UX document's Interactions table (`CAP-GOV-spec-rules`).

### 3.3 References

1. **Full IDs only**: A document MUST reference another by its full ID, never by a Markdown path.
2. **Relation fields** (frontmatter): `usecases`, `capabilities`, `related_usecases`, `related_capabilities` hold a list
   of IDs; `spec` and `plan` hold one ID. A UX document declares `usecases` (the use cases whose steps cite it) and
   `capabilities` (the capabilities whose state or operations it presents), and a scalar `element` (`screen`, `modal`
   or `panel`) that is not a reference. Proposal anchors may declare `milestone`, one MS ID; SPEC milestone metadata is ignored and yields no membership reference. Milestones may declare `depends_on`, a list of MS IDs; proposal/spec anchors may declare a list of exact PROP/SPEC anchor IDs. Omit an empty optional field; an explicit empty list is valid. Auxiliary documents cannot declare unit prerequisites. Completed SPEC targets remain resolvable and are terminal for unit cycle traversal; the MS and unit graphs stay separate. A field of the wrong shape (a scalar where a list is expected, a non-string
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

1. **Built per load**: `DocumentIndex.load` MUST walk `docs/` and `specs/` (sorted, symbolic links skipped) or read
   the file list a caller supplies, read every file, and build the ID and alias maps, historical documents, problems
   and order from those files on every load. The rules supply the run's workspace cache, so a snapshot run
   (`check --staged`, `--ci`) indexes the snapshot and a fix is seen by the recheck.
2. **Parse reuse**: a file's parse result MUST be reused only for the same workspace-relative path and the exact text
   the reader returned; within a process this makes the rules of one run parse every file once.
3. **Parse memo**: WHERE `<root>/.devkit/transient/` is a directory, the index MUST keep parse results between
   processes in `<root>/.devkit/transient/docs/document-index.json`, each entry keyed by the path and the BLAKE2b
   digest of the UTF-8 encoding of the text parsed, the whole file under a parser fingerprint (the format version,
   the source of the read, parse and codec modules, the PyYAML version, libyaml presence and the Python version)
   (`ADR-content-keyed-document-parse-memo`, `ADR-parse-memo-location-and-format`). A stored result is a document,
   "no document", a malformed-frontmatter reason or an "unstorable" marker; a file that cannot be read or decoded
   has no entry. The memo is not used when a symbolic link is at `.devkit/transient/`, `docs/` or the file, or the
   file resolves outside the root. Deleting the file is always safe: the next load rebuilds it.
4. **Memo writes**: only a load that walks the workspace with the default reader MUST write the memo, and only when
   its entries differ from those it read (a new, changed or removed file, or a discarded memo), by atomic replace
   without a lock; a load with a supplied file list or reader reads the memo and never writes it
   (`ADR-parse-memo-failure-and-write-policy`).
5. **Memo silence**: IF the memo is unreadable, malformed, of another version or fingerprint, holds an entry
   that cannot be rebuilt, is a non-regular file or cannot be written, THEN the index MUST return a fresh build's
   result with no advisory, notice or exit-status change, logging one line visible under `-v`; a non-regular file
   at the memo path is never removed or replaced. A missing memo is created without a log line
   (`packages/devkit-docs/tests/integration/features/documents/test_memo_index.py`).
6. **Resolution**: resolving an ID MUST go through the canonical mapping (section 3.5) and return the one document
   it names, else raise `DOCS_ID_UNRESOLVED` (no document) or `DOCS_ID_DUPLICATE` (several declare the ID, or
   several declare the alias; `[TARGET]` lists their paths).
7. **Reference queries**: outgoing references are grouped by canonical target ID (an alias with its document) and
   incoming references, written with the document's ID or a resolving alias, by source ID, both in ID order. A target
   that no single document declares stays in the result (a dangling or ambiguous reference).
8. **Rewriting**: `rewrite` replaces only parsed references whose target a mapping names, never other occurrences
   of the ID. A quoted frontmatter value keeps its quote style; a bracket reference becomes a code-span reference
   (mapping an ID to itself converts the notation only).

### 3.5 Aliases

1. **Field**: any ID-bearing document (`CAP`, `UC`, `UX`, `ARCH`, `ADR`, `MS`, `MAT`, `PROP`, `PADR`, `SPEC`, `PLAN`,
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
5. **Renaming**: a document whose ID derives from its path (`CAP`, `UC`, `UX`, `ARCH`, `SPEC`, `PLAN`, `TASKS`, `REC`,
   `FB`) is renamed by moving the file, setting the new ID and keeping the old ID in `aliases`; renaming a spec bundle
   keeps an alias on every file whose ID derives from the bundle slug (`spec.md`, `plan.md`, `tasks.md`,
   `reconcile.md`). An ADR gains aliases from its PADR at handoff (`CAP-DLV-proposal-planning`) or, as a compaction
   replacement, lists the IDs of the ADRs it retires (`ADR-immutable-decisions-editable-records`). One `devkit rules fix` then moves current documents to the new ID.
   The current documents it rewrites include ADRs and PADRs (`ADR-immutable-decisions-editable-records`) and the
   `feedback/` files of every spec bundle, whatever the bundle's or the feedback's status (section 3.1, rules 7 and
   8), so a rename's write scope owns every path that references the old ID except historical files (completed spec
   bundles outside `feedback/`, done or dropped milestones) and materials, which stay as written and resolve through
   the alias. `uv run devkit docs refs <old-id> --direction in -n 0` lists the referencing paths, those included.
   The same fix rewrites the old ID where an unindexed quick reference (`docs/development/`, `guides/`, package and
   tool READMEs by default; `CAP-GOV-spec-rules`) cites it in a code span, so only plain-text mentions, feedback
   `target` fields included, need a manual sweep (`rg <old-id>`). Because the fix rewrites every code-span alias, a
   rename spec writes the old IDs as plain text, never in a code span, in its mapping tables and prose, so its record
   keeps which IDs were renamed.
6. **Declaration across contracts**: wherever another contract refuses or reports an ID that a document declares (a
   taken spec or proposal slug, a duplicate PADR, a graduating ADR), an alias declaration counts as a declaration;
   wherever a command takes an ID argument that it resolves through the index (`devkit docs resolve`, `refs`,
   `entrypoints --target`, `proposal new --milestone`), an alias resolves to its canonical document.

## 4. Interfaces & Data Contracts

### 4.1 Frontmatter Fields Read by the Model

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | The document ID. |
| `reconcile_id` | string | The ID of a reconcile record (used when `id` is absent). |
| `status` | string | Lifecycle status; `completed` on a `spec.md` makes its bundle historical, its feedback aside; a terminal status makes the document historical for browsing (rule 8). |
| `title` | string | Display title (any language). |
| `summary` | string | One or two English sentences; embedded by search. |
| `area` | string | Area of a capability, use case or UX document (its directory). |
| `element` | string | What a UX document describes: `screen`, `modal` or `panel` (read by `RULE-ux-links`). |
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
| `DOCS_DOCUMENT_INVALID` | `WARNING` | `DocumentInvalidWarning` | A file under `docs/` or `specs/` cannot be read as UTF-8 or has malformed frontmatter (including a non-string `id`, `reconcile_id` or `status`); it is left out of the index. Returned under `notices`; exit `0`, `1` under `--strict`. |
| `YAML_BINDING_UNAVAILABLE` | `ERROR` (execution failure) | `YamlBindingUnavailableError` | A YAML read starts without PyYAML's `CSafeLoader`; exit `2` before parsing or memo reuse, and never as `DOCS_DOCUMENT_INVALID`. |
| `DOCS_ID_UNRESOLVED` | `ERROR` (`INPUT_ERROR`) | `UnresolvedIdError` | No document declares the ID. |
| `DOCS_ID_DUPLICATE` | `ERROR` (`MAINTENANCE`) | `DuplicateIdError` | More than one document declares the ID, or (no document declaring it as its ID) the alias; `[TARGET]` lists them. |

### 4.4 Library

```python
from devkit_docs.features.documents import DocumentIndex, Kind, is_id, kind_of, rewrite

index = DocumentIndex.load(root)  # documents, by_id, by_alias, problems (DOCS_DOCUMENT_INVALID), historical
document = index.resolve("CAP-CORE-search")  # an ID or an alias; UnresolvedIdError, DuplicateIdError
document, alias = index.lookup("CAP-CORE-old")  # alias is None for a declared ID
index.canonical("CAP-CORE-old")  # (document, alias) or None when no document or several match
index.canonical_id("CAP-CORE-old")  # the canonical ID, else the written value
index.alias_collisions()  # [(alias, [every document involved]), ...]
index.outgoing(document)  # {canonical target ID: [Reference, ...]}
index.incoming(document.id)  # {source ID: [Reference, ...]}, alias-written references included
index.is_historical(document)  # a completed bundle's file outside its feedback/, or a done/dropped milestone
index.is_terminal(document)  # its status is one of its kind's terminal_statuses in the kind table (rule 8)
index.is_browsing_historical(document)  # what list and search hide unless asked: either of the above
```

`definitions()` returns the kind table in kind order and `definition(kind)` one row (`KindDefinition`);
`relation_prefixes()` maps each relation field to the prefix it takes, `by_prefix(value)` returns the row whose
prefix opens `value` as `<PREFIX>-...`, and `KindTableError` reports an inconsistent table or a missing fact. A row's
`summary` is a `Summary` (`always`, `anchor`, `never`) and its `format_scope` a `FormatScope` (`none`, `global`,
`every-root`). `PREFIXES` and `TERMINAL_STATUSES` are copies of the rows taken at import.

`parse_document(path, text)` reads one document (`None` without a well-formed ID); `visible_lines` is the prose
scanner behind reference extraction; `SOURCE_DIRECTORIES`, `is_document_file` and `in_source_directory` expose the
file selection.

## Document asset distribution

The devkit-docs wheel MUST register the auto-selected `docs:core` bundle. It owns eight writing instructions,
nine document rule assets, five shared templates and the docs-pointer. Only docs declares the `docs/steering`
context directory. `devkit get-context docs` lists steering summaries and document instructions.
`docs:docs-skeleton` seeds absent files only when selected; seeded files remain project-owned.
The bundle introduces no SDD entry, approval, immutable ADR history or completed-artifact retention obligations.
The selected development approach owns those policies (`ADR-document-and-sdd-bundles`).
A clean document-only installation omits devkit-spec; deselecting spec assets does not disable installed extensions.
Tests: `packages/devkit-docs/tests/integration/bundles/docs/` and `packages/devkit-docs/tests/e2e/bundles/docs/`.
