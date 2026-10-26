---
id: PROP-release-handbook
title: Release-bound Multilingual Handbook
summary: "Adds a human-readable handbook under handbook/{lang}/, regenerated at release as a snapshot derived from the Living Spec: English is synthesized from docs/, other languages are translated from English, and docs/ stays the single source of truth."
status: reviewing
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
    - .devkit/config.toml
    - docs/capabilities/delivery/
    - docs/architecture/
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
`devkit get-context` load only what a task needs. At the Planning base 3137814f it holds 42 capabilities, 14
architecture documents, 16 module references, 12 use cases and 49 ADRs (42 accepted). The agent-first
restructuring under way fragments it further, which is the intended shape for agents.

A person who wants to know what devkit is and how to use it day to day has no single entry point. `README.md`
describes the repository structure, `guides/` are installation guides for agents, and the repository viewer
(`CAP-VIEW-repository-viewer`) shows the Living Spec documents as they are. Building an overall picture means joining
`ARCH-01-introduction-and-goals`, `ARCH-03-context` and `ARCH-05-1-containers`, several capabilities and ADR supersession chains by hand.

**Hypothesis.** A handbook that is a derived view, not a second source of truth, gives people that entry point
without adding Living Spec maintenance:

- It is a snapshot bound to a release tag. Between releases it is intentionally stale and says so; it is never a
  reconcile target, so `spec-sync` gains no obligation.
- It reorganizes rather than summarizes: the Living Spec is organized by contract and ID, the handbook by user
  journey and concept. Use cases (`UC-*`) and capability areas form its backbone together, because the use cases
  cover delivery and governance but no distribution journey.
- Detail is not rewritten. Handbook pages link to the source documents at the release tag, untranslated.
- Whether the handbook changes how `docs/` is written is a separate decision (q5); this proposal does not change the
  Living Spec writing instructions.

`CAP-DLV-weekly-report` already establishes the pattern this reuses: an explicitly invoked playbook produces an
artifact bound to a source revision and verifies its links before completing.

## 2. Technical Spike Questions

Answered in Planning; evidence in `materials/spike-findings.md`.

- **Q1 (generation split)**: Deterministic: table of contents, UC and capability lists, source links and
  provenance from the document index (`devkit spec list/resolve/refs --format json`); the glossary, command and
  error-code tables need small readers of their own in the handbook script. The agent writes the narrative only.
  `devkit generated` is not used, because its check reports the handbook stale between releases.
- **Q2 (staleness detection)**: `sources: {<ID>: <SHA>}` per English page works when the SHA comes from git
  (`git rev-parse <commit>:<path>` after resolving the ID). Coverage gap: every use case and capability not cited by
  any English page. Translation staleness hashes only the English narrative body (section 3.2).
- **Q3 (exclusion)**: The document index scans only `docs/` and `specs/`, so search, `get-context` and the spec
  document rules ignore `handbook/` unchanged. Repo-wide Markdown rules check it; `RULE-cli-contract` would fail on
  pages that are stale by design, so `handbook/**` joins that rule's `exclude` in `.devkit/config.toml`.
  `RULE-markdown-link` keeps checking relative links between pages.
- **Q4 (accuracy checks)**: Scripted checks are listed in section 3.3 step 3. Contradiction with the Living Spec is
  semantic and stays in the recorded human review.
- **Q5 (release ordering)**: Generate, verify and commit in release preparation, then tag (section 3.3). Release
  notes stay as they are; `changes.md` is not fed into them.
- **Q6 (decision digest scope)**: `SPEC-document-id-aliases-and-compaction` is completed and excludes ADR compaction;
  `ADR-immutable-decisions-editable-records` keeps the ledger compact. The digest lists the accepted ADRs' summaries
  only and folds no chains (q7).
- **Q7 (ownership)**: Open; the user decides the bundle and contract area (q6).

## 3. Proposed Design & Impact

### 3.1 Layout

```text
handbook/
├── manifest.json      # language-neutral: snapshot tag, source commit, langs
├── en/                # pivot language, synthesized from docs/
│   ├── README.md      # L0: what devkit is, the overall model, where to start
│   ├── concepts.md    # bundle, sync, projection; Living Spec and specs; workflow stages; advisories
│   ├── journeys/      # L1: one page per use case (UC-*), how-to oriented
│   ├── areas/         # L1: capability area summaries linking to the L2 sources
│   ├── decisions.md   # list of the accepted ADRs with their summaries (q7)
│   ├── changes.md     # previous handbook tag to this one: completed specs and new ADRs
│   └── glossary.md    # generated from docs/glossary.md
└── <lang>/            # same file set as en/, translated from en/, plus terms.yaml (q4)
```

- **Tiers**: L0 (one-page overview) and L1 (journey and area pages) are generated. L2 is the Living Spec source
  document at the release tag, linked by tag-pinned URL (`blob/<tag>/docs/...`), never `main`, and never translated.
  Translated pages mark these links as English sources.
- **Languages**: `handbook/{lang}/` with identical relative paths in every language. Adding a language adds a
  directory and a `langs` entry. Identifiers (`devkit sync`, error codes, document IDs) are never translated.
- **Delivery form**: a tracked `handbook/` on `main`, pending q1.
- **Pages carry no `id:` frontmatter**, so they never enter the document index.

