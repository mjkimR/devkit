---
id: SPEC-release-handbook
title: Release-bound Multilingual Handbook
summary: 'Adds a tracked handbook for people under handbook/{lang}/ (en, ko), refreshed only on the user''s request during release preparation as a snapshot derived from the Living Spec: English is synthesized from docs/, Korean is translated from English, and docs/ stays the single source of truth.'
status: completed
created: 2026-10-26
related_capabilities:
  - CAP-DLV-release-handbook
related_usecases: []
workflow: sdd-spec-feature
---

# [SPEC-release-handbook] Release-bound Multilingual Handbook

## 1. Problem Statement & Motivation

Handed off from proposal PROP-release-handbook on 2026-10-26.

- **Preserved Materials**: `docs/materials/2026-10/20261026-release-handbook` (spike evidence for the design below).
- **Decisions**: `ADR-handbook-on-request-release-snapshot` (a tracked derived view excluded from reconcile, refreshed
  on request, gated only on refreshing releases) and `ADR-localized-handbook-language-exception` (non-English text
  only under `handbook/<lang>/` for languages other than `en`).

`docs/` is organized for agents: contracts are split by capability area and addressed by ID, so search and
`devkit get-context` load only what a task needs. A person who wants to know what devkit is and how to use it day to
day has no single entry point: `README.md` describes the repository structure, `guides/` are installation guides for
agents, and the repository viewer (`CAP-VIEW-repository-viewer`) shows the Living Spec documents as they are.
Building an overall picture means joining `ARCH-01-introduction-and-goals`, `ARCH-03-context`,
`ARCH-05-1-containers`, several capabilities and ADR supersession chains by hand.

A handbook that is a derived view, not a second source of truth, gives people that entry point without adding Living
Spec maintenance. It is a snapshot bound to a release tag and intentionally stale between refreshes; it reorganizes
the Living Spec by user journey and concept and links to the source documents at the release tag instead of
rewriting them. `CAP-DLV-weekly-report` already establishes the pattern: an explicitly invoked playbook produces an
artifact bound to a source revision and verifies it before completing.

This unit delivers the tooling, the playbook, the contract and the release-script check. The first snapshot is
generated when the user first requests a refresh during a release preparation
(`ADR-handbook-on-request-release-snapshot`), not in this unit.

## 2. User Stories

- **US-1**: As a maintainer preparing a release, I want a playbook and a script that tell me which handbook pages are
  stale, regenerate the deterministic parts and verify the result, so that a refreshed handbook matches the release's
  `docs/` without manual cross-checking.
- **US-2**: As a reader of the handbook in English or Korean, I want every page to state which release and source
  commit it describes and to link to the Living Spec sources at that tag, so that I know how old it is and where the
  authoritative contract lives.
- **US-3**: As a maintainer releasing without a refresh, I want the release build to ignore the handbook, so that the
  handbook never blocks a release I did not refresh it for.

## 3. Non-Goals

1. **Scope Excluded**: generating or committing a first handbook snapshot (`handbook/en/`, `handbook/ko/`,
   `handbook/manifest.json`) in this unit. **Rationale**: a refresh runs only on the user's explicit request during
   release preparation (`ADR-handbook-on-request-release-snapshot`); the first such request produces the first
   snapshot through the delivered playbook.
2. **Scope Excluded**: making the handbook a source of truth or a reconcile target; `spec-sync` gains no obligation.
3. **Scope Excluded**: translating Living Spec source documents (L2).
4. **Scope Excluded**: showing the handbook or tags in the repository viewer. **When to Reconsider**: a later
   proposal adds tag reads and a handbook mode to the viewer.
5. **Scope Excluded**: moving or slimming `docs/development/reference/`, package READMEs or `README.md` content into
   the handbook. **When to Reconsider**: after the first release handbook exists.
