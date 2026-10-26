---
id: SPEC-foundation-documents
title: Steering documents for project-wide background
summary: Adds a flat docs/steering/ directory of project-wide background documents such as the glossary, product vision and style guides, whose frontmatter devkit get-context lists in every agent context so agents read a body when a decision concerns it, and moves the glossary into it.
status: planned
created: 2026-10-26
depends_on:
  - SPEC-table-driven-document-kinds
related_capabilities:
  - CAP-DIST-context-and-playbooks
  - CAP-DIST-manifest-spec
  - CAP-DIST-workspace-ownership
  - CAP-DOCS-document-model
  - CAP-DOCS-document-search
  - CAP-GOV-spec-rules
  - CAP-HARN-agent-guidance
  - CAP-DLV-release-handbook
  - CAP-DLV-delivery-workflows
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-foundation-documents] Steering documents for project-wide background

## 1. Problem Statement & Motivation

Handed off from proposal PROP-foundation-documents on 2026-10-26.
- **Preserved Materials**: `docs/materials/2026-10/20261026-foundation-documents`
  (`spike-findings.md` F1-F6, `steering-design.md` D1-D4)
- **Decisions**: `ADR-steering-documents-directory`, `ADR-background-pointer-in-constitution`,
  `ADR-bundle-context-lists-project-documents`

### 1. Background & Hypothesis

The Living Spec has kinds for behavior and structure (capabilities, use cases, architecture, decisions) and a free
form for evidence (materials). It has no place for project-wide background that applies to every piece of work but
is neither behavior nor evidence: the product's purpose and principles, a brand or tone guide, a visual style
direction, a domain or setting overview. The glossary is the only document of this nature today, and it sits alone
at `docs/glossary.md` (with `docs/glossary.yaml` for search synonyms).

Without a place, such background is written into capabilities, where it bends the contract shape and invites
entrypoints and reconciliation that do not apply, or into materials, where it loses its standing as current and
binding. Either way agents do not know to read it, so work that depends on it (wording, naming, interface and
content decisions) drifts from it.

Hypothesis: one flat `docs/steering/` directory of ID-free steering documents, one file per topic, fixes both
problems when every agent context sees what each file covers. `devkit get-context spec` prints each steering file's
frontmatter (title and a one-line scope) at run time, so the list is always current and always loaded, and an agent
reads a body only when its decision concerns that scope. A rule bounds the number of files and each body's size, so
the always-loaded cost stays small. The glossary moves into the directory.

## 2. User Stories

- **US-1**: As an agent in any role, I want every context to list the project's steering documents with their scope
  so that I read the one a wording, naming, interface or content decision depends on.
- **US-2**: As a project maintainer, I want one flat directory for project-wide background, the glossary included,
  so that background has a known place outside the contract kinds and materials.
- **US-3**: As a project maintainer, I want a rule to bound the steering directory and check the IDs it cites so
  that the always-loaded cost stays small and background does not drift from the documents it names.
- **US-4**: As a bundle author, I want a bundle to declare a workspace directory whose Markdown frontmatter
  `devkit get-context` lists, so that `devkit-dist` needs no knowledge of any one bundle's documents.

## 3. Non-Goals

1. **Scope Excluded**: no new ID-bearing document kind and no row in the kind table; no relation fields to or from
   steering documents; steering files stay outside the document index and search.
2. **Scope Excluded**: no change to the glossary table columns, to the Owner check's semantics, to document search
   or to the ranker.
3. **Scope Excluded**: no namespace copy of the steering directory (`docs/packages/<name>/steering/`); package
   glossaries stay at `docs/packages/<name>/glossary.md`.
4. **Scope Excluded**: no product, brand or style content of any particular project, and no
   `docs/steering/ux-objects.md` (that is `PROP-ux-documentation`).
5. **Scope Excluded**: no migration, notice or legacy reader for a consumer's existing `docs/glossary.md`
   (`AGENTS.md` Compatibility); only the release handbook script, which reads historical commits, falls back to the
   old path.
6. **Scope Excluded**: the handbook pages under `handbook/` are not regenerated or stamped (frozen for 0.1.4).
7. **Scope Excluded**: no Codex or Antigravity host verification of the projected role contracts (`user`).

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] A bundle manifest declares a context document directory

