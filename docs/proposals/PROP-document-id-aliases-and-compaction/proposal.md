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
document or decision breaks every reference written with the old ID: `RULE-document-reference` reports each as
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
- **Document aliases** (`PADR-document-id-aliases`): Living Spec kinds `CAP`, `US`, `ARCH`, `ADR`, `MAT` and `MS`
  may declare aliases with their own prefix; proposal and spec-bundle kinds may not. Aliases are unique against
  every declared ID and every other alias.
- **One lookup**: `DocumentIndex` gains one alias-aware lookup used by every identity check; `devkit spec resolve`
  and `devkit spec refs --direction in` report alias hits, and `devkit spec search` pins an exact alias match. The
  devkit-agt rules catalog stays exact-ID.
- **Alias references**: a fixable error in current documents, rewritten by `devkit rules fix`; historical files
  (completed spec bundles, done or dropped milestones) resolve silently and are never rewritten.
- **Handoff**: a graduating PADR's `ADR-<slug>` is refused when it equals a declared alias.
- **Playbooks** (`PADR-playbook-aliases-as-identifiers`): playbook `aliases` stop being search keywords and become
  identifiers; search ranks `name` and `description` only. Breaking change in place, no migration. What a playbook
  alias identifies is open (section 5).

## 3. Proposed Design & Impact

### 3.1 Document aliases (`CAP-DOCS-document-model`, `CAP-DOCS-document-lookup`)

- `aliases: [<PREFIX>-<old-slug>, ...]` on a `CAP`, `US`, `ARCH`, `ADR`, `MAT` or `MS` document (namespace documents
  included). Each item is a well-formed ID with the declaring document's prefix, not its own ID, not repeated. A
  wrong shape or kind is a recorded issue reported by `RULE-document-reference`.
- `DocumentIndex` (`packages/devkit-spec/src/devkit_spec/features/documents/repositories/index.py`) indexes aliases
  as secondary identifiers beside `by_id`; its alias-aware lookup returns the document and whether an alias was used.
  A collision with a declared ID of any status, or with another document's alias, is reported on both documents.
- Callers moved to the lookup: `RULE-document-reference` resolution and handed-off checks, the traceability link
  rule, dependencies, browse, roadmap, scaffold, specs, handoff (including the graduating-ADR clash check) and the
  proposals rewrite service.

### 3.2 Alias references (`RULE-document-reference`)

- An alias reference resolves. In a current document it is an error that `devkit rules fix` rewrites to the canonical
  ID in frontmatter and prose, through `services/rewrite.py`; in a historical file it is skipped.
- Incoming references (`devkit spec refs <canonical> --direction in`) include alias-written references.
- `devkit spec resolve <alias>` reports the canonical ID and the alias; `CAP-DOCS-document-search` pins an exact
  alias match like an exact ID.

### 3.3 Playbook aliases (`CAP-DIST-context-and-playbooks`, `ARCH-08-2-resource-taxonomy`)

- `packages/devkit-dist/src/devkit_dist/features/distribution/services/bundles/playbooks.py` validates `aliases` as
  identifiers (form set by q1), and `services/bundles/manifest.py` checks them unique against the bundle's playbook
  IDs and the other playbooks' aliases.
- `usecases/playbook_search.py` indexes `name` and `description` only; results keep `aliases` as identity metadata
  (`models/results.py`). `usecases/playbook_get.py` resolves an alias as q1 decides.
- `services/installation/playbook_skill.py` (the projected `devkit-playbook` skill text) and the search service
  docstring (`features/search/services/index.py`, wording only) stop describing aliases as search text;
  `CAP-SRCH-document-search` changes its metadata example the same way.
- The seven bundled playbooks with keyword lists (devkit-spec `brownfield-adoption` and `feedback-hygiene`,
  devkit-agt `skill-authoring` and `agent-guide-authoring`, devkit-catalog `drift-reconciliation` and
  `weekly-report`, devkit-starter `review`) drop them, moving any phrase worth keeping into the description.
  The repository's projected copies are refreshed by `devkit sync`.

## 4. Lifecycle & Verification

- Unit tests (`packages/devkit-spec/tests/unit/features/documents/`): alias parsing and shape issues, refused kinds
  and foreign prefixes, collisions with declared IDs of any status and with other aliases, the alias-aware lookup.
- Governance tests (the rule's own tests and `tests/unit/features/governance/`): alias references as fixable errors in
  current documents, the fix result, historical files byte-identical after `devkit rules fix`, relation-field prefix
  typing kept, traceability with an alias.
- Handoff test: a graduating ADR ID equal to a declared alias is refused.
- CLI tests: `devkit spec resolve`, `devkit spec refs --direction in` and `devkit spec search` for an alias.
- devkit-dist tests (`packages/devkit-dist/tests/`): keyword aliases refused, identifier aliases accepted, alias
  collisions refused at manifest validation, search ignores aliases, `devkit playbook get` per q1.
- `just rules-check` clean on the repository; no file under `docs/decisions/` in the diff.

## 5. Open Decisions

- **q1 Playbook alias target** (`envelopes/worker-02.yaml`): what a playbook alias identifies and whether
  `devkit playbook get` resolves it.
