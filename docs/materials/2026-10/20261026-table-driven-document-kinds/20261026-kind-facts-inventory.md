---
id: MAT-kind-facts-inventory
title: Document kind facts inventory
summary: "Lists every place in devkit-spec and devkit-viewer that encodes a document kind fact, classifies each as table data or kind-specific behavior, and records the baseline probe for showing no behavior change."
created_at: 2026-10-26
---

# [MAT-kind-facts-inventory] Document kind facts inventory

Evidence for spike questions Q1 to Q4 of `SPEC-table-driven-document-kinds`, read at base `96df5d86`. Paths are
relative to `packages/devkit-spec/src/devkit_spec/features/` unless they start with `packages/` or `docs/`. The
viewer findings come from this proposal's historical Git `cfc82a4cb3d651c38c61b6a4da880be9ebfbe2fd:docs/proposals/PROP-table-driven-document-kinds/envelopes/scout-01.yaml`.

## 1. Facts that are table data (Q1)

| Fact | Current places | Notes |
| --- | --- | --- |
| Prefix to kind, kind order | `documents/models/ids.py:16-48` (`Kind`, `PREFIXES`, `ID_SOURCE`); `documents/usecases/browse.py:22` (`_KIND_ORDER = enumerate(Kind)`); `documents/cli/commands.py:184`, `documents/cli/search.py:40` (`click.Choice` over `Kind`) | Row order must stay the enum order: `devkit spec list` sorts by it and the CLI choice order is printed in help. |
| Living Spec membership and directory | `governance/usecases/id_convention.py:80-81` (`_LIVING_SPEC`, `_LIVING_DIRECTORIES`), `:454`, `:477`; `governance/usecases/traceability_link.py:40-41` (`docs/usecases/`, `docs/capabilities/`) | Fallbacks: `id_convention.py:509` (`"usecases" if kind is USECASE else "capabilities"`), `:200-222` (any kind other than capability and use case gets the architecture grammar and message), `:476-485` (any target outside `_LIVING_SPEC` gets the dated-partition remediation, milestones included). |
| Area-scoped directory (`<dir>/<area>/`, `area:` field) | `id_convention.py:200-221` (capability and use case branches set `expected_area`), `:507-509` | Only capability and use case. |
| Frontmatter-format scope | `governance/usecases/spec_format.py:59-60` (`SCOPE`, `NAMESPACE_SCOPE`) | `capabilities`, `usecases`, `proposals`, `roadmap`; namespaces only `capabilities`, `usecases`. |
| Heading-token kinds | `id_convention.py:66` (`_ID_TOKEN` lists `SPEC PLAN TASKS REC ADR FB CAP UC ARCH MS`) | `PROP`, `PADR`, `MAT` are absent by design. |
| Summary requirement | `governance/usecases/document_summary.py:29-30` (`REQUIRED`, `ANCHORS`) | Three values: always, anchor file only (proposal, spec), never. |
| Entrypoint-bearing kinds | `governance/usecases/code_entrypoints.py:42` (`_KINDS`) | Capability and use case. |
| Terminal statuses | `documents/repositories/index.py:157-161` (`TERMINAL_STATUSES`) | Feedback, decision, proposal (`ADR-terminal-statuses-are-historical`). |
| Relation field to accepted prefix | `governance/usecases/document_reference.py:43-52` (`EXPECTED_PREFIX`); `documents/models/model.py:11-14` (field lists) | Keyed by field, not by kind. `depends_on` is dual: `MS-` on milestones, `PROP-`/`SPEC-` anchors on units (`documents/services/dependencies.py:13-19`), which is behavior. |
| Bidirectional pair | `traceability_link.py:43-44,80-81` | `capabilities` on a use case and `usecases` on a capability. |
| Entrypoint-bearing paths | `entrypoints/services/paths.py:25-34` (`_LIVING_DIRECTORIES = ("docs/capabilities/", "docs/usecases/")`), read by `code_entrypoints.py:60-63`, `entrypoints/services/derive.py:92`, `scope/usecases/inputs.py:153` | A second copy of the entrypoint-bearing set, keyed by path; must derive from the rows or a new kind passes `_KINDS` and is skipped by path. |
| Default status at fix time | `spec_format.py:316-322` (`planned` for `MS-`, `open` for `FB-`, else `draft`) | Per-kind default; the `else` is a fallback. |
| Milestone status vocabulary and `created_at` requirement | `spec_format.py:158-170` | Per-kind format facts of `RULE-spec-format`. |
| Retired ID forms and remediation text | `ids.py:54-56` (`_LEGACY_REF`); `id_convention.py:82-85` (`_REFERENCE_REMEDIATION`) | Text is a rule message; it must stay byte-identical. |

## 2. Facts that stay kind-specific behavior (Q1)

| Behavior | Places |
| --- | --- |
| Path and stem grammar per kind: dated partitions (ADR, spec bundle files, feedback in three locations), `CAP-<AREA>-<slug>` stem, arc42 chapter set, global-only milestones | `id_convention.py:124-245`, `:248-302` |
| Spec bundle file set and `reconcile_id` field | `id_convention.py:76`, `:146-154` |
| Unit anchors (proposal and spec anchor files) and their relation rules (`depends_on`, `milestone`, provenance) | `documents/models/model.py:117-122`; `documents/models/parse.py:69-80`; `documents/services/dependencies.py` |
| Spec lifecycle, task progress, entrypoint derivation | `documents/usecases/browse.py:189-195`; `entrypoints/usecases/derive.py:73`; `governance/usecases/spec_lifecycle.py` |
| Proposal planning state and fields, feedback fields and severity order | `documents/usecases/browse.py:104-145` |
| Milestone hygiene, roadmap membership, dependency cycles | `governance/usecases/hygiene.py:60-80`; `proposals/usecases/roadmap.py:10-30`; `document_reference.py:158-190`; `documents/repositories/index.py:223` |
| Index cache record validation | `documents/repositories/memo.py:205,279` (reads `kind_of`, unaffected by where the table lives) |

