---
id: SPEC-alias-references-in-quick-references
title: Check document IDs in quick references and keep rename tables intact
summary: Extend RULE-document-reference's cited-ID check to docs/development, guides and package READMEs so renamed IDs are fixed there too, state that rename specs write old IDs as plain text, and correct the rule guide on ADR alias rewrites.
status: in-progress
created: 2026-10-30
related_capabilities:
  - CAP-GOV-spec-rules
  - CAP-DOCS-document-model
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-alias-references-in-quick-references] Check document IDs in quick references and keep rename tables intact

## 1. Problem Statement & Motivation

A document rename keeps the old ID in `aliases` and runs `devkit rules fix`, which rewrites every alias reference in
the indexed documents (`CAP-DOCS-document-model`, renaming step). The repository's quick references are outside the
document index: `docs/development/**`, `guides/**` and the package and tool READMEs cite document IDs in code spans,
yet `RULE-document-reference` neither reports nor fixes them, so a clean `devkit rules check` after a rename still
leaves stale IDs that only an `rg` sweep finds. The base holds four such alias references (two in
`docs/development/`, two in `packages/devkit-viewer/README.md`).

The same fix rewrites a rename spec's own mapping table when the spec writes the old IDs in code spans, so the record
loses which IDs were renamed; the renaming step and the `spec-specify` skill do not warn about it. And the rule's guide
says the autofix never rewrites an alias reference in an ADR or PADR, which contradicts the code and
`ADR-immutable-decisions-editable-records`.

## 2. User Stories

- **US-1**: As an agent renaming a document, I want `devkit rules check` to report and `devkit rules fix` to rewrite
  the old ID where a quick reference cites it, so that one fix pass leaves no stale code-span reference.
- **US-2**: As an agent writing a quick reference, I want a cited ID that no document declares reported, so that a
  typo or a removed document does not reach other agents.
- **US-3**: As an agent writing a rename spec, I want the guidance to tell me to write the old IDs as plain text, so
  that the fix leaves the spec's mapping table intact.
- **US-4**: As an agent scoping a rename, I want the rule guide to state what the fix rewrites, so that I do not
  leave ADRs and PADRs out of the write scope.

## 3. Non-Goals

1. **Scope Excluded**: plain-text IDs (outside a code span) in any file, and the `target` field of feedback files, stay
   unchecked; the renaming step names them as the remaining manual sweep.
2. **Scope Excluded**: the steering-file and glossary Owner checks keep their behavior (reported, never fixed).
3. **Scope Excluded**: quick-reference files stay outside the document index: no indexing, no reference-graph edges,
   no `devkit docs refs` results for them.
4. **Scope Excluded**: no rule change for rename mapping tables (no skipping of a code span beside its canonical ID);
   the fix is guidance only.
5. **Scope Excluded**: other ID-free Markdown (the root `README.md`, nested package READMEs, bundle seed files,
   examples, the handbook, test READMEs) is not checked by default; a project adds paths through the setting.

## 4. Acceptance Criteria & Behavioral Contracts

### [AC-01] An alias cited in a quick reference is reported and fixed

- **Given** `docs/a.md` declares `id: ADR-new` with `aliases: [ADR-old]`, and `docs/development/x.md`,
  `guides/y.md`, `packages/p/README.md` and `tools/t/README.md` each cite ADR-old in a code span
- **When** `devkit rules check` runs
- **Then** each file has one fixable `RULE-document-reference` error at the citation's line and column with the
  message `` ADR-old is an alias of ADR-new; reference `ADR-new` ``
- **And When** `devkit rules fix` runs
- **Then** each code span reads ADR-new, the rest of every file is unchanged and a second check reports nothing.

### [AC-02] An unresolved cited ID in a quick reference is an error

- **Given** a quick reference cites in code spans an ID no document declares, an ID two documents declare and an
  alias two documents declare
- **When** `devkit rules check` runs
- **Then** each is one error, not fixable, with the message the indexed documents use (`no document has the ID
  <ID>`, `<ID> is declared by 2 documents: <paths>`, `<ID> is an alias declared by 2 documents: <paths>`), and
  `devkit rules fix` leaves the file unchanged.

### [AC-03] Only cited IDs in the visible text of the configured, targeted, unindexed files are checked

- **Given** quick references that hold IDs as plain text, in fenced or indented code, in HTML comments, in
  `~~strikethrough~~` and in a code span with more than the ID, and Markdown files outside the default set (the root
  `README.md`, `packages/p/docs/README.md`, `examples/README.md`)
- **When** `devkit rules check` runs
- **Then** none of them is reported; a quick-reference file that declares an ID under `docs/` is checked once, as an
  indexed document; a file not targeted by a run, or removed by `[rules] exclude`, is neither reported nor rewritten.

### [AC-04] The quick-reference set is a rule setting

- **Given** `RULE-document-reference` declares the setting `quick_references` (a list of workspace path patterns)
  with the defaults `docs/development/**/*.md`, `guides/**/*.md`, `packages/*/README.md` and `tools/*/README.md`
- **When** a project sets `[rules.settings.RULE-document-reference] quick_references = ["notes/**/*.md"]`
- **Then** a stale citation in `notes/n.md` is reported and one in `guides/y.md` is not; `quick_references = []`
  turns the check off; an invalid pattern (for example `"../x"`) fails the run with `RULES_SETTINGS_INVALID`; and
  `devkit rules explain RULE-document-reference` documents the setting.

### [AC-05] The repository's quick references are clean

- **Given** this change applied to the repository
- **When** `uv run devkit rules check` runs on the whole workspace
- **Then** it reports no `RULE-document-reference` finding in the quick references (the four alias references of the
  base are rewritten to their canonical IDs).

### [AC-06] The rule guide matches the code

- **Given** the deployed guide of `RULE-document-reference`
- **When** an agent reads its Remediation and Configuration sections
- **Then** the autofix bullet no longer says it never rewrites an alias reference in an ADR or PADR, it names the
  quick-reference rewrite, and Configuration describes `quick_references` with its defaults.

### [AC-07] Rename guidance keeps mapping tables intact

- **Given** the renaming step of `CAP-DOCS-document-model` and the `spec-specify` skill
- **When** an agent plans a document rename
- **Then** both state that a rename spec writes the old IDs as plain text, never in a code span, in its mapping tables
  and prose, because `devkit rules fix` rewrites code-span alias references; and the renaming step states that the
  fix also covers code-span citations in the configured quick references, leaving plain-text IDs (feedback `target`
  fields included) and ID-free files outside the configured set to a manual sweep. A bundle guidance test pins the `spec-specify` sentence.

## 5. Source feedback

- `FB-alias-references-outside-index-unreported`: extend the cited-ID check to the quick references, with alias
  autofix and unresolved-ID errors (AC-01 to AC-05, AC-07); plain-text IDs and feedback `target` fields stay out of
  scope.
- `FB-rules-fix-rewrites-rename-mapping-tables`: guidance in the renaming step and `spec-specify` that rename specs
  write old IDs as plain text (AC-07); no rule change.
- `FB-document-reference-guide-adr-rewrite-stale`: drop the stale ADR/PADR clause from the rule guide's Remediation
  (AC-06).

## 6. Assumptions

1. Quick references are Markdown files only; the default set is the one the user named, written as `**` patterns, and
   leaves nested READMEs out because bundle seed READMEs ship to consumer projects whose IDs differ.
2. The setting's defaults ship with the `docs` bundle, so a consumer project with matching paths gets the check too;
   it can narrow or empty the list in `[rules.settings.RULE-document-reference]`.