- **Given** a `bundle.toml` with a top-level `context_documents` key
- **When** the bundle is loaded (`load_bundle`)
- **Then** a value that passes the seeded `target` grammar (`docs/steering`) is accepted and exposed as
  `Bundle.context_documents`, a missing key is `None`, and a non-string, empty, absolute, `..`, backslash,
  `.devkit/...`, `.git` or `AGENTS.md` value raises `BundleError` (`BUNDLE_INVALID`) naming `context_documents`.

### [AC-02] get-context lists the declared directory's documents

- **Given** a synchronized bundle whose managed `bundle.toml` declares `context_documents = "docs/steering"` and a
  workspace `docs/steering/` holding `b.md`, `a.md` (both with `title` and `summary`), `README.md`, `glossary.yaml`
  and a subdirectory `sub/` with `c.md`
- **When** `devkit get-context <bundle> --format json` runs
- **Then** it exits `0` and its result has a `documents` list of exactly two objects, `a.md` then `b.md`, each with
  the absolute `path`, the `title` and the `summary`; `README.md`, the YAML file and `sub/c.md` are not listed.

### [AC-03] get-context never fails on a project document

- **Given** the declaration of AC-02
- **When** the directory is absent, is a symlink, or holds a symlinked `*.md`, a non-regular entry, a non-UTF-8
  file, a file without frontmatter or with malformed YAML frontmatter, a file whose `title` or `summary` is not a
  string, or a file whose frontmatter does not close within its first 4096 bytes; or the bundle declares nothing
- **Then** get-context exits `0`; an undeclared or absent or symlinked directory gives `documents: []`; symlinked and
  non-regular entries are not listed; each other file is listed with `null` for every value it cannot read; a file
  larger than 4096 bytes whose frontmatter closes within that prefix is listed with its values.

### [AC-04] The always-loaded list stays bounded at the default caps

- **Given** ten steering files (the default `max_files`), each with a 300-character summary (the default
  `max_summary_length`) and a 60-character title
- **When** get-context lists them
- **Then** the JSON of `documents`, without the bytes of the ten `path` values, is at most 4096 bytes.

### [AC-05] Every spec context names the steering list and its trigger

- **Given** the `spec` bundle
- **When** its manifest, constitution and role contracts are read
- **Then** `bundle.toml` declares `context_documents = "docs/steering"`; the constitution has one line naming
  `docs/steering/` and the `documents` list of `devkit get-context spec`, telling the agent to read a body before a
  decision its summary covers; and every role contract under `subagents/` runs `devkit get-context spec` (none reads
  `.devkit/managed/spec/AGENTS.md` instead).

### [AC-06] RULE-steering-documents checks the directory's shape and frontmatter

- **Given** `RULE-steering-documents` (error severity) and files under `docs/steering/`
- **When** `devkit rules check` runs
- **Then** it reports, one violation each: a file inside a subdirectory; a file that is neither `*.md` nor
  `glossary.yaml`; an `id` key; a missing or empty `title`; a missing or empty `summary`; a summary with a letter
  outside the Latin script; a summary longer than `max_summary_length` characters (default 300); and reports nothing
  for `README.md`, for a well-formed file, or when no file under `docs/steering/` is targeted.

### [AC-07] RULE-steering-documents bounds the file count and body size

- **Given** the default settings `max_files = 10` and `max_body_bytes = 24576`
- **When** the directory holds eleven Markdown files other than `README.md`, or a file whose body (the text after
  the frontmatter) is 24577 bytes
- **Then** the rule reports the eleventh file in sorted order and the oversized body, each once; a staged commit
  that adds the eleventh file is reported by a `--staged` run; raising either setting clears the finding, and a
  non-positive setting is a settings error.

### [AC-08] IDs cited in steering files resolve

- **Given** a steering file citing an unresolved ID, an alias of another document's ID and a resolved ID, each in
  backticks, in its body
- **When** `RULE-document-reference` checks it, with and without `--fix`
- **Then** it reports `no document has the ID <ID>` for the first and `<alias> is an alias of <ID>; name <ID>` for
  the second, nothing for the resolved ID, rewrites nothing under `--fix`, adds the file to no reference graph, and
  reports an Owner cell of `docs/steering/glossary.md` once.

