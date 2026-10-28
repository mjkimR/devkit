---
id: CAP-DOCS-document-lookup
title: Document Lookup
summary: "Defines devkit docs resolve, refs and list: map IDs to paths, follow references both ways, and browse documents by kind, status (with a notice for an unused status), area, text, frontmatter field, history, namespace or owned code path, with feedback by severity, paging and JSON output."
area: documents
status: active
usecases:
  - UC-find-the-right-documents
entrypoints:
  - packages/devkit-docs/src/devkit_docs/features/documents/cli/commands.py
created_at: 2026-10-13
---

# [CAP-DOCS-document-lookup] Document Lookup

## 1. Summary

Three commands give an agent deterministic access to the document index (`CAP-DOCS-document-model`): `devkit docs
resolve` maps IDs to paths, `devkit docs refs` follows the references of one document in either direction, and
`devkit docs list` browses documents with filters. They are the exact-match counterpart of `devkit docs search`
(`CAP-DOCS-document-search`), which ranks by meaning when the ID is not known. Each call loads the index through
the parse memo of `CAP-DOCS-document-model` where the workspace has one (section 3.4 there), so a repeated call in an
unchanged workspace parses again only documents whose frontmatter holds a value the memo cannot store. The memo never
changes an argument, output, code or exit status.

## 2. Scope & Boundary

- **In-Scope**: `resolve`, `refs` and `list`: arguments, options, filters, ordering, paging, text sentinels, JSON
  keys, exit codes and error codes.
- **Out-of-Scope** (Non-Goals):
  - Ranking by meaning: `CAP-DOCS-document-search`.
  - Namespace semantics (membership, default selection): `CAP-DOCS-namespaces`; this capability only applies them.
  - Per-kind listing extras: filters by linked use case or capability (`--with-usecase`, `--with-cap`) and a `--sort`
    option. Scope Excluded: `list` filters by the generic fields and `--where` below; proposal priority and size,
    feedback severity, scope and kind are `--where` fields. When to Reconsider: when agents repeatedly combine
    `refs` and `list` by hand for one of these questions.
  - Comparison operators, substring or pattern matching in `--where`: it matches whole values.
  - Validating references: `RULE-document-reference` (`CAP-GOV-spec-rules`).

## 3. Business Rules & Policies

### 3.1 Common

1. **Workspace**: every command takes `-w/--workspace-root` (default: the devkit project containing the current
   directory), `--format text|json` and devkit's output options (`-q`, `-v`, `--strict`), as every `devkit docs`
   command does (`CAP-HARN-command-mount`). Paths in the output MUST be workspace-relative.
2. **Warnings and notices**: files the index left out are `DOCS_DOCUMENT_INVALID` warnings, and an unknown
   `list --status` value is a `DOCS_LIST_STATUS_UNKNOWN` notice (3.4); both go to stderr (under `notices` in JSON).
   They MUST NOT change the exit code, except a warning under `--strict`.
3. **Namespaces ignored for identity**: `resolve` and `refs` MUST resolve IDs repository-wide whatever namespace is
   selected; only `list` (and `search`) narrows by namespace.

### 3.2 `devkit docs resolve ID...`

1. Prints one `[DOCUMENT: ...]` line per resolved ID, in argument order. An ID argument may be an alias
   (`CAP-DOCS-document-model` section 3.5): the line names the canonical document and adds `alias=<alias>`; no notice
   is emitted.
2. Each unresolved or duplicated ID (a colliding alias included) MUST be reported as an error after the lines that
   did resolve (`DOCS_ID_UNRESOLVED`, `DOCS_ID_DUPLICATE`); the command then exits `2`.

### 3.3 `devkit docs refs ID`

1. `--direction out` (default) lists the documents ID references; `--direction in` the documents that reference ID.
2. One `[REF: <id> ...]` line per document on the other side, in ID order. `fields` lists where the references are
   (`body` or frontmatter field names, sorted, comma-separated), `count` how many references there are.
3. `path=-` and `status=-` mark an ID that no single document declares: a dangling reference, or a duplicated ID.
4. The `proposal` provenance field is not a reference and MUST NOT appear.
5. An unresolvable ID argument fails with `DOCS_ID_UNRESOLVED` or `DOCS_ID_DUPLICATE` (exit `2`); an alias argument
   names its document.
