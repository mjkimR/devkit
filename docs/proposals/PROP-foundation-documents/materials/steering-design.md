# Steering design (Planning round 2)

Input: the `user` direction recorded in `envelopes/answer-01.yaml` (name `steering`, one flat directory, progressive
loading through `devkit get-context spec`, a cap rule, the glossary moves, search unchanged). Read at base
`96df5d86`.

## D1. How `devkit get-context` obtains the steering list

`GetContext.execute` (`packages/devkit-dist/src/devkit_dist/features/distribution/usecases/context.py`) returns the
bundle's constitution and the headers of its synchronized instructions, read through the receipt and the shared
project lock (`CAP-DIST-context-and-playbooks` section 2). `devkit-dist` is SDD-agnostic (`ARCH-05-1-containers`
section 2.4; `AGENTS.md`: `devkit-dist` never imports `devkit_agt`).

| Option | Cost | Risk |
| --- | --- | --- |
| A. The bundle manifest declares a workspace directory of context documents; get-context lists `path`, `title`, `summary` of each Markdown file in it (chosen) | One manifest field, one result key, validation in `CAP-DIST-manifest-spec` | A second bundle may declare the same directory; listing is per bundle, so no conflict |
| B. An entry-point provider (`devkit.context` group) that `devkit-spec` registers | Plugin contract, discovery, error mapping | Code in a content bundle's package runs inside get-context; more surface than the need |
| C. A literal `docs/steering` in `devkit-dist` | Smallest code | Puts an SDD concept into the SDD-agnostic distribution package |
| D. Sync renders the list into the managed constitution | No get-context change | Stale between syncs; the `user` chose run-time reading |

Files are project-owned workspace files, not receipt entries, so get-context reads them directly (no hash check) and
under the same shared lock. A file whose frontmatter is malformed or lacks `title` or `summary` is listed with the
missing value as `null`; `RULE-steering-documents` reports it, so get-context never fails a context load for a
project document.

## D2. Sizing the caps

| Measure | Value |
| --- | --- |
| `docs/glossary.md` today | 7808 bytes (56 lines), before the steering frontmatter |
| `docs/glossary.yaml` | 1114 bytes (not Markdown; not counted) |
| Seeded `glossary.md` | 917 bytes |
| Skill document budget (`test_bundle_budgets.py`, `RULE-skill-document-size`) | 12288 bytes |
| `RULE-document-summary` length cap | 300 characters |
| Spec constitution today (`AGENTS.md.jinja`) | 4677 bytes |

Always-loaded cost per context: at most `max_files` x (path + title + 300-character summary), about 400 bytes per
file. Ten files is about 4 kB, the size of the constitution itself.

## D3. Glossary with steering frontmatter

- `RULE-document-reference` `_glossary` scans visible table lines; a frontmatter block holds no five-column table.
- `scripts/handbook.py` `glossary_terms` scans `## ` headings and table rows; frontmatter lines match neither.
- Without an `id` the file stays outside the document index (`CAP-DOCS-document-model` rule 3.2).

## D4. Namespace copy

No real need found: this repository registers no namespace, package glossaries already live at
`docs/packages/<name>/glossary.md` (`living-spec-writing`), and a per-namespace list would multiply the always-loaded
cost by the number of packages. Dropped.
