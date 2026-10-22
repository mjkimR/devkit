---
id: PROP-document-id-aliases-and-compaction
title: Document and Playbook ID Aliases
summary: "Introduces an optional aliases frontmatter field of previous or alternate IDs on Living Spec documents, resolved through one alias-aware DocumentIndex lookup and rewritten to canonical IDs by devkit rules fix, and gives playbook aliases the same identifier meaning."
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

A Living Spec document is found only by its exact ID. Renaming or merging a capability, story, architecture
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
- **Document aliases** (`PADR-document-id-aliases`): `CAP`, `US`, `ARCH` and `MS` documents may declare aliases
  with their own prefix. `ADR` is refused (approved ADRs are append-only, so an ADR alias could never be used), `MAT`
  is refused (materials are not rule-checked) and so are proposal and spec-bundle kinds. Aliases are identity, not
  references. A declared ID always wins; an alias resolves only when unambiguous, otherwise the collision is reported
  and nothing is rewritten.
- **One canonical mapping**: `DocumentIndex` maps a written target to its canonical document; `resolve()` and every
  identity check use it. `devkit spec resolve` reports `alias=`, `devkit spec refs` counts and groups alias hits, and
  `devkit spec search` pins an exact alias match. The devkit-agt rules catalog stays exact-ID.
- **Alias references**: a fixable error in current documents, rewritten by `devkit rules fix`; historical files
  (completed spec bundles, done or dropped milestones) and decision records (ADRs and PADRs) resolve silently and are
  never rewritten.
- **Handoff**: unchanged; no alias can equal a graduating `ADR-<slug>`.
- **Playbooks** (`PADR-playbook-aliases-as-identifiers`): playbook `aliases` stop being search keywords and become
  identifiers; search ranks `name` and `description` only. Breaking change in place, no migration. What a playbook
  alias identifies is open (section 5).

## 3. Proposed Design & Impact

### 3.1 Document aliases (`CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`)

- `aliases: [<PREFIX>-<old-slug>, ...]` on a `CAP`, `US`, `ARCH` or `MS` document (namespace documents included).
  Each item is a well-formed ID with the declaring document's prefix, not its own ID, not repeated. A wrong shape or
  a refused kind is a recorded issue reported by `RULE-document-reference`. `aliases` is not a relation field.
- `DocumentIndex` (`packages/devkit-spec/src/devkit_spec/features/documents/repositories/index.py`) keeps the aliases
  beside `by_id` and exposes one canonical mapping returning the document and the alias used. A declared ID always
  wins; an alias resolves only when exactly one document declares it and none has it as its ID. A collision is
  reported on every document involved and leaves references unresolved or unchanged.
- Callers moved to the mapping, found by an audit of `by_id`, `.resolve(` and `== <doc>.id` across devkit-spec:
  `resolve()` and `incoming()` themselves; `RULE-document-reference` resolution, handed-off checks and `depends_on`
  cycle graph; `documents/services/dependencies.py`; the traceability link rule including its reverse-link
  comparison; hygiene milestone membership; browse (`refs` grouping); roadmap; scaffold; specs; entrypoints
  `--target` derivation; handoff; the proposals rewrite service.

### 3.2 Alias references (`RULE-document-reference`)

- An alias reference resolves. In a current document it is an error that `devkit rules fix` rewrites to the canonical
  ID in frontmatter and prose, through `services/rewrite.py`. In historical files and decision records (ADRs under
  `docs/decisions/`, PADRs) it resolves silently and is never rewritten. A glossary Owner naming an alias is
  reported, not fixed.
- `devkit spec resolve <alias>` prints the canonical `[DOCUMENT: ...]` with `alias=<alias>` and an `alias` JSON field,
  without a notice; `devkit spec refs <canonical> --direction in` includes alias-written references and
  `--direction out` groups an alias with its canonical ID; `CAP-DOCS-document-search` pins an exact alias match.

### 3.3 Playbook aliases (`CAP-DIST-context-and-playbooks`, `ARCH-08-2-resource-taxonomy`)

- `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/playbooks.py` validates `aliases` as
  identifiers (form set by q1), and `services/bundles/manifest.py` checks them unique against the bundle's playbook
  IDs and the other playbooks' aliases; retrieval checks the effective headers again, since overrides can change them.
- `usecases/playbook_search.py` indexes `name` and `description` only; results keep `aliases` as identity metadata
  (`models/results.py`). `usecases/playbook_get.py` resolves an alias as q1 decides.
- `services/installation/playbook_skill.py` (the projected `devkit-playbook` skill text) and the search service
  docstring (`features/search/services/index.py`, wording only) stop describing aliases as search text;
  `CAP-SRCH-document-search` changes its metadata example the same way.
- The seven bundled playbooks with keyword lists (devkit-spec `brownfield-adoption` and `feedback-hygiene`,
  devkit-agt `skill-authoring` and `agent-guide-authoring`, devkit-catalog `drift-reconciliation` and
  `weekly-report`, devkit-starter `review`) drop them, moving any phrase worth keeping into the description.
  The repository's projected copies and `.devkit/installation.json` are refreshed by `devkit sync`.

## 4. Lifecycle & Verification

- Unit tests (`packages/devkit-spec/tests/unit/features/documents/`): alias parsing and shape issues, refused kinds
  (`ADR`, `MAT`, lifecycle kinds) and foreign prefixes, `aliases` entries not counted as references, declared-ID
  precedence, collisions with declared IDs of any status and with other aliases (including an ID created after the
  alias), the canonical mapping.
- Governance tests (the rule's own tests and `tests/unit/features/governance/`): alias references as fixable errors in
  current documents, the fix result, historical files and an ADR or PADR citing an alias byte-identical after
  `devkit rules fix`, a self-mention, relation-field prefix typing kept, traceability with an alias fixed without a
  duplicate entry, hygiene with an `MS` alias, a `depends_on` cycle through an alias.
- CLI tests: `devkit spec resolve` (`alias=` and JSON field), `devkit spec refs --direction in` and `--direction out`
  with an alias and the canonical ID mixed, `devkit spec search`, entrypoints `--target` with an alias.
- devkit-dist tests (`packages/devkit-dist/tests/`): keyword aliases refused, identifier aliases accepted, alias
  collisions refused at manifest validation and, through an override, at retrieval; search ignores aliases;
  `devkit playbook get` per q1.
- `just rules-check` clean on the repository; no file under `docs/decisions/` in the diff.

## 5. Open Decisions

- **q1 Playbook alias target** (this turn's worker envelope): what a playbook alias identifies and whether
  `devkit playbook get` resolves it. Options: (a, recommended) a previous asset ID in the same bundle, resolved by
  `get` with the exact ID first and ambiguity refused; (b) a validated identifier list that nothing resolves; (c) no
  playbook aliases at all, removing the field.
