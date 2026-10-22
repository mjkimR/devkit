---
id: PROP-release-handbook
title: Release-bound Multilingual Handbook
summary: "Adds a human-readable handbook under handbook/{lang}/, regenerated at each release as a snapshot derived from the Living Spec: English is synthesized from docs/, other languages are translated from English, and docs/ stays the single source of truth."
status: draft
created_at: 2026-10-22
target_area: documents/
priority: medium
size: M
boundaries:
  owns:
    - tools/devkit-dev/
    - scripts/
    - justfile
    - AGENTS.md
    - README.md
  excludes:
    - packages/devkit-viewer/
    - packages/devkit-dist/src/devkit_dist/features/search/
    - docs/development/reference/
task_kind: feature
planning_effort: medium
dev_effort: medium
workflow: sdd-proposal
---

# [PROP-release-handbook] Release-bound Multilingual Handbook

## 1. Background & Hypothesis

`docs/` is organized for agents: contracts are split by capability area and addressed by ID, so search and
`devkit get-context` load only what a task needs. At `main` 542f4461 it holds 238 files: 39 capabilities (about
8.7k lines), 15 architecture documents, 16 module references, 9 stories and 74 ADRs written within one month.
The agent-first restructuring under way fragments it further, which is the intended shape for agents.

A person who wants to know what devkit is and how to use it day to day has no single entry point. `README.md`
describes the repository structure, `guides/` are installation guides for agents, and the repository viewer
(`CAP-VIEW-repository-viewer`) shows the Living Spec documents as they are. Building an overall picture means joining
`ARCH-01-introduction-and-goals`, `ARCH-03-context` and `ARCH-05-1-containers`, several capabilities and ADR supersession chains by hand.

**Hypothesis.** A handbook that is a derived view, not a second source of truth, gives people that entry point
without adding Living Spec maintenance:

- It is a snapshot bound to a release tag. Between releases it is intentionally stale and says so; it is never a
  reconcile target, so `spec-sync` gains no obligation.
- It reorganizes rather than summarizes: the Living Spec is organized by contract and ID, the handbook by user
  journey and concept. Stories (`US-*`) already follow user journeys and form its backbone.
- Detail is not rewritten. Handbook pages link to the source documents at the release tag, untranslated.
- With the handbook carrying human readability, the agent-first restructuring of `docs/` no longer has to.

`CAP-DLV-weekly-report` already establishes the pattern this reuses: an explicitly invoked playbook produces an
artifact bound to a source revision and verifies its links before completing.

## 2. Technical Spike Questions

- **Q1 (generation split)**: Which parts are generated deterministically (table of contents, command and error code
  tables, provenance header, source links, glossary) and which are written by an agent (narrative)? Can the
  deterministic parts reuse the document index and `devkit spec refs`, or do they need their own reader?
- **Q2 (staleness detection)**: Is `sources: {<ID>: <blob SHA>}` per English page enough to detect stale pages
  deterministically, and how is a coverage gap (a new story or capability that no page cites) reported?
- **Q3 (exclusion)**: Does a repository-root `handbook/` stay out of the document index, `devkit spec search`,
  `devkit get-context` and spec rules such as `RULE-document-summary` and `RULE-document-reference` without changes?
  If not, what is the smallest exclusion?
- **Q4 (accuracy checks)**: Which checks catch a synthesized page that contradicts the Living Spec: cited IDs and
  commands existing at the source commit, no normative keywords (`MUST`, `SHALL`), language parity? Which run as a
  script and which stay in the human review at release?
- **Q5 (release ordering)**: Generate, commit, then tag, so that the tag contains a handbook matching its own
  `docs/`? How does this fit the release procedure in `ARCH-07-deployment`, and should `changes.md` feed the release
  notes there?
- **Q6 (decision digest scope)**: A digest of the ADRs in effect (supersession chains folded) overlaps the problem
  `SPEC-document-id-aliases-and-compaction` addresses on the ledger side. Is the digest in scope here, and where is
  the boundary between the two proposals?
- **Q7 (ownership)**: Start as a devkit-repository-only playbook and script in the `devkit-dev` bundle, with a later
  promotion to a `devkit-spec` feature for other Living Spec repositories? Does the eventual contract belong in
  `capabilities/documents/` or a new capability area?

