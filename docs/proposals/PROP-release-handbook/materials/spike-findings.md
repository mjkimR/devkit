# Spike findings: PROP-release-handbook

Evidence for the Technical Spike Questions, from `envelopes/scout-01.yaml` and `envelopes/challenger-01.yaml` at
the Planning base 3137814f. Paths are worktree-relative; line numbers hold at that base.

## Q1 Generation split

| Part | Source | Reader |
| --- | --- | --- |
| Table of contents, UC/CAP lists, source links | `devkit spec list/resolve/refs --format json`, or `DocumentIndex.load(root)` (`packages/devkit-spec/src/devkit_spec/features/documents/usecases/search.py:199`) | existing index |
| Glossary page | `docs/glossary.md` 5-column table (`docs/glossary.md:10`) | new table reader |
| Command table | live click tree, as `RULE-cli-contract` walks it | new introspection |
| Error-code table | `**/*.py` code scan, as `RULE-advisory-unique-code` does (`.../unique_code/rule.py:168-183`) | new scan |
| Provenance header, manifest | git | script |
| Narrative (L0, journeys, areas) | agent | playbook |

`devkit generated` is unsuitable: `generated check` reports the handbook stale between releases
(`docs/capabilities/generated/CAP-GEN-tracked-artifacts.md:18`).

## Q2 Staleness and coverage

- No devkit command returns a git blob SHA; the index memo key is BLAKE2b of the text
  (`packages/devkit-spec/src/devkit_spec/features/documents/repositories/memo.py:84-86`). Resolve the path by ID,
  then `git rev-parse <commit>:<path>`. ID keys survive moves; aliases resolve.
- Coverage gap: `devkit spec list usecase capability -n 0 --format json` minus the union of `sources` keys.
- Hashing the whole English file marks every translation stale on every run, because headers and generated
  sections change each run (challenger finding 3). Hash only the narrative body.

## Q3 Exclusion

- Document index: `SOURCE_DIRECTORIES = ("docs", "specs")`
  (`packages/devkit-spec/src/devkit_spec/features/documents/repositories/index.py:49`). Search, `get-context` and
  the docs/specs-scoped spec rules (`RULE-document-summary`, `RULE-document-reference`, `RULE-id-convention`) ignore
  `handbook/` with no change.
- Repo-wide Markdown rules check it (`packages/devkit/src/devkit_agt/features/rules/usecases/project.py:414`):
  `RULE-markdown-link` (relative links only; useful), `RULE-file-length` (hygiene warning, not in CI) and
  `RULE-cli-contract` (ERROR; cited `devkit` commands against the running CLI;
  `packages/devkit/src/devkit_agt/features/rules/services/builtins/cli_contract/rule.py:50,69`). CI runs a whole
  workspace `just rules-check` (`.github/workflows/ci.yml:49`).
- A page that is stale by design fails `RULE-cli-contract` after a command rename (challenger finding 1, P1).
  Smallest exclusion: `handbook/**` in `[rules.settings.RULE-cli-contract].exclude` (`.devkit/config.toml:20-23`),
  not the global `[rules] exclude`, which would also drop `RULE-markdown-link`.

## Q4 Accuracy checks

| Check | Mechanism |
| --- | --- |
| Cited IDs exist at the source commit | `devkit spec resolve` (exit 2, `SPEC_ID_UNRESOLVED`) on a checkout of that commit |
| Cited commands exist at the source commit | click-tree introspection at the source commit |
| L2 link targets exist | `git cat-file -e <source commit>:<path>`; the tag does not exist yet at verification (challenger finding 2) |
| Relative links between pages | `RULE-markdown-link` |
| No normative keywords | regex in the script; no rule exists |
| Language parity | file set and `translated_from` against `manifest.json` |
| No contradiction with the Living Spec | human review; semantic |

weekly-report has no scripted link check: its playbook asks the agent to read back and check links
(`packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/weekly-report.md:60`).

## Q5 Release ordering

- Release preparation is `just version-sync` and a metadata commit (`docs/architecture/ARCH-07-deployment.md:52-68`);
  a `v*` tag on `main` triggers `release.yml` (`.github/workflows/release.yml:14,37`), whose notes come from
  `scripts/release.sh:48-92` plus GitHub's generated notes.
- No release playbook exists. The handbook commit fits into release preparation before the tag.
- Tags v0.1.0 to v0.1.3 span 2026-10-13 to 2026-10-24; `docs/` changed 239 files between v0.1.1 and v0.1.2
  (challenger finding 4). Byte-level staleness makes most pages stale at most releases.

## Q6 Decision digest

`SPEC-document-id-aliases-and-compaction` is completed and excludes ADR compaction
(`specs/2026-10/20261022-document-id-aliases-and-compaction/spec.md:5,48-51`). Ledger compaction is governed by
`ADR-immutable-decisions-editable-records` and the `adr-compaction` playbook. The index holds 49 decisions, 42
accepted. A digest is a read-only listing of accepted ADR summaries; nothing overlaps.

## Q7 Ownership

- `devkit-dev` ships two instructions and two rules, no playbooks or scripts
  (`tools/devkit-dev/src/devkit_dev/bundle/bundle.toml`); `ARCH-05-1-containers` (lines 144-146) defines it as
  repository-specific structure checks, so a playbook there widens that definition.
- weekly-report ships in the `devkit-catalog` `maintenance` bundle; its contract is in `capabilities/delivery/`.
- Playbooks are `[[assets]] kind = "playbook"` entries (`CAP-DIST-manifest-spec`).
- No rule or ADR enforces English-only documentation; `RULE-document-summary` checks only the `summary` field of
  `docs/` and `specs/`. The exception ADR would be the first decision on documentation language.
- `docs/glossary.md` holds English terms only, and `docs/glossary.yaml` holds search synonym clusters that include
  terms other concepts own (challenger finding 7); neither is a translation guide.