6. **Scope Excluded**: changing document search, the document index or how `docs/` is written.
7. **Scope Excluded**: feeding `changes.md` into the GitHub release notes.
8. **Scope Excluded**: promoting the handbook to a `devkit-spec` feature for other Living Spec repositories.
9. **Scope Excluded**: a refresh cadence or any automatic refresh.
10. **Scope Excluded**: a command or rule that checks document language; the language exception is checked in review.

## 4. Acceptance Criteria & Behavioral Contracts

The script is `scripts/handbook.py`, run as `just handbook <command>`. Its stdout carries one-line sentinels; a run
that cannot complete writes an `[ERROR]` block with a code and an `[ACTION]` line to stderr and exits `2`.

### [AC-01] A changed source document marks its English page stale

- **Given** a handbook whose English page `en/journeys/a.md` declares `sources` with the git blob SHA of a cited
  document at an earlier commit
- **When** that document changes in a later commit and `just handbook status` runs
- **Then** stdout has one `[HANDBOOK_STALE: page=en/journeys/a.md sources=<ID>]` line, the summary line reports
  `stale=1` and the command exits `1`; with no finding of any kind it exits `0`

### [AC-02] Translation staleness follows only the English narrative body

- **Given** a Korean page whose `translated_from` names `en/<path>@<hash>` of the current English narrative body
- **When** only the provenance header or a generated section of the English page changes
- **Then** `just handbook status` reports no `[HANDBOOK_TRANSLATION_STALE]` line for that page; **and when** a
  narrative line of the English page changes, it reports one
  `[HANDBOOK_TRANSLATION_STALE: page=ko/<path> source=en/<path>]` line

### [AC-03] Uncited use cases and capabilities are coverage gaps

- **Given** a use case or capability that no English page lists in its `sources`
- **When** `just handbook status` runs
- **Then** stdout has one `[HANDBOOK_GAP: id=<ID> kind=<usecase|capability>]` line per such document

A use case or capability with status `deprecated` is not a gap: the handbook describes current behavior (requirement
discovered in review round 1).

### [AC-04] Language parity is checked against the manifest

- **Given** `manifest.json` lists `langs` `en` and `ko`
- **When** `ko/` lacks a page that `en/` has, or has a page that `en/` lacks
- **Then** `just handbook status` reports `[HANDBOOK_PARITY: page=ko/<path> problem=missing]` or `problem=extra`, and
  `just handbook verify` exits `1` with a `code=HANDBOOK_PARITY` line

### [AC-05] Verification rejects inaccurate pages

- **Given** a handbook page that cites an unresolved document ID, a `devkit` command or option the CLI does not have,
  a tag-pinned source link whose path does not exist at the manifest source commit, a capitalized normative keyword
  (`MUST`, `SHALL`, `SHOULD`, `MAY`) outside code, or a broken relative link
- **When** `just handbook verify` runs
- **Then** it exits `1` with one `[HANDBOOK_INVALID: page=<page> line=<n> code=<CODE>]` line per finding, using
  `HANDBOOK_ID_UNRESOLVED`, `HANDBOOK_COMMAND_UNKNOWN`, `HANDBOOK_SOURCE_MISSING`, `HANDBOOK_NORMATIVE_KEYWORD` and
  `HANDBOOK_LINK_BROKEN` respectively (in a preview, a link may name the commit or the upcoming tag `v<VERSION>`); a handbook without findings prints
  `[HANDBOOK_VERIFIED: tag=<tag> commit=<sha> pages=<n>]` and exits `0`

### [AC-06] Generation writes deterministic sections and provenance only

- **Given** a clean `docs/` and `VERSION` naming the upcoming release
- **When** `just handbook generate` runs
- **Then** `handbook/manifest.json` names tag `v<VERSION>` and the source commit `HEAD`, every page's provenance
  header names that tag, commit and date, every generated section and fully generated page (`decisions.md`,
  `glossary.md`, `changes.md`) is rewritten, and no narrative text outside generated sections changes; with
  uncommitted changes under `docs/` it exits `2` with `HANDBOOK_DOCS_DIRTY` and writes nothing