6. **Aliases**: `--direction in` includes references written with an alias that resolves to the document;
   `--direction out` groups a reference written with an alias under its canonical ID, as one target with the
   references written either way.

### 3.4 `devkit docs list [KIND]...`

1. **Kinds**: `KIND...` restricts to `capability`, `usecase`, `ux`, `architecture`, `decision`, `proposal`,
   `proposal-decision`, `spec`, `plan`, `tasks`, `reconcile`, `feedback`, `material`, `milestone` (default: all).
2. **Filters** (all combine with AND):
   - `--status/-s a,b`: comma-separated statuses, compared case-insensitively. A given `--status` replaces the default
     history hiding: the documents whose status it names are listed whatever their history. Status vocabularies
     come from the templates, which a project may override, so a value is never rejected: one that no indexed
     document of the selected kinds (every kind without `KIND`) carries as the status `list` shows (a status
     overlay's value where one applies, 3.6), historical or in another namespace included, adds one `DOCS_LIST_STATUS_UNKNOWN` notice naming those values, with the statuses that do occur in
     its `[FIX]` (`SPEC-list-unknown-status`). The filter still applies as given, so a valid status no document carries yet
     gives an empty page plus the notice.
   - `--area/-a TEXT`: case-insensitive substring of the frontmatter `area`.
   - `--query TEXT`: case-insensitive substring of the ID or the title.
   - `--where FIELD=VALUE[,VALUE...]` (repeatable): documents whose frontmatter `FIELD` holds one of the values. The
     field name is case-sensitive; values are compared case-insensitively after trimming against the parsed value:
     a scalar's text, `true`/`false` for a boolean, the ISO 8601 form of a date or timestamp, any scalar element of a
     list. A missing field, `null` or a mapping never matches. Each `--where` must match. An item without `=`, field
     or value MUST fail with `ARGUMENT_INVALID` (exit `2`, nothing on stdout).
   - `--history`: include historical documents: files of completed spec bundles, their feedback aside, done or
     dropped milestones, and documents of a terminal status (feedback `resolved`, `promoted`, `dismissed`,
     `forwarded`; decision `superseded`; proposal `rejected`; `CAP-DOCS-document-model` rules 7 and 8). Hidden by
     default whatever kinds are selected, so `list feedback` and `list feedback spec` select alike
     (`ADR-terminal-statuses-are-historical`). Historical IDs remain resolvable and their incoming membership
     remains queryable.
   - `--file PATH`: documents whose frontmatter `entrypoints` overlap the workspace-relative path: an entry equal to
     it, under it, or a directory containing it (whole path segments, case-sensitive; `CAP-TRACE-code-entrypoints`).
     The path need not exist, so a deleted file still finds its documents; a path that breaks the entrypoint path
     contract (absolute, a glob, a `..` segment) MUST fail with `DOCS_ENTRYPOINTS_PATH_INVALID` (exit `2`) before
     any document is read. Only capabilities and use cases declare `entrypoints`.
   - `--namespace NAME` / `--all-namespaces`: the namespace selection (`CAP-DOCS-namespaces`). Default: the namespace
     of the current directory plus the global documents.
3. **Order**: kind order (the table of `CAP-DOCS-document-model`), then, for feedback, `severity` (`critical`,
   `blocked`, `workaround`, `noise`, then any other or missing value, case-insensitive), then ID, then path.
4. **Line fields**: `kind`, `status`, `path`, the fields a status overlay adds (3.6), `tasks` (`<checked>/<total>` of the `tasks.md` beside a spec, counted
   as devkit counts checklist items; `-` for other kinds or without `tasks.md`), on proposal lines only `task_kind`,
   `planning_effort` and `dev_effort` (`-` when absent), on feedback lines only `severity`,
   `scope` and `target` (`-` when absent), `namespace` (only in a workspace that registers namespaces), `title`.

### 3.5 Paging (`refs`, `list`)

1. `--limit/-n` (default `20`, `0` for all) and `--offset` (default `0`). A negative value MUST fail with devkit's
   `ARGUMENT_INVALID`.
2. The output ends with `[PAGE: total= offset= limit= count= next=]`; `next` is the offset of the next page, `-` on
   the last one. `list` adds `hidden=<n>` last: the documents that match every other filter but were left out as
   historical (`0` with `--history` or `--status`).
3. When more items follow, `[NEXT_CMD: uv run devkit docs ...]` repeats the command with every given filter, `-w` when it
   was given, `--limit` and the next `--offset`; each `--where` is repeated as given, in order.
4. When `hidden` is above zero, `list` prints `[HISTORY_CMD: uv run devkit docs list ... --history]` last: the command with
   every given filter, `--history`, `-w` when it was given and `--limit` when it is not the default.

### 3.6 Status Overlays (`list`)

1. **Registration**: `list` MUST load every callable registered in the entry-point group `devkit.docs.status_overlay`,
   in entry-point name order (then value). Each is called as `overlay(root, documents)` and returns
   `{document ID: {field: text}}`.
2. **Shown status**: WHERE an overlay sets `status` for a document, `list` MUST show that value as the document's
   status and MUST apply `--status` and the `DOCS_LIST_STATUS_UNKNOWN` notice (3.4) to it.
3. **Extra fields**: every other field an overlay sets MUST be added to the document's line, after `path`, and to its JSON
   record.
4. **Precedence**: IF two overlays set the same field of one document, THEN the one loaded later MUST win.
5. **Reserved fields**: an overlay MAY set `status` but MUST NOT set a field `list` already shows (`id`, `kind`,
   `path`, `title`, `area`, `summary`, `namespace`, `historical`, `tasks`, the proposal fields and the feedback
   fields).
6. **Failure isolation**: IF an overlay fails to load, raises, returns anything other than a mapping of document IDs to
   mappings of text fields, or sets a reserved field, THEN `list` MUST leave that overlay's whole result out, add one
   `DOCS_OVERLAY_FAILED` warning naming it (`extension: <name>`), and still apply the other overlays and exit as
   without it.
7. **Display only**: an overlay MUST NOT write a document; `resolve`, `refs`, `search` and the rules read the
   declared status. Without a registered overlay, `list` shows the declared status.
8. **devkit-spec's overlay**: devkit-spec registers `spec =
   devkit_spec.features.proposals.services.planning:planning_overlay`: a `draft` proposal whose `plan-<slug>` branch
   exists, locally or fetched, is shown with `status=reviewing` and `planning_branch` (`CAP-DLV-proposal-incubation`
   rule 10, `ADR-document-package`).

## 4. Interfaces & Data Contracts

### 4.1 Usage

```bash
devkit docs resolve CAP-CORE-search UC-find-docs     # the path of each ID
devkit docs refs CAP-CORE-search                      # what it references
devkit docs refs CAP-CORE-search --direction in       # what references it
devkit docs list usecase --status active --area core  # browse
devkit docs list capability --file src/engine/        # documents owning a code path
devkit docs list spec --history --all-namespaces      # completed bundles too, every package
devkit docs list milestone --history                 # include done/dropped milestones
devkit docs list feedback --where severity=critical -n 0   # open critical feedback (settled ones are historical)
devkit docs list feedback --status resolved            # resolved feedback, without --history
```

### 4.2 Text Output

```text
[DOCUMENT: UC-find-docs kind=usecase status=active path=docs/usecases/core/UC-find-docs.md]
[REF: UC-find-docs path=docs/usecases/core/UC-find-docs.md status=active fields=body,usecases count=2]
[REF: UC-removed path=- status=- fields=body count=1]
[DOCUMENT: SPEC-search kind=spec status=draft path=specs/2026-10/20261002-search/spec.md tasks=1/2 title="Search"]
[DOCUMENT: PROP-search kind=proposal status=draft path=docs/proposals/PROP-search/proposal.md task_kind=feature planning_effort=medium dev_effort=medium title="Search"]
[DOCUMENT: FB-slow-sync kind=feedback status=open path=specs/2026-10/feedback/20261013-slow-sync.md severity=critical scope=upstream target="devkit sync" title="Sync blocks"]
[PAGE: total=42 offset=0 limit=20 count=20 next=20 hidden=3]
[NEXT_CMD: uv run devkit docs list spec --limit 20 --offset 20]
[HISTORY_CMD: uv run devkit docs list spec --history]
```

`resolve` prints `[DOCUMENT: <id> kind= status= path=]`, with `alias=<alias>` appended when the argument was an
alias; `list` prints
`[DOCUMENT: <id> kind= status= path= [overlay fields] tasks= task_kind= planning_effort= dev_effort= severity= scope= target= namespace= title=]`, `tasks=` only on spec lines, `task_kind=`, `planning_effort=` and `dev_effort=` only on proposal lines, `severity=`, `scope=` and
`target=` only on feedback lines, `namespace=` only with registered namespaces, and the overlay fields (3.6), such as
`planning_branch=`, only on documents an overlay names. Values follow devkit's sentinel conventions: `-` for empty, `yes`/`no` for booleans, a JSON
string when the value holds whitespace, quotes, brackets, `=` or a backslash.

### 4.3 JSON Keys (`--format json`)

| Command | Keys |
| --- | --- |
| `resolve` | `documents` (document records: `id`, `kind`, `path`, `status`, `title`, `area`, `summary`, plus `alias`: the alias argument, `null` for a declared ID), `errors` (advisory objects), `notices` |
| `refs` | `id`, `direction`, `total`, `offset`, `limit`, `items` (`id`, `path`, `status`, `references`: `target`, `source`, `path`, `field`, `line`, `column`, `bracket`), `notices`; `path` and `status` are `null` for an ID no single document declares |
| `list` | `total`, `hidden` (the page line's `hidden`), `offset`, `limit`, `namespace` (the selection, `null` for every namespace), `documents` (document records plus `namespace`, `historical` (`true` for a document historical by rule 7 or 8 of `CAP-DOCS-document-model`), `tasks` (spec records); proposal records also `task_kind`, `planning_effort`, `dev_effort`; feedback records also `severity`, `scope`, `target`; a key without a value is left out; the fields of a status overlay (3.6), its `status` replacing the declared one), `notices` |

### 4.4 Exit Codes

`0` success; `2` an unresolved or duplicated ID, or an argument error. Warnings exit `0` (`1` under `--strict`);
notices always exit `0`.

### 4.5 Error Codes

| Code | Level | Class | Condition |
| --- | --- | --- | --- |
| `DOCS_ID_UNRESOLVED` | `ERROR` (`INPUT_ERROR`) | `UnresolvedIdError` | No document declares the ID. |
| `DOCS_ID_DUPLICATE` | `ERROR` (`MAINTENANCE`) | `DuplicateIdError` | More than one document declares the ID; `[TARGET]` lists them. |
| `DOCS_DOCUMENT_INVALID` | `WARNING` | `DocumentInvalidWarning` | A file under `docs/` or `specs/` cannot be read or has malformed frontmatter; it is left out. A `refs` that then fails (`DOCS_ID_UNRESOLVED`) still reports these warnings, before the error in text and under `notices` of `{"error": ...}` in JSON. |
| `ARGUMENT_INVALID` | `ERROR` (`INPUT_ERROR`) | `devkit_core.base.errors.ArgumentError` | A negative `--limit` or `--offset`; a `--where` item without `=`, field or value; an unknown `--namespace`, or `--namespace` combined with `--all-namespaces`. |
| `DOCS_CONFIG_INVALID` | `ERROR` (`INPUT_ERROR`) | `devkit_docs.base.errors.DocsConfigError` | `list`: a malformed `[tool.docs]` table, namespaces included (`CAP-DOCS-namespaces`). |
| `DOCS_ENTRYPOINTS_PATH_INVALID` | `ERROR` (`INPUT_ERROR`) | `devkit_docs.base.errors.EntrypointsPathError` | `list --file`: the path breaks the entrypoint path contract (`CAP-TRACE-code-entrypoints`). |
| `DOCS_OVERLAY_FAILED` | `WARNING` | `devkit_docs.base.errors.OverlayFailedWarning` | `list`: a `devkit.docs.status_overlay` extension failed to load, raised, returned a malformed result or set a reserved field (3.6); its result is left out and the detail names it. The exit code is unchanged. |
| `DOCS_LIST_STATUS_UNKNOWN` | `NOTICE` | `devkit_docs.base.errors.ListStatusUnknownNotice` | `list --status`: a value no indexed document of the selected kinds (every kind without `KIND`) carries as its shown status (3.6), whatever its history or namespace; `[FIX]` lists the statuses that do occur. The filter still applies and the exit code is unchanged. |
