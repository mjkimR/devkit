# Spike findings (Planning round 1)

Evidence for the spike questions of `SPEC-foundation-documents`, read at base `96df5d86` in the
`plan-foundation-documents` worktree. Probe: a copy of `.devkit/` and `docs/` (without `proposals/`) under the ignored
`.probe/repo/`, with a namespace `alpha` registered and ID-free files added, checked with `devkit rules check` and
`devkit spec search` from this worktree's environment.

## F1. The document index and search see only ID-bearing files

- `parse_document` derives the kind from the `id` (or `reconcile_id`) prefix; a file without a well-formed ID "is not
  a document (a README, a glossary, a guide) and is silently left out" (`CAP-DOCS-document-model` rule 3.2).
- `search_documents` takes its candidates from `index.documents`; every hit carries `id`, `kind` and `status`
  (`CAP-DOCS-document-search` sections 4.2 and 4.3: `[HIT: <id> ...]`).
- Probe: `devkit spec search "product purpose users principles" --mode lexical` and a search for the exact path
  `docs/foundation/product.md` return no hit for `docs/foundation/product.md`; path pinning applies only to indexed
  documents.
- Consequence: "search indexes the group" through an English `summary` cannot hold for ID-free files without a change
  to the index or a second candidate source in search, and the hit format then needs a value for `id` and `kind`.

## F2. What the spec rules check in an ID-free file under `docs/`

| Check | Root `docs/foundation/x.md` | `docs/packages/<name>/foundation/x.md` | Source |
| --- | --- | --- | --- |
| Date- or number-based references (`ADR-0001`, `SPEC-20261001-old`) | reported | reported | `RULE-id-convention` `_reference_files`: every `docs/` file except materials |
| Unresolved ID reference (`CAP-DOCS-missing-one`) | not reported | not reported | `RULE-document-reference` walks indexed documents only |
| Summary present / English | not checked (a Hangul summary passed) | not checked | `RULE-document-summary` `REQUIRED` lists kinds |
| Path, ID and heading convention | not targeted | not targeted | `RULE-id-convention` `_targets` lists fixed directories |
| Relative Markdown links | checked | checked | `RULE-markdown-link` (devkit builtin) |

ID-free files in both locations pass the current rules (probe: no error besides the two planted legacy references).
Their own ID references are unchecked, so a foundation document citing a renamed capability drifts silently.

## F3. Every consumer of the glossary path

| Consumer | Path read today | Behavior if only the file moves |
| --- | --- | --- |
| `RULE-document-reference` `_glossary` | literal `docs/glossary.md` | Owner check silently stops (probe: a bad Owner in `docs/foundation/glossary.md` is not reported) |
| Search expansion `GLOSSARY_PATH` | literal `docs/glossary.yaml`, root only | Synonym expansion silently stops; `SPEC_GLOSSARY_INVALID` text names the old path (`base/errors.py`) |
| `docs-skeleton` seed (`seed/docs/glossary.md`, `glossary.yaml`, `README.md`, `architecture/README.md`) | seeded once where absent | An existing consumer gets a second, new glossary at the new path on its next sync; this repository's receipt `.devkit/installation.json` changes |
| `living-spec-writing` (Glossary section, package glossary rule), `architecture-writing` (arc42 section 12), `spec-sync` skill, brownfield `migration.md`, `document_reference/guide.md` | text names `docs/glossary.md` | Guidance points to a missing file |
| `id_convention.py` remediation text "decisions and glossary have their own directories" | text | Still true after the move |
| Viewer `bookGroup` (`packages/devkit-viewer/frontend/src/lib/api/documents.ts`) | literal `docs/glossary.md` | The glossary falls into the `Overview` group; the committed build under `devkit_viewer/static/` must be rebuilt |
| Release handbook `scripts/handbook.py` (`collect_status`, `render_glossary`) | `git show <source_commit>:docs/glossary.md` | At a later refresh the generated glossary page is silently empty and `HANDBOOK_TERM_MISSING` never fires; the current snapshot (`source_commit` 5e71d74c, v0.1.4) still has the old path |
| Handbook tests `tools/devkit-dev/tests/integration/test_handbook_script.py` | fixture `docs/glossary.md` | Must cover both paths if the script reads both |
| Living Spec: `docs/README.md`, `docs/architecture/README.md` (link `../glossary.md`), `CAP-DOCS-document-model`, `CAP-GOV-spec-rules`, `CAP-DOCS-document-search`, `CAP-HARN-agent-guidance` (seeded tree), `CAP-DLV-release-handbook`, `CAP-DLV-delivery-workflows` (reflection includes `docs/glossary.md`) | prose and one relative link | `RULE-markdown-link` reports the link; the rest drifts |
| Handbook pages `handbook/<lang>/areas/documents.md` | prose `docs/glossary.yaml` | Release snapshot, refreshed only at a release (out of scope) |

The handbook reads a pinned historical commit, so reading only the new path breaks a refresh across the move. Reading
the new path first and the old one when the commit lacks it is history access, not a legacy reader of a current
format (`AGENTS.md` Compatibility).

## F4. Name collision

"Foundation" already names devkit's lowest code layer in this repository: "shared foundation" (`devkit-core`,
`ARCH-05-1-containers`, `ARCH-05-2-components`, `CAP-GOV-rules-engine` section 4, `AGENTS.md`), "foundation modules"
(`ARCH-01-introduction-and-goals`). It is not a glossary term. The proposal's own wording is "project-wide
background". "Context" collides with bundle context (`devkit get-context`); `guides/` is a top-level directory here.

## F5. Reading path for agents (Q3)

- The spec constitution is loaded once per agent context by every role, workers and nested roles included
  (`devkit get-context spec`); a one-line pointer there reaches every context at a constant cost.
- The `spec` skill's intake runs only for a user's own request, never for a worker turn (`spec` skill, Route step 1),
  so a step placed there does not reach Development workers.
- `living-spec-writing` is read only before writing `docs/` or `specs/`, not before code or interface work.
- No mechanism bounds a file's size beyond `RULE-file-length` (devkit-dev, repository-local).

## F6. Overlap with the parallel proposals (both on main at `96df5d86`)

| Surface | `PROP-table-driven-document-kinds` | `SPEC-ux-documentation` | This proposal |
| --- | --- | --- | --- |
| Kind set (`models/ids.py`, `id_convention.py` `_LIVING_DIRECTORIES`) | replaces constants with one table; no new kind, no rule-code change | adds a UX kind as a table row | adds no kind (excludes); touches `_reference_files` scope only if foundation references are checked |
| Index and search (`repositories/index.py`, `usecases/search.py`) | reads directories and membership from the table | adds the kind to browsing and search | moves `GLOSSARY_PATH`; may add ID-free candidates (F1) |
| `RULE-document-reference` | relation-field kinds from the table | new link fields | glossary Owner path; optional reference check of foundation files |
| `CAP-DOCS-document-model`, `CAP-GOV-spec-rules` | table as the single definition | UX kind entry and coverage rules | foundation group and glossary path |
| Viewer `documents.ts` `bookGroup` and its committed build | front end reads kind definitions | UX documents in browsing | glossary group path (F3) |
| Glossary | none | screens cite glossary terms (option 6b) | moves the glossary |
| Style content | none | excludes visual styling and theming | the group is where a style direction lives |

Order: `PROP-table-driven-document-kinds` first (user decision recorded in the Host's handoff), then this proposal,
then `SPEC-ux-documentation`, so the UX guidance names the glossary at its new path and can point to foundation style
documents instead of restating them. If this proposal adds a kind or touches `bookGroup`, it must build on the table's
definitions rather than add constants beside them.