A page with a provenance or generated block that has no end marker stops generation with exit `2` and
`HANDBOOK_BLOCK_UNCLOSED` before any file is written, and `verify` reports it, because filling the block would replace
the narrative after it (requirement discovered in review round 1).

### [AC-07] A preview never touches the tracked handbook

- **Given** a repository with or without `handbook/`
- **When** `just handbook generate --preview` runs
- **Then** it writes to `dist/handbook-preview/`, the provenance header names the commit as unreleased, and no file
  under `handbook/` changes

### [AC-08] The release build checks only a refreshing release

- **Given** a committed `handbook/manifest.json`
- **When** `scripts/release.sh <tag>` runs for a tag equal to the manifest tag, and `docs/` at `HEAD` differs from
  `docs/` at the manifest source commit or a verification check fails
- **Then** the build stops before building any wheel with a non-zero exit and a `code=HANDBOOK_DOCS_MISMATCH` or other
  `[HANDBOOK_INVALID: ...]` line; **and when** the manifest tag differs from the built tag or no manifest exists, the
  handbook check prints `[HANDBOOK_SKIPPED: tag=<tag> manifest_tag=<tag|none>]`, runs no verification and writes no
  file

### [AC-09] Stale handbook pages never fail the repository rules

- **Given** `.devkit/config.toml` excludes `handbook/**` from `RULE-cli-contract`
- **When** a handbook page cites a `devkit` command that a later commit renamed
- **Then** `RULE-cli-contract` reports no violation for the page, while the same citation outside `handbook/` is
  still reported; `RULE-markdown-link` keeps checking relative links under `handbook/`

### [AC-10] The playbook ships in the repository development bundle

- **Given** the `devkit-dev` bundle
- **When** its manifest is loaded
- **Then** it declares a `handbook` playbook asset in a `handbook` preset that this repository selects, and the
  playbook names the script commands, the release-preparation ordering and the recorded human review

### [AC-11] The contract and the language exception are documented

- **Given** the delivered change
- **When** the Living Spec and the root guides are read
- **Then** a capability in `docs/capabilities/delivery/` states the handbook contract, `ARCH-07-deployment` names the
  optional release-preparation step and the release-script check, `ARCH-05-1-containers` names the playbook in the
  `devkit-dev` definition, `AGENTS.md` states the exception for non-English `handbook/<lang>/`, and `README.md`
  points people to the handbook

## 5. Design

### 5.1 Layout

```text
handbook/
├── manifest.json      # language-neutral: tag, source commit, repository, langs, generation date
├── en/                # pivot language, synthesized from docs/
│   ├── README.md      # L0: what devkit is, the overall model, where to start
│   ├── concepts.md    # bundle, sync, projection; Living Spec and specs; workflow stages; advisories
│   ├── journeys/      # L1: one page per use case, how-to oriented
│   ├── areas/         # L1: capability area summaries linking to the L2 sources
│   ├── decisions.md   # generated: each accepted ADR's summary and tag-pinned link
│   ├── changes.md     # generated: previous handbook snapshot to this one, completed specs and new ADRs
│   └── glossary.md    # generated from docs/glossary.md
└── ko/                # the en/ file set, translated from en/, plus terms.yaml
```

- **Tiers**: L0 and L1 pages are written by the agent around generated sections; L2 is the Living Spec source at the
  release tag, linked by tag-pinned URL (`blob/<tag>/<path>`), never `main`, never translated, and marked as an
  English source on translated pages.
- **Languages**: `en` and `ko`, with identical relative paths. Adding a language adds a directory, its `terms.yaml`
  and a `langs` entry. Identifiers (commands, error codes, document IDs) are never translated.
- **Pages carry no `id:` frontmatter**, so they never enter the document index; `handbook/` is outside the index's
  source directories, so search, `get-context` and the docs-scoped rules ignore it unchanged.

