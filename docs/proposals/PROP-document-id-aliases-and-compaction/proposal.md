---
id: PROP-document-id-aliases-and-compaction
title: Document and Playbook ID Aliases
summary: "Introduces an optional aliases frontmatter field of previous or alternate IDs on every ID-bearing document, resolved through one alias-aware DocumentIndex lookup and rewritten to canonical IDs by devkit rules fix, and gives playbook aliases the same identifier meaning."
status: reviewing
created_at: 2026-10-21
target_area: capabilities/documents/
priority: high
size: L
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - packages/devkit-dist/src/devkit_dist/features/distribution/
    - packages/devkit-dist/src/devkit_dist/features/search/services/index.py
    - packages/devkit-dist/tests/
    - docs/capabilities/delivery/CAP-DLV-proposal-incubation.md
    - docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md
    - docs/capabilities/search/CAP-SRCH-document-search.md
    - docs/architecture/ARCH-08-2-resource-taxonomy.md
    - packages/devkit/src/devkit_agt/bundles/authoring/bundle/playbooks/
    - packages/devkit-catalog/src/devkit_catalog/maintenance/bundle/playbooks/
    - packages/devkit-starter/src/devkit_starter/bundle/playbooks/
    - .devkit/installation.json
  excludes:
    - docs/decisions/
    - packages/devkit/src/devkit_agt/features/
    - packages/devkit-viewer/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-document-id-aliases-and-compaction] Document and Playbook ID Aliases

## 1. Background & Hypothesis

A document is found only by its exact ID. Renaming or merging a capability, story, architecture
document or milestone breaks every reference written with the old ID: `RULE-document-reference` reports each as
unresolved and `devkit spec resolve` finds nothing. The only rename devkit handles is the handed-off `PROP-<slug>`
to `SPEC-<slug>` rewrite of the proposals lifecycle.

Playbooks already have an `aliases` frontmatter field, but it holds English search keywords that
`devkit playbook search` ranks. Introducing document ID aliases under the same name with another meaning would give
one field two concepts.

**Core hypothesis:** an optional `aliases` field of previous or alternate IDs, resolved by one alias-aware lookup and
rewritten to the canonical ID by `devkit rules fix`, lets documents be renamed without breaking references; giving
playbook `aliases` the same identifier meaning keeps one concept across devkit.

## 2. Planning Decisions

- **Scope narrowed** (answers to `envelopes/worker-01.yaml`): the proposal specifies ID aliases only. ADR compaction,
  the append-only amendment and ADR supersession checking (`supersedes`/`superseded_by` parsing, pairing and status
  checks, correcting drifted ADRs) are out of scope; the earlier supersession PADR is withdrawn (deleted unaccepted).
  No file under `docs/decisions/` changes. The ledger survey in `materials/ledger-evidence.md` is kept as Planning
  history only.
- **ADRs are not excluded** (user correction of the worker-01 q3 answer, which the second turn misapplied): "no ADR
  change" means only that refactoring or compacting existing ADR files is out of scope, not that ADRs are left out of
  the aliases specification.
- **Document aliases** (`PADR-document-id-aliases`): `aliases` is one common frontmatter specification for every
  ID-bearing document kind (`CAP`, `US`, `ARCH`, `ADR`, `MS`, `MAT` and the lifecycle kinds `PROP`, `PADR`, `SPEC`,
  `PLAN`, `TASKS`, `REC`, `FB`); there is no kind-based refusal. The kind-independent rules hold for all: aliases
  carry the declaring document's own prefix, are identity and not references, a declared ID always wins, an alias
  resolves only when unambiguous and a collision is reported and nothing is rewritten. Where a kind has a validation
  gap, the PADR states how aliases behave there (materials: identity checked, their own references unchecked).
- **One canonical mapping**: `DocumentIndex` maps a written target to its canonical document; `resolve()` and every
  identity check use it. `devkit spec resolve` reports `alias=`, `devkit spec refs` counts and groups alias hits, and
  `devkit spec search` pins an exact alias match. The devkit-agt rules catalog stays exact-ID.
- **Alias references**: a fixable error in current documents, rewritten by `devkit rules fix`; historical files
  (completed spec bundles, done or dropped milestones) and decision records (ADRs and PADRs) resolve silently and are
  never rewritten.
- **Handoff**: carried aliases follow the handoff rename of their document (`PROP-` to `SPEC-` on `spec.md`, `PADR-`
  to `ADR-` on each promoted ADR), and the handoff refuses when a graduating `ADR-<slug>` or `SPEC-<slug>`, or a
  translated alias, equals an existing ID or alias.
- **Playbooks** (`PADR-playbook-aliases-as-identifiers`, answer to `envelopes/worker-02.yaml` q1): playbook `aliases`
  stop being search keywords and become previous asset IDs in the same bundle, resolved by `devkit playbook get`;
  search ranks `name` and `description` only. Breaking change in place, no migration.

## 3. Proposed Design & Impact

### 3.1 Document aliases (`CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`)

- `aliases: [<PREFIX>-<old-slug>, ...]` on any ID-bearing document (namespace documents included). Each item is a
  well-formed ID with the declaring document's prefix, not its own ID, not repeated. A wrong shape is a recorded
  issue. `aliases` is not a relation field.
- `DocumentIndex` (`packages/devkit-spec/src/devkit_spec/features/documents/repositories/index.py`) keeps the aliases
  beside `by_id` and exposes one canonical mapping returning the document and the alias used. A declared ID always
  wins; an alias resolves only when exactly one document declares it and none has it as its ID. A collision is
  reported on every document involved and leaves references unresolved or unchanged.
