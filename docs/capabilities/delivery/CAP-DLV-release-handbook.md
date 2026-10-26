---
id: CAP-DLV-release-handbook
title: Release Handbook
summary: "A tracked handbook for people under handbook/<lang>/, derived from the Living Spec and refreshed only on the user's request in release preparation; a script reports staleness, regenerates deterministic parts and verifies, and only a refreshing release build checks it."
area: delivery
status: active
usecases: []
entrypoints:
  - tools/devkit-dev/src/devkit_dev/bundle/playbooks/handbook.md
  - scripts/handbook.py
---

# [CAP-DLV-release-handbook] Release Handbook

## 1. Summary

The handbook is the entry point for people who want to know what devkit is and how to use it. It is a derived view
of the Living Spec bound to a release tag: English pages under `handbook/en/` reorganize `docs/` by user journey and
concept, other languages translate the English pages, and every page links to its Living Spec sources at the tag.
It is refreshed only when the user runs the `devkit-dev/handbook` playbook during release preparation
(`ADR-handbook-on-request-release-snapshot`), so between refreshes it is intentionally stale and says which release
it describes.

## 2. Scope & Boundary

- **In-Scope**: the `handbook/` layout, page provenance and staleness, the refresh playbook in the repository-only
  `devkit-dev` bundle, the `scripts/handbook.py` commands (`just handbook ...`) and the handbook check of
  `scripts/release.sh`.
- **Out-of-Scope**:
  - Being a source of truth or a reconcile target: `docs/` prevails, and `spec-sync` has no handbook obligation.
  - Translating Living Spec sources; they stay English and are linked, not copied.
  - The document index, search and `get-context`: they scan `docs/` and `specs/` only, so they ignore `handbook/`.
  - The release notes (`ARCH-07-deployment`): `changes.md` is not fed into them.
  - Any cadence or automatic refresh.

## 3. Business Rules & Policies

### 3.1 Layout and pages

1. **Layout**: The handbook MUST keep `handbook/manifest.json` and one directory per language in the manifest's
   `langs`, `en` first; every language MUST have the English file set at identical relative paths.
   (`tools/devkit-dev/tests/integration/test_handbook_script.py`)
2. **Language boundary**: Non-English text MUST appear only under `handbook/<lang>/` for a language other than `en`
   (`ADR-localized-handbook-language-exception`); identifiers (commands, error codes, document IDs, paths) are never
   translated. Checked in review.
