---
id: PLAN-release-handbook
spec: SPEC-release-handbook
---

# Technical Plan: `SPEC-release-handbook` Release-bound Multilingual Handbook

## 1. Constitution & Invariant Review

- `ADR-handbook-on-request-release-snapshot` and `ADR-localized-handbook-language-exception` are accepted and this
  plan implements them; no further ADR is needed.
- `ARCH-05-1-containers` defines `devkit-dev` as repository-specific structure checks. Adding a playbook widens that
  definition, which the proposal agreed; the document is updated, no invariant changes.
- `ARCH-08-1-agent-output`: the script writes one-line sentinels to stdout and `[ERROR]`/`[ACTION]` blocks to stderr,
  exits `0` (clean), `1` (findings) or `2` (could not run).
- `docs/` writing instructions, the document index and search stay unchanged (`SPEC-release-handbook` Non-Goal 6).

## 2. Architecture Overview & Impact

| Component | Change |
| --- | --- |
| `scripts/handbook.py` (new) | `status`, `stamp`, `generate [--preview]`, `verify`, `release-check <tag>`; standard library plus PyYAML, with lazy imports of `devkit_dist.cli` and the rules testing entry point for the command and link checks |
| `justfile` | `handbook *args` recipe running the script in the workspace environment |
| `scripts/release.sh` | runs `release-check "$tag"` after the tag and `VERSION` checks, before any wheel build |
| `scripts/affected_tests.py` | maps `scripts/handbook.py` and `scripts/release.sh` to the new tests; `handbook/` selects no test, and `.devkit/config.toml` keeps selecting none (an existing selector contract) |
| `tools/devkit-dev` bundle | `playbooks/handbook.md`, asset `handbook` in preset `handbook`; README note |
| `tools/devkit-dev/tests/integration/` | `test_handbook_script.py` (script, release check and rule exclusion in one module, so its fixture needs no shared helper); `test_resources.py` lists the new asset |
| `.devkit/config.toml` | `handbook/**` in the `RULE-cli-contract` exclude; `devkit-dev = ["structure", "handbook"]` |
| `AGENTS.md`, `README.md` | language exception; a pointer for people |
| Living Spec | new capability CAP-DLV-release-handbook; `ARCH-07-deployment` and `ARCH-05-1-containers` updated |

No new dependency: PyYAML is already a workspace dependency (`devkit-core`).

## 3. Component & Interface Design

```text
just handbook status                 -> [HANDBOOK_STALE|HANDBOOK_TRANSLATION_STALE|HANDBOOK_GAP|HANDBOOK_PARITY|HANDBOOK_TERM_MISSING ...]
                                        [HANDBOOK_STATUS: stale=N translations=N gaps=N parity=N terms=N]   exit 0 clean, 1 findings
just handbook stamp <lang>/<path>... -> [HANDBOOK_STAMPED: page=<page>]                                       exit 0
just handbook generate [--preview]   -> [HANDBOOK_GENERATED: dir=<dir> tag=<tag|unreleased> commit=<sha> pages=N]  exit 0
just handbook verify                 -> [HANDBOOK_INVALID: page=<p> line=<n> code=<CODE> detail="..."]...
                                        [HANDBOOK_VERIFIED: tag=<tag> commit=<sha> pages=N]                   exit 0 / 1
python scripts/handbook.py release-check <tag>
                                     -> [HANDBOOK_SKIPPED: tag=<tag> manifest_tag=<tag|none>]                 exit 0
                                        or the verify output plus the docs-tree check                         exit 0 / 1
```

- **Page format**: optional YAML frontmatter (`sources` on English pages, `translated_from` on translations,
  `generated: true` on fully generated pages; never `id`), the H1, then the provenance block between
  `<!-- handbook:provenance -->` and `<!-- /handbook:provenance -->`, then narrative with generated blocks
  `<!-- handbook:generated <name> -->` ... `<!-- /handbook:generated -->` (`toc`, `usecases`, `capabilities`).
- **Narrative hash**: SHA-256 (first 16 hex digits) of the body without frontmatter, provenance block and generated
  blocks, with trailing whitespace stripped per line.
- **Manifest** (`handbook/manifest.json`): `{"tag", "source_commit", "repository", "langs", "generated"}`; `tag` is
  `v<VERSION>` for a release run. The previous manifest's `tag` and `source_commit` seed `changes.md`.
- **Source links**: `https://github.com/<repository>/blob/<tag>/<path>`; `verify` checks each such link's ref equals
  the manifest tag and its path exists at the source commit.
- **Documents**: frontmatter `id`, `aliases`, `title`, `summary`, `status` under `docs/` and `specs/` at `HEAD`; kinds
  by prefix (`UC-` usecase, `CAP-` capability, `ADR-` decision, `SPEC-` spec). Blob SHAs come from one
  `git ls-tree -r HEAD -- docs specs`.
- **Per-language strings**: the provenance sentence, generated-page headings and the English-source mark exist for
  `en` and `ko`; an unknown language falls back to English.

## 5. Error Handling & Edge Cases

| Code | When | Exit |
| --- | --- | --- |
| `HANDBOOK_DOCS_DIRTY` | `generate` (release run) with uncommitted changes under `docs/` | 2 |
| `HANDBOOK_MANIFEST_INVALID` | `verify`, `status` or a refreshing `release-check` without a readable manifest naming `en` | 2 |
| `HANDBOOK_SOURCE_UNAVAILABLE` | the manifest source commit is not in the repository | 2 |
| `HANDBOOK_PAGE_UNKNOWN` | `stamp` names a page that does not exist | 2 |
| `HANDBOOK_ID_UNRESOLVED`, `HANDBOOK_COMMAND_UNKNOWN`, `HANDBOOK_SOURCE_MISSING`, `HANDBOOK_LINK_REF`, `HANDBOOK_NORMATIVE_KEYWORD`, `HANDBOOK_LINK_BROKEN`, `HANDBOOK_PARITY`, `HANDBOOK_TRANSLATION_STALE`, `HANDBOOK_TERM_MISSING`, `HANDBOOK_PAGE_STALE`, `HANDBOOK_FRONTMATTER_ID`, `HANDBOOK_DOCS_MISMATCH` | verification findings | 1 |

- A release with no `handbook/manifest.json` (this repository until the first refresh) skips like a differing tag.
- The first snapshot has no previous manifest: `changes.md` states that it is the first snapshot.
- The preview copies `handbook/` (when present) into `dist/handbook-preview/` before regenerating, so narrative is
  preserved and the tracked directory is untouched.

## 6. Verification & Test Plan

| Scenario | Test |
| --- | --- |
| AC-01, AC-02, AC-03, AC-04, AC-05, AC-06, AC-07 | `tools/devkit-dev/tests/integration/test_handbook_script.py` on a git fixture repository |
| AC-08 | `test_handbook_script.py` (`release-check` outcomes, no writes on skip, `release.sh` order) |
| AC-09 | `test_handbook_script.py`: `RULE-cli-contract` with the settings of `.devkit/config.toml` on a fixture page, inside and outside `handbook/` |
| AC-10 | `tools/devkit-dev/tests/integration/test_resources.py` and a playbook content test |
| AC-11 | reconcile review of the documents; `just rules-check` |

Commands: `just lint devkit-dev`, `just check devkit-dev`, `just test devkit-dev`, `just test-affected`,
`just rules-check`.
