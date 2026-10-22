---
id: PROP-document-id-aliases-and-compaction
title: Document ID Aliases and ADR Compaction
summary: "Introduces an optional aliases frontmatter field across Living Spec documents to preserve referential integrity during renaming and compaction, and defines an ADR compaction procedure to consolidate fragmented architectural decision chains."
status: reviewing
created_at: 2026-10-21
target_area: capabilities/documents/
priority: high
size: M
planning_effort: medium
dev_effort: medium
boundaries:
  owns:
    - packages/devkit-spec/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - docs/decisions/
  excludes:
    - packages/devkit-dist/src/devkit_dist/features/search/
    - packages/devkit-viewer/
task_kind: feature
workflow: sdd-proposal
---

# [PROP-document-id-aliases-and-compaction] Document ID Aliases and ADR Compaction

## 1. Background & Hypothesis

Architecture Decision Records (ADRs) under `docs/decisions/` are an append-only ledger: `docs/decisions/README.md`
(and its seed copy), the `spec-sync` skill and the `spec:living-spec-writing` instruction state that approved ADRs are
never deleted or retroactively modified, and a change is a new ADR linked through `supersedes` and `superseded_by`.

Rapid development produced 74 ADRs in one month (`materials/ledger-evidence.md`). Two problems follow:

1. **Supersession drift (measured)**: the supersession fields are not checked by any rule. `parse_document` skips an
   ADR's `supersedes`, and `superseded_by` is not read. Five ADRs replaced by a later ADR still say
   `status: accepted`, so an agent filtering decisions by status reads replaced decisions as current
   (`ADR-integration-approval-asserted`, mentioned 38 times, is one of them).
2. **Fragmented chains (expected to grow)**: replacement chains (currently at most three records) make a reader
   traverse several ADRs to learn the current decision. Consolidating them into one record by removing the old files
   would break every reference to the removed IDs.

**Core hypothesis:** checked supersession makes the ledger's current state reliable at once, and an alias mechanism
for ADR IDs lets a governed compaction consolidate a chain into one record without breaking references.

## 2. Planning Decisions

- **Supersession integrity** is in scope whatever the compaction decision
  (`PADR-adr-supersession-integrity`): kind-aware provenance on ADRs, a fixable reverse-field check, and the
  drifted records corrected.
- **Alias references** (when aliases are kept): an alias reference in a current document is a fixable error that
  `devkit rules fix` rewrites to the canonical ID, following the handed-off `PROP-<slug>` precedent; historical
  files (completed spec bundles, done/dropped milestones) resolve the alias silently and are never rewritten. The
  bracket-versus-code-span question is already answered by `services/rewrite.py`.
- **Kinds**: aliases are accepted on ADRs only, and an alias must carry the `ADR-` prefix. Other kinds keep exact
  IDs; a later proposal may extend this with resolved-kind typing.
- **One lookup**: `DocumentIndex` gains one alias-aware lookup that every identity check uses (the rule's
  resolution and handed-off checks, traceability, dependencies, browse, roadmap, scaffold, specs, handoff and the
  proposals rewrite service); `devkit spec resolve` reports an alias hit with the canonical ID and the alias, and
  `devkit spec refs <canonical> --direction in` includes references written with an alias. The devkit-agt rules
  catalog stays exact-ID.
- **Handoff**: a graduating PADR's `ADR-<slug>` is refused when it equals a declared alias, as it is for a declared ID.
- Open decisions for the user are listed in section 5.

## 3. Proposed Design & Impact

### 3.1 ADR supersession integrity (`PADR-adr-supersession-integrity`)

- On an ADR, `supersedes` is a list of `ADR-` IDs (a scalar is read as a one-element list) and `superseded_by` one
  `ADR-` ID; both are provenance, outside the current reference graph. Unit-anchor provenance is unchanged.
- A declared superseded ADR must say `status: superseded` and name its successor in `superseded_by` (fixable); a
  `superseded_by` target must list the ADR in its `supersedes` (by hand).
- Development corrects the drifted records in `docs/decisions/`.

### 3.2 ADR aliases (`CAP-DOCS-document-model`) — subject to decision q1

- An ADR may declare `aliases: [ADR-<old-slug>, ...]`. An alias may equal no declared ID of any status and no other
  alias; it must also appear in the ADR's `supersedes`, so the redirect is always backed by provenance.
- `DocumentIndex` keeps `by_alias` beside `by_id`; the alias-aware lookup returns the document and whether it was
  reached through an alias.
- `RULE-document-reference` treats an alias reference as resolved, reports it as a fixable error in current
  documents and skips it in historical ones.

### 3.3 ADR compaction procedure — subject to decision q1

1. **Scope**: group ADRs that are iterations of the same decision (a supersession chain or a set of refinements).
2. **Consolidation**: author one new ADR through the normal proposal path, whose `Context` and `Considered Options`
   summarize why the earlier options were discarded.
3. **Provenance**: list every consolidated ID in `supersedes` and `aliases`.
4. **Removal**: delete the consolidated files (Git history keeps them), run `devkit rules fix` to retarget current
   references, and search `packages/` (bundle workflows, skills, READMEs, tests) for the retired IDs, which the
   document index does not cover, retargeting or striking them through.
5. **Check**: `devkit rules check` is clean; `devkit spec resolve <old-id>` reports the consolidated ADR.

The procedure lives in the spec bundle's instructions (`packages/devkit-spec/`), and the append-only statements are
amended to allow this governed removal: `docs/decisions/README.md`, the seed README and `templates/decision.md` in
the spec bundle, the `spec-sync` skill, the `spec:living-spec-writing` instruction, and the resolution contract in
`CAP-DOCS-document-model` and `CAP-DOCS-document-lookup`. That amendment is recorded as its own PADR once q1 is
answered.

## 4. Lifecycle & Verification

- Unit tests (`packages/devkit-spec/tests/unit/features/documents/`): ADR provenance parsing (scalar and list),
  alias parsing, alias collisions with any declared ID or alias, non-ADR aliases refused, the alias-aware lookup.
- Governance tests (`packages/devkit-spec/tests/unit/features/governance/` and the rule's own tests): supersession
  pairing and its fix, alias references as fixable errors in current documents, historical files byte-identical
  after `devkit rules fix`, traceability with an alias.
- Handoff test: a graduating ADR ID that equals a declared alias is refused.
- CLI tests: `devkit spec resolve` and `devkit spec refs --direction in` for an alias.
- End-to-end fixture: two ADRs compacted into one with a clean rules check and alias resolution.
- Acceptance demonstration: decided by q3.

## 5. Open Decisions

- **q1 Direction and compaction model**: supersession integrity plus delete-based compaction with ADR aliases, or
  supersession integrity only, or integrity plus tombstone compaction without aliases.
- **q2 Playbook aliases**: whether the playbook-alias question leaves this proposal.
- **q3 Real compaction**: whether Development compacts one real chain of the ledger as the acceptance demonstration.