### 5.2 Provenance and staleness

- Every page has a generated provenance header: snapshot tag, source commit, generation date and that the Living Spec
  prevails on any conflict. The handbook uses no normative keywords.
- English pages declare `sources: {<ID>: <blob SHA>}` for the cited documents at the source commit. Translated pages
  declare `translated_from: en/<path>@<hash>`, the hash covering only the English narrative body (without frontmatter,
  provenance header or generated sections). Staleness propagates `docs/ -> en -> {lang}`.
- `just handbook stamp <page>...` records a page as refreshed: current SHAs for an English page, the current English
  narrative hash for a translation. Generation never stamps, so a page stays stale until it is rewritten or reviewed.
- Each non-English language keeps `handbook/<lang>/terms.yaml`, mapping every `docs/glossary.md` term to its
  preferred rendering; its generated glossary adds that rendering. `docs/glossary.yaml` stays a search synonym list.

### 5.3 Refresh procedure

Run only when the user requests a refresh, during release preparation after `VERSION` names the upcoming release and
before the `just version-sync` metadata commit. A release without a refresh keeps the previous handbook.

1. `just handbook status` reports stale pages, coverage gaps, parity mismatches and missing terms.
2. The agent rewrites the stale English pages, then their translations, and stamps each; `just handbook generate`
   regenerates the deterministic parts.
3. `just handbook verify` checks, at the source commit: cited IDs resolve; cited `devkit` commands and options exist;
   tag-pinned link paths exist (`git cat-file -e <source commit>:<path>`); no normative keyword; parity and current
   translations; complete term lists; no stale English page; relative links pass `RULE-markdown-link`.
4. A person reviews each refreshed page against its cited sources; the playbook records the outcome in its completion
   report. The handbook is committed before the release tag.
5. `scripts/release.sh` runs the script's `release-check <tag>` before building: a refreshing release (manifest tag
   equals the built tag) reruns step 3 and compares `docs/` at `HEAD` with `docs/` at the manifest source commit;
   every other release skips the handbook.

### 5.4 Impact

- **New**: the playbook in the `devkit-dev` bundle, `scripts/handbook.py`, the `handbook` recipe in `justfile`, the
  script tests under `tools/devkit-dev/tests/`, and a capability for the handbook contract in
  `docs/capabilities/delivery/`.
- **Changed**: `.devkit/config.toml` (`handbook/**` in `[rules.settings.RULE-cli-contract].exclude`, the `handbook`
  preset selected), `scripts/release.sh`, `scripts/affected_tests.py` (test mapping), `AGENTS.md`, `README.md`,
  `ARCH-07-deployment` and `ARCH-05-1-containers`.

## 6. Assumptions

1. No first snapshot is committed in this unit (Non-Goal 1): `ADR-handbook-on-request-release-snapshot` binds every
   refresh to the user's explicit request during release preparation, and the Planning verification item for a first
   generated handbook names "the first refreshing release". `README.md` therefore names the handbook path without a
   relative link, which would fail `RULE-markdown-link` while `handbook/` is absent.
2. The script reads document identity (`id`, `aliases`, `title`, `summary`, `status`) from the frontmatter under
   `docs/` and `specs/`, the same directories the document index scans, instead of calling `devkit spec` per ID, so it
   runs on fixtures without an installed project.
3. Command and relative-link checks reuse `RULE-cli-contract` and `RULE-markdown-link` through the rules testing
   entry point (`check`) on a scratch copy of the pages, so the handbook check and the repository rules cannot
   disagree.
4. The playbook gets its own `handbook` preset in `devkit-dev` so the `structure` preset keeps its meaning (structure
   checks); this repository selects both. Deploying the playbook into `.devkit/managed/` is a `devkit sync` outside
   this unit's write scope.
5. The release-script test covers the handbook check through `release-check` and asserts that `scripts/release.sh`
   runs it before any wheel build; a full wheel build is not part of the test.