- Alias shape issues and collisions are identity checks of `RULE-document-reference`: they run over every indexed
  document, materials included, as the duplicate-ID check does today. The rule's reference checks still skip
  materials (`is_material`), so a reference written inside a material, alias or not, is neither reported nor
  rewritten; a reference to a material's alias from a checked document resolves and is fixed like any other.
- Callers moved to the mapping, found by an audit of `by_id`, `.resolve(` and `== <doc>.id` across devkit-spec:
  `resolve()` and `incoming()` themselves; `RULE-document-reference` resolution, handed-off checks and `depends_on`
  cycle graph; `documents/services/dependencies.py`; the traceability link rule including its reverse-link
  comparison; hygiene milestone membership; browse (`refs` grouping); roadmap; scaffold; specs; entrypoints
  `--target` derivation; handoff; the proposals rewrite service.

### 3.2 Alias references (`RULE-document-reference`)

- An alias reference resolves. In a current document it is an error that `devkit rules fix` rewrites to the canonical
  ID in frontmatter and prose, through `services/rewrite.py`. In historical files and decision records (ADRs under
  `docs/decisions/`, PADRs) it resolves silently and is never rewritten, whatever kind the alias belongs to. A
  glossary Owner naming an alias is reported, not fixed.
- `devkit spec resolve <alias>` prints the canonical `[DOCUMENT: ...]` with `alias=<alias>` and an `alias` JSON field,
  without a notice; `devkit spec refs <canonical> --direction in` includes alias-written references and
  `--direction out` groups an alias with its canonical ID; `CAP-DOCS-document-search` pins an exact alias match.

### 3.3 Handoff (`CAP-DLV-proposal-incubation`)

- A proposal's `aliases` are carried to `spec.md` with the `PROP-` prefix replaced by `SPEC-`; each promoted PADR's
  `aliases` are kept on its ADR with `PADR-` replaced by `ADR-`, so the own-prefix rule holds after the rename.
- The handoff's reference rewrite treats a reference written with a carried alias like one written with the old ID:
  rewritten to the new canonical ID in current documents, untouched in historical files and decision records.
- `_check_targets` (`features/proposals/usecases/handoff.py`) refuses, before any write, when a graduating
  `ADR-<slug>` or `SPEC-<slug>`, or a translated alias, equals an existing document ID or an existing alias.

### 3.4 Playbook aliases (`CAP-DIST-context-and-playbooks`, `ARCH-08-2-resource-taxonomy`)

- `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/playbooks.py` validates `aliases` as
  previous asset IDs (the `[a-z][a-z0-9-]*` manifest slug grammar, not frontmatter `name`), and `services/bundles/manifest.py` checks them unique against the bundle's playbook
  IDs and the other playbooks' aliases; retrieval checks the effective headers again, since overrides can change them.
- `usecases/playbook_search.py` indexes `name` and `description` only; results keep `aliases` as identity metadata
  (`models/results.py`). `usecases/playbook_get.py` resolves `<bundle>/<alias>`: an exact asset ID always wins;
  otherwise the alias resolves only when exactly one effective playbook header of that bundle (overrides included)
  declares it, and the result reports the canonical `id` and the alias used; an alias declared by more than one
  effective playbook is refused with a stable code. The `CAP-DIST-context-and-playbooks` sentence that `get` does no
  alias lookup and no fallback changes accordingly.
- `services/installation/playbook_skill.py` (the projected `devkit-playbook` skill text) and the search service
  docstring (`features/search/services/index.py`, wording only) stop describing aliases as search text;
  `CAP-SRCH-document-search` changes its metadata example the same way.
- The seven bundled playbooks with keyword lists (devkit-spec `brownfield-adoption` and `feedback-hygiene`,
  devkit-agt `skill-authoring` and `agent-guide-authoring`, devkit-catalog `drift-reconciliation` and
  `weekly-report`, devkit-starter `review`) drop them, moving any phrase worth keeping into the description.
  The repository's projected copies and `.devkit/installation.json` are refreshed by `devkit sync`.

## 4. Lifecycle & Verification

- Unit tests (`packages/devkit-spec/tests/unit/features/documents/`): alias parsing and shape issues on every kind
  (`CAP`, `ADR`, `MAT` and a lifecycle kind such as `PADR` among them), foreign prefixes, `aliases` entries not counted as references, declared-ID
  precedence, collisions with declared IDs of any status and with other aliases (including an ID created after the
  alias), the canonical mapping.
- Governance tests (the rule's own tests and `tests/unit/features/governance/`): alias references as fixable errors in
  current documents, the fix result, historical files and an ADR or PADR citing an alias byte-identical after
  `devkit rules fix`, a self-mention, relation-field prefix typing kept, traceability with an alias fixed without a
  duplicate entry, hygiene with an `MS` alias, a `depends_on` cycle through an alias, a
  material's alias collision reported while a reference inside a material stays unchecked, a reference to an `ADR`
  alias from a current document fixed.
- Handoff tests: a proposal's and a PADR's aliases carried with the translated prefix, a reference written with a
  carried alias rewritten, refusal when a graduating `ADR-<slug>` or `SPEC-<slug>` or a translated alias equals an
  existing ID or alias.
- CLI tests: `devkit spec resolve` (`alias=` and JSON field), `devkit spec refs --direction in` and `--direction out`
  with an alias and the canonical ID mixed, `devkit spec search`, entrypoints `--target` with an alias.
- devkit-dist tests (`packages/devkit-dist/tests/`): keyword aliases refused, identifier aliases accepted, alias
  collisions refused at manifest validation and, through an override, at retrieval; search ignores aliases;
  `devkit playbook get` with an exact ID, an alias, an exact ID shadowing an alias and an ambiguous alias
  (stable refusal code).
- `just rules-check` clean on the repository; no file under `docs/decisions/` in the diff.

## 5. Open Decisions

None. The playbook alias target was decided in `envelopes/answer-02.yaml`.