Relation facts that are not per-row: `depends_on` takes `MS-` on milestones and `PROP-`/`SPEC-` anchors on units
(`documents/services/dependencies.py:12`, handled before `EXPECTED_PREFIX`), and the traceability pair
(`traceability_link.py:43-44,91-94`) is one relation between two kinds with its labels.

The first search covered `Kind.` and `kind_of` uses only; historical Git `cfc82a4cb3d651c38c61b6a4da880be9ebfbe2fd:docs/proposals/PROP-table-driven-document-kinds/envelopes/challenger-01.yaml` findings 1 and 2 added the
path- and prefix-keyed facts above. Development repeats the search for directory literals and prefix strings
before it starts.

`scope/usecases/inputs.py:62` defines an unrelated `kind_of` (path granularity), not a document kind.

## 3. Viewer (Q3)

From historical Git `cfc82a4cb3d651c38c61b6a4da880be9ebfbe2fd:docs/proposals/PROP-table-driven-document-kinds/envelopes/scout-01.yaml`. The viewer parses documents in the browser and never runs a repository's devkit
(`CAP-VIEW-repository-viewer` section 4). Its kind knowledge is front-end constants:
`frontend/src/lib/api/documents.ts:246` (cross-reference link prefixes), `:268-296` (`bookGroup`, `bookGroups`),
`features/knowledge/KnowledgeViews.svelte:169-170,229-236,255`, `api/roadmap.ts:37,63,97-98`,
`features/dashboard/dashboard.ts:109-164`, `api/planning.ts:17`. Python browse code knows only the dashboard
sections and the `PROP-`/`MS-`/`feedback/` path patterns (`features/browse/repositories/worktree.py:131-172`). The
viewer has no dependency on `devkit-spec`, no payload carries a kind, and autohub hosts supply their own
`RepositoryDataSource`, so only a definition inside the front-end bundle reaches them.

The link regex at `documents.ts:246` lists `CAP US ARCH ADR PROP SPEC PLAN TASKS REC MAT PADR`: `US` is the
retired use case prefix, and `UC`, `FB` and `MS` references are not linked today.

`bookGroup` also hard-codes `docs/glossary.md`, which `SPEC-foundation-documents` moves; that proposal does not own
the viewer front end.

## 4. Typing constraint (Q2)

`Kind` members are referenced statically (`Kind.SPEC`, `Kind.MILESTONE` and others, 51 references outside `ids.py` and tests). An enum built
at runtime from a table (`StrEnum("Kind", rows)`) has no members Pyright can see, so those references would fail
`just check`. The table therefore keys on a declared `Kind` and an import-time or unit check requires exactly one row
per member; `PREFIXES` and `ID_SOURCE` derive from the rows.

## 5. Baseline probe (Q4)

Run twice at `96df5d86` in the Planning worktree (outputs in the ignored `.probe/`):

- `devkit spec list --all-namespaces -n 0 --format json` (93,815 bytes), `devkit rules check --format json` and
  `devkit spec search "document kind" --format json` were byte-identical between runs, so a before/after diff is
  usable.
- `devkit rules check` reports no violation on this repository, so the repository comparison proves nothing about
  rule messages on bad input. Many existing rule tests match message fragments
  (`bundles/spec/bundle/rules/id_convention/tests/test_rule.py:24-25`), and none asserts the milestone path
  remediation, so they do not prove byte parity either. Parity needs a characterization fixture workspace with one
  violation per rule branch per kind, whose `devkit rules check --format json` output and `devkit rules fix` diff
  are captured before the first code change, plus the `devkit spec list --help` and `devkit spec search --help`
  text (kind choice order).
- A development worker can take the baseline in its own worktree: its starting head is the base, so it captures the
  three outputs before its first code change and compares them after.

## 6. Development characterization (Q4)

Captured by the development worker in its worktree (outputs in the ignored `scratch/char/`):

- Fixture: a fresh Git workspace synced with the `spec` bundle, a registered `pkg` namespace and 53 Markdown
  documents with one violation per rule branch per kind (path, stem, month, frontmatter, `id`/`reconcile_id`, area,
  heading token, same-kind heading, duplicate and retired-reference branches of `RULE-id-convention`; the format,
  effort, namespace and milestone branches of `RULE-spec-format`; summary, entrypoint, relation-field and
  traceability cases; terminal documents). It yields 137 violations across eight rules, and the fix applies 51
  fixes.
- `before`: run at the starting head `6a19ff5f` before the first code change; `before2`, a second run, was
  byte-identical. Captured: the fixture's `devkit rules check --format json`, `devkit rules fix` output and Git
  diff, `devkit spec list` (all namespaces, per kind, text) and `devkit spec show`; on the repository,
  `devkit spec list --all-namespaces -n 0 --format json`, `devkit spec search "document kind" --format json` and
  `devkit rules check --format json`; the `--help` text of `devkit spec list`, `devkit spec search`, `devkit rules`
  and `devkit rules check`.
- `after`: run at the final head. The repository captures read a snapshot of the starting head's tree
  (`git archive 6a19ff5f`, synced, with the `plan-ux-documentation` branch the planning state reads), so the unit's
  own document edits do not enter the comparison. `diff -r` of `before` and `after`, excluding the fixture
  workspaces, is empty.