## 3. Proposed Design & Impact

### 3.1 Layout

```text
handbook/
├── manifest.json      # language-neutral: snapshot tag, source commit, langs ["en", "ko"]
├── en/                # pivot language, synthesized from docs/
│   ├── README.md      # L0: what devkit is, the overall model, where to start
│   ├── concepts.md    # bundle, sync, projection; Living Spec and specs; workflow stages; advisories
│   ├── journeys/      # L1: one page per story (US-*), how-to oriented
│   ├── areas/         # L1: capability area summaries linking to the L2 sources
│   ├── decisions.md   # digest of the decisions in effect (scope per Q6)
│   ├── changes.md     # previous release tag to this one: completed specs and new ADRs
│   └── glossary.md    # generated from docs/glossary.md
└── ko/                # same file set as en/, translated from en/
```

- **Tiers**: L0 (one-page overview) and L1 (journey and area pages) are generated. L2 is the Living Spec source
  document at the release tag, linked by tag-pinned URL (`blob/<tag>/docs/...`), never `main`, and never translated.
  Translated pages mark these links as English sources.
- **Languages**: `handbook/{lang}/` with identical relative paths in every language. Adding a language adds a
  directory and a `langs` entry. Identifiers (`devkit sync`, error codes, document IDs) are never translated.

### 3.2 Provenance and staleness

- Every page states the snapshot tag, source commit and generation date, and that the Living Spec prevails on any
  conflict. The handbook uses no normative keywords.
- English pages declare `sources: {<ID>: <blob SHA>}`; translated pages declare
  `translated_from: en/<path>@<blob SHA>`. Staleness propagates `docs/ -> en -> {lang}`, so only English pages are
  checked against the Living Spec and translations are checked against English only.
- Translated pages use `docs/glossary.yaml` synonym clusters as the term guide, giving the English term on first use
  so the step to an English L2 source stays readable.

### 3.3 Refresh procedure

An explicitly invoked playbook, run during release preparation:

1. A script reports stale pages (changed source SHAs), coverage gaps and language parity mismatches.
2. An agent rewrites only the stale English pages, then their translations; deterministic sections are regenerated
   every run.
3. Verification: cited IDs and commands exist at the source commit, tag-pinned links resolve, no normative keywords,
   every language matches `manifest.json`.
4. A person reviews; the handbook is committed before the release tag (Q5).

Between releases a run against `main` is allowed for preview, but its provenance header names the commit and states
that it is unreleased.

### 3.4 Impact

- **New**: `handbook/` at the repository root, the playbook and its script (Q7), a `justfile` recipe.
- **`AGENTS.md`**: an explicit exception to "Write all documentation, architecture specifications, and guide materials
  in English" for `handbook/{lang}/` translations, backed by an ADR.
- **`README.md`**: links to the handbook for people.
- **Living Spec**: unchanged except the contract recording the handbook (Q7) and possibly the release step in
  `ARCH-07-deployment` (Q5).

### 3.5 Non-Goals

- Making the handbook a source of truth or a reconcile target.
- Translating Living Spec source documents (L2).
- Showing the handbook or tags in the repository viewer. The viewer reads local branches only and refuses a tag with
  `VIEWER_REF_UNKNOWN`; tag reads and a handbook mode are a later proposal.
- Moving or slimming `docs/development/reference/`, package READMEs or `README.md` content into the handbook; that
  is decided after the first release handbook exists.
- Changing document search or the document index beyond the minimal exclusion Q3 may require.

## 4. Lifecycle & Retirement Criteria

- **PADR candidates**: the handbook as a release-bound derived view excluded from reconcile (Q5, Q7); the localized
  documentation exception to the English-only rule.
- **Verification**: script tests for staleness, coverage gap and parity reports on fixtures; a first generated
  `handbook/en/` and `handbook/ko/` for the next release passing the playbook's verification; `just rules-check` clean
  with `handbook/` present.
- **On Acceptance**: recorded with `devkit spec proposal accept`, handed off to a spec bundle on `dev-<slug>`; the
  proposal is deleted there and its decisions become ADRs.
- **On Rejection**: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