### [AC-09] The glossary Owner check reads the moved glossary

- **Given** an unresolved Owner in a five-column table
- **When** it is in `docs/steering/glossary.md`, and when it is in `docs/glossary.md`
- **Then** `RULE-document-reference` reports the first and no longer reads the second.

### [AC-10] Search expands synonyms from the moved glossary

- **Given** synonym clusters in `docs/steering/glossary.yaml`
- **When** `devkit spec search` expands a query
- **Then** it expands through that file, a `docs/glossary.yaml` alone expands nothing, and `SPEC_GLOSSARY_INVALID`
  names `docs/steering/glossary.yaml` in its message, target and fix.

### [AC-11] The docs skeleton seeds the steering glossary

- **Given** the `spec` bundle's `docs-skeleton` seed
- **When** it is listed or synchronized into an empty project
- **Then** it holds `steering/glossary.md` (with `title` and English `summary` frontmatter and the five-column
  table) and `steering/glossary.yaml`, no root `glossary.md` or `glossary.yaml`, and its `README.md` and
  `architecture/README.md` point to `steering/glossary.md`.

### [AC-12] No bundle guidance names the old glossary path

- **Given** the `spec` bundle sources (instructions, skills, playbooks, rule guides, seed)
- **When** they are searched for `docs/glossary.md`, `docs/glossary.yaml` or `../glossary.md`
- **Then** none is found, and `living-spec-writing`, `architecture-writing`, `spec-sync`, the `adr-compaction`
  playbook, the brownfield `migration.md` and the `RULE-document-reference`, `RULE-id-convention` and
  `RULE-proposal-boundaries` guides name `docs/steering/glossary.md` where they named the glossary.

### [AC-13] The repository moves its own glossary and Living Spec

- **Given** this repository after the change
- **When** `devkit rules check` and `devkit sync --check` run
- **Then** `docs/steering/glossary.md` and `docs/steering/glossary.yaml` exist with no root copy; the glossary has
  the steering frontmatter and the row **Steering document** (Avoid: foundation, background); `docs/README.md`,
  `docs/architecture/README.md` and the capabilities that name the glossary path name `docs/steering/`; both
  commands exit `0`.

### [AC-14] The release handbook reads either glossary layout

- **Given** `scripts/handbook.py` and a pinned source commit
- **When** the commit has `docs/steering/glossary.md`, only `docs/glossary.md`, or neither
- **Then** it reads the steering glossary, falls back to the old path, and fails with `HANDBOOK_GLOSSARY_MISSING`
  (exit `2`) when neither exists; the glossary page and `HANDBOOK_TERM_MISSING` follow the file it read.

### [AC-15] The viewer groups steering documents

- **Given** the viewer's `bookGroup`
- **When** it classifies `docs/steering/glossary.md`, `docs/steering/product.md`,
  `docs/packages/example/glossary.md` and `docs/glossary.md`
- **Then** the first three are `Steering`, `docs/glossary.md` is `Overview`, `bookGroups` holds `Steering` in place
  of `Glossary`, and the committed build under `devkit_viewer/static/` is rebuilt from that source.

## 5. Assumptions

- The handed-off premises hold on base `26f7eb33`: every glossary consumer of spike F3 is still at the path it
  names, and `SPEC-table-driven-document-kinds` landed the kind table this change adds no row to.
- The manifest key is a top-level `context_documents` string (one directory per bundle), because the ADR names one
  declared directory and the top level is where bundle-wide fields such as `auto_select` live.
- `RULE-steering-documents` checks only the root `docs/steering/` (no namespace copy, Non-Goal 3), reuses the
  English-letter test of `RULE-document-summary`, and reports the count overflow whenever any steering file is
  targeted, so a commit adding a file that sorts before others is refused too.
- `README.md` is matched by exact name, the way the document index skips it.
- The handbook failure code is `HANDBOOK_GLOSSARY_MISSING`, in the script's existing `HANDBOOK_*` family, raised as
  its other run failures are (exit `2`); the released snapshot's `source_commit` 5e71d74c has `docs/glossary.md`, so
  the fallback keeps it readable.
- This repository's `docs/steering/` gets no `README.md`: `docs/README.md` describes the directory.