3. **Generated pages**: `decisions.md` (each accepted ADR's summary and source link), `changes.md` (accepted ADRs and
   completed specs new since the previous snapshot) and `glossary.md` (the `docs/glossary.md` terms, with each
   language's rendering from `handbook/<lang>/terms.yaml`) MUST be written whole by the script in every language and
   carry `generated: true`.
4. **No index entry**: Handbook pages MUST NOT carry `id:` frontmatter (`HANDBOOK_FRONTMATTER_ID`).
5. **Source links**: A link to a Living Spec source MUST be `https://github.com/<repository>/blob/<tag>/<path>`
   with the manifest tag (in a preview, the source commit or the upcoming `v<VERSION>`), never `main`
   (`HANDBOOK_LINK_REF`); translated pages mark
   it as an English original.
6. **Wording**: Pages MUST NOT use a capitalized RFC 2119 keyword outside code (`HANDBOOK_NORMATIVE_KEYWORD`).

### 3.2 Provenance and staleness

1. **Provenance**: WHEN the handbook is generated, the script MUST write into every page a provenance block
   (`<!-- handbook:provenance -->`) naming the release tag, the source commit, the generation date and that the
   Living Spec prevails on any conflict.
2. **English staleness**: An English page MUST declare `sources: {<ID>: <git blob SHA>}` for the documents it cites;
   WHEN a cited document's blob at `HEAD` differs from the recorded SHA, `status` MUST report the page stale.
3. **Translation staleness**: A translated page MUST declare `translated_from: en/<path>@<hash>`, where the hash is
   the SHA-256 prefix (16 hex digits) of the English body without frontmatter, provenance block and generated
   blocks; WHEN the English narrative changes, `status` MUST report the translation stale, and a provenance or
   generated-section change MUST NOT.
4. **Stamping**: Only `stamp` MUST record a page as current; `generate` MUST NOT change `sources` or
   `translated_from`.
5. **Coverage**: `status` MUST report every use case and every capability that is not `deprecated` and that no
   English page lists in `sources` as a gap.

### 3.3 Refresh and verification

1. **On request only**: The refresh MUST run only when the user requests it, during release preparation after
   `VERSION` names the upcoming release and before the `just version-sync` metadata commit and the tag.
2. **Closed blocks**: IF a page opens a provenance or generated block without its end marker, THEN `generate` MUST
   exit `2` with `HANDBOOK_BLOCK_UNCLOSED` before writing any file.
3. **Committed source**: IF `docs/` has uncommitted changes, THEN `generate` MUST exit `2` with `HANDBOOK_DOCS_DIRTY`
   and write nothing.
4. **Release run**: WHEN `generate` runs without `--preview`, it MUST write `handbook/manifest.json` with tag
   `v<VERSION>` and source commit `HEAD`, and it MUST NOT change narrative text outside generated blocks.
5. **Preview**: WHERE `--preview` is given, `generate` MUST write only `dist/handbook-preview/` (untracked), name the
   snapshot unreleased and pin source links to the commit.
6. **Verification**: `verify` MUST report, at the manifest source commit, every unresolved cited ID, unknown
   `devkit` command or option, missing source path, unpinned source link, normative keyword, broken relative link,
   parity mismatch, unclosed block, stale translation, missing term rendering and stale English page, one
   `[HANDBOOK_INVALID: ...]` line each, and exit `1` on any.
7. **Human review**: The playbook MUST record each refreshed page's review against its sources in its completion
   report before `handbook/` is committed.
8. **Rules**: `RULE-cli-contract` MUST exclude `handbook/**` (`.devkit/config.toml`), because pages are stale by
   design; `RULE-markdown-link` keeps checking them.
   (`tools/devkit-dev/tests/integration/test_handbook_script.py`)

### 3.4 Release check

1. **Refreshing release**: WHEN `scripts/release.sh` builds a tag equal to the committed manifest tag, it MUST run
   the verification of 3.3 rule 6 and compare `docs/` at `HEAD` with `docs/` at the manifest source commit before
   any wheel build, and fail the build on a finding (`HANDBOOK_DOCS_MISMATCH` for the tree).
2. **Other releases**: WHEN the manifest tag differs from the built tag or no manifest exists, the check MUST print
   `[HANDBOOK_SKIPPED: ...]`, run no verification and write no file.
   (`tools/devkit-dev/tests/integration/test_handbook_script.py`)

## 4. Interfaces & Data Contracts

### 4.1 Commands

`just handbook <command>` runs `scripts/handbook.py`. stdout carries the sentinels below; exit `0` is clean, `1`
findings, `2` could not run (an `[ERROR]` block on stderr).

| Command | Output |
| --- | --- |
| `status` | `[HANDBOOK_STALE: page= sources=]`, `[HANDBOOK_TRANSLATION_STALE: page= source=]`, `[HANDBOOK_GAP: id= kind=usecase\|capability]`, `[HANDBOOK_PARITY: page= problem=missing\|extra]`, `[HANDBOOK_TERM_MISSING: lang= term=]`, then `[HANDBOOK_STATUS: tag= stale= translations= gaps= parity= terms=]` |
| `stamp <lang>/<path>...` | `[HANDBOOK_STAMPED: page=]` per page |
| `generate [--preview]` | `[HANDBOOK_GENERATED: dir= tag=<tag\|unreleased> commit= pages=]` |
| `verify [--preview]` | `[HANDBOOK_INVALID: page= line= code= detail=]` per finding, else `[HANDBOOK_VERIFIED: tag= commit= pages=]` |
| `release-check <tag>` | `[HANDBOOK_SKIPPED: tag= manifest_tag=<tag\|none>]`, or the `verify` output for a refreshing release |

### 4.2 Codes

| Code | Meaning | Exit |
| --- | --- | --- |
| `HANDBOOK_DOCS_DIRTY` | `docs/` has uncommitted changes at a release run of `generate` | 2 |
| `HANDBOOK_MANIFEST_INVALID` | no readable manifest naming `source_commit` and `langs` with `en` | 2 |
| `HANDBOOK_SOURCE_UNAVAILABLE` | the manifest source commit is not in the repository | 2 |
| `HANDBOOK_PAGE_UNKNOWN` | `stamp` names no page, or a translation without its English page | 2 |
| `HANDBOOK_REPOSITORY_UNKNOWN` | no `GITHUB_REPOSITORY` and no github.com `origin` for source links | 2 |
| `HANDBOOK_GIT_FAILED` | a Git command failed | 2 |
| `HANDBOOK_BLOCK_UNCLOSED` | a page opens a provenance or generated block without its end marker (`generate` writes nothing; `verify` reports it with exit 1) | 2 |
| `HANDBOOK_ID_UNRESOLVED` | a cited or `sources` ID resolves to no document (`stamp` exits 2) | 1 |
| `HANDBOOK_COMMAND_UNKNOWN` | a cited `devkit` command or option does not exist (`RULE-cli-contract`) | 1 |
| `HANDBOOK_SOURCE_MISSING` | a source link's path does not exist at the source commit | 1 |
| `HANDBOOK_LINK_REF` | a source link is not pinned to the manifest tag | 1 |
| `HANDBOOK_NORMATIVE_KEYWORD` | a capitalized normative keyword outside code | 1 |
| `HANDBOOK_LINK_BROKEN` | a relative link does not resolve between handbook pages (`RULE-markdown-link`) | 1 |
| `HANDBOOK_PARITY` | a language misses or adds a page | 1 |
| `HANDBOOK_TRANSLATION_STALE` | `translated_from` does not match the English narrative | 1 |
| `HANDBOOK_TERM_MISSING` | a glossary term has no rendering in `terms.yaml` | 1 |
| `HANDBOOK_PAGE_STALE` | an English page's sources changed | 1 |
| `HANDBOOK_FRONTMATTER_ID` | a page carries `id:` frontmatter | 1 |
| `HANDBOOK_DOCS_MISMATCH` | `docs/` at the release commit differs from the manifest source commit | 1 |

### 4.3 Data

- **`handbook/manifest.json`**: `tag` (`null` for a preview), `source_commit`, `repository` (`<owner>/<name>`),
  `langs`, `generated` (date) and, after the first refresh, `previous` (`tag`, `source_commit`) for `changes.md`.
- **Page frontmatter**: `sources` (English), `translated_from` (translations), `generated` (generated pages).
- **Generated blocks**: `<!-- handbook:generated <name> -->` ... `<!-- /handbook:generated -->` with `toc`,
  `usecases` or `capabilities`, rewritten on every run.
- **`handbook/<lang>/terms.yaml`**: a mapping of every `docs/glossary.md` term to its rendering. `docs/glossary.yaml`
  stays a search synonym list.