### 3.2 Provenance and staleness

- Every page states the snapshot tag, source commit and generation date, and that the Living Spec prevails on any
  conflict. The handbook uses no normative keywords.
- English pages declare `sources: {<ID>: <SHA>}` with git blob SHAs of the cited documents at the source commit.
  Translated pages declare `translated_from: en/<path>@<hash>`, where the hash covers only the English narrative body,
  without the provenance header or the generated sections. Staleness propagates `docs/ -> en -> {lang}`, so only
  English pages are checked against the Living Spec and translations against English only; a header-only change leaves
  translations fresh.
- Each non-English language keeps `handbook/<lang>/terms.yaml`, mapping every `docs/glossary.md` term to its
  preferred rendering. Translated pages use it and give the English term on first use. `docs/glossary.yaml` stays a
  search synonym list, because its clusters include terms other concepts own.

### 3.3 Refresh procedure

An explicitly invoked playbook, run during release preparation before `just version-sync`'s metadata commit
(`ARCH-07-deployment` section 1 gains this step), for the releases q2 selects:

1. A script reports stale pages, coverage gaps (uncited use cases and capabilities) and language parity mismatches.
2. An agent rewrites only the stale English pages, then their translations; deterministic sections are regenerated
   every run.
3. Verification by the script, at the source commit:
   - every cited ID resolves;
   - every cited `devkit` command and option exists;
   - every L2 link target path exists (`git cat-file -e <source commit>:<path>`); the URL is rendered with the tag,
     which does not exist yet;
   - no normative keyword (`MUST`, `SHALL`, `SHOULD`, `MAY` in capitals);
   - every language has the file set of `manifest.json` and a current `translated_from` for each page;
   - `RULE-markdown-link` passes on `handbook/`.
4. A person reviews each refreshed page against its cited sources; the playbook records the review outcome in its
   completion report. The handbook is committed before the release tag.
5. `scripts/release.sh` checks that the `docs/` tree at the tagged commit equals the `docs/` tree at the
   `manifest.json` source commit for a release that refreshes the handbook, and fails the build otherwise (q3).

A preview run against `main` writes to an untracked directory (`dist/handbook-preview/`) and its provenance header
names the commit as unreleased. Only a release run writes `handbook/`.

### 3.4 Impact

- **New**: `handbook/` at the repository root (a new root directory), the playbook and its script (q6), a `justfile`
  recipe, and a capability recording the handbook contract (q6).
- **`.devkit/config.toml`**: `handbook/**` in `[rules.settings.RULE-cli-contract].exclude`.
- **`AGENTS.md`**: an explicit exception to "Write all documentation, architecture specifications, and guide materials
  in English" for `handbook/{lang}/` translations, backed by an ADR (q4).
- **`README.md`**: links to the handbook for people.
- **Living Spec**: the handbook capability (q6), the release-preparation step in `ARCH-07-deployment`, and
  `ARCH-05-1-containers` if the playbook joins `devkit-dev` (q6).

### 3.5 Non-Goals

- Making the handbook a source of truth or a reconcile target.
- Translating Living Spec source documents (L2).
- Showing the handbook or tags in the repository viewer. The viewer reads local branches only and refuses a tag with
  `VIEWER_REF_UNKNOWN`; tag reads and a handbook mode are a later proposal.
- Moving or slimming `docs/development/reference/`, package READMEs or `README.md` content into the handbook; that
  is decided after the first release handbook exists.
- Changing document search or the document index.
- Feeding `changes.md` into the GitHub release notes.
- Promoting the handbook to a `devkit-spec` feature for other Living Spec repositories.

## 4. Lifecycle & Retirement Criteria

- **PADR candidates**: the handbook as a release-bound derived view excluded from reconcile, with its delivery form and
  refresh cadence (q1, q2, q3); the localized documentation exception to the English-only rule (q4).
- **Verification**:
  - script tests on fixtures: a changed source SHA marks its English page stale; a header-only English change leaves
    translations fresh; an uncited use case or capability is reported as a gap; a missing or extra translated file is
    a parity mismatch; an unresolved ID, a missing command, a missing L2 path and a normative keyword each fail
    verification;
  - a release-script test: a `docs/` tree differing from the manifest source commit fails the build;
  - a first generated `handbook/en/` and translation for the next refreshing release passing every step 3 check, with
    the recorded human review;
  - `just rules-check` clean with `handbook/` present, and still clean after a fixture renames a cited command.
- **On Acceptance**: recorded with `devkit spec proposal accept`, handed off to a spec bundle on `dev-<slug>`; the
  proposal is deleted there and its decisions become ADRs.
- **On Rejection**: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.

## 5. Planning decisions

- Planning effort `medium`: one `scout` (spike evidence) and one `challenger` pass
  (`envelopes/scout-01.yaml`, `envelopes/challenger-01.yaml`).
- Folded challenger findings: 1 (cli-contract exclusion), 2 (verify paths at the source commit, release-script tree
  check), 3 (narrative-body hash), 6 (boundaries), 7 (per-language term list), 8 (listed checks and recorded review),
  9 (untracked preview), 11 (backbone and inventory).
- Open for the user: findings 4, 5 and 10, asked as q1 to q7.
