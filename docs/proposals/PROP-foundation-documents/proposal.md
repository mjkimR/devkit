---
id: PROP-foundation-documents
title: Foundation documents for project-wide background
summary: "Adds a foundation group under docs/ (and per namespace) for project-wide background documents such as the glossary, product vision and style guides, which a spec constitution pointer sends agents to when a decision depends on them, and moves the glossary into it."
status: reviewing                     # draft | reviewing | accepted | rejected
created_at: 2026-10-26
target_area: documents/
priority: high                        # critical | high | medium | low
size: M                               # S | M | L | XL
planning_effort: medium               # low | medium | high (hint for Planning)
dev_effort: medium                    # low | medium | high (hint for Development)
boundaries:
  owns:
    - packages/devkit-spec/src/devkit_spec/features/
    - packages/devkit-spec/src/devkit_spec/base/
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/
    - packages/devkit-spec/tests/
    - packages/devkit-viewer/frontend/src/lib/
    - packages/devkit-viewer/src/devkit_viewer/static/
    - scripts/handbook.py
    - tools/devkit-dev/tests/integration/
    - docs/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - docs/capabilities/harness/
    - docs/capabilities/delivery/
    - docs/architecture/
    - docs/glossary.md
    - docs/glossary.yaml
    - docs/README.md
    - .devkit/installation.json
    - guides/
  excludes:
    - A new ID-bearing document kind
    - Product, brand or style content of any particular project
    - Changes to the glossary table format
    - Changes to the search ranker (CAP-SRCH-document-search)
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
depends_on: [PROP-table-driven-document-kinds]
---

# [PROP-foundation-documents] Foundation documents for project-wide background

## 1. Background & Hypothesis

The Living Spec has kinds for behavior and structure (capabilities, use cases, architecture, decisions) and a free
form for evidence (materials). It has no place for project-wide background that applies to every piece of work but
is neither behavior nor evidence: the product's purpose and principles, a brand or tone guide, a visual style
direction, a domain or setting overview. The glossary is the only document of this nature today, and it sits alone
at `docs/glossary.md` (with `docs/glossary.yaml` for search synonyms).

Without a place, such background is written into capabilities, where it bends the contract shape and invites
entrypoints and reconciliation that do not apply, or into materials, where it loses its standing as current and
binding. Either way agents do not know to read it, so work that depends on it (wording, naming, interface and
content decisions) drifts from it.

Hypothesis: a fixed foundation group under `docs/` (and under each namespace's docs root), holding ID-free documents
that apply as a whole rather than through per-document relations, fixes both problems. The glossary moves into it.
The `spec` bundle points agents to the group when a work unit starts, and search indexes it through each document's
English summary.

## 2. Technical Spike Questions

- **Q1**: Name and layout: `docs/foundation/` with free file names, or a small set of named documents (for example
  glossary, product, style)? Is "foundation" the clearest name next to existing terms such as bundle context?
- **Q2**: Do foundation documents stay ID-free like the glossary today, and what do the spec rules then check in
  them (summary, references to ID-bearing documents, nothing)? Confirm that ID-free documents under a namespace docs
  root pass the current rules.
- **Q3**: How do agents read the group without loading all of it into every context: a pointer in the managed
  guidance, a step in the `spec` skill at work-unit start, or search only? What bounds its size?
- **Q4**: What moves with the glossary: the owner-resolution input of `RULE-document-reference`, the synonym file
  read by document search, the seeded `docs-skeleton` files, writing instructions, the `spec-sync` skill, the
  brownfield adoption playbook and the namespace glossary rule in the living-spec writing instruction.

## 3. Proposed Design & Impact

Spike evidence: `materials/spike-findings.md` (F1-F6). Review: `envelopes/challenger-01.yaml`. Items marked
**(open: qN)** follow the user's answer to that question of this round; the text states the recommended option.

- **Group** (open: q1, q2): a fixed directory `docs/foundation/` and `docs/packages/<name>/foundation/` (created under
  `docs/`), documented in `CAP-DOCS-document-model` and `CAP-DOCS-namespaces`. Files are ID-free, free-named Markdown,
  outside the document index as today (`CAP-DOCS-document-model` rule 3.2); ID-free files in both locations pass the
  current rules (F2). "Foundation" gets a glossary row whose Avoid column separates it from the code layer of
  `devkit-core` (F4).
- **Reading** (`PADR-background-pointer-in-constitution`): one conditional line in the spec constitution names the
  group and its trigger; each file opens with a one-line scope; a guidance test asserts both.
- **Search** (open: q4): no search coverage; the group is read by path, so no English `summary` is required in its
  files. Search and glossary expansion stay in `CAP-DOCS-document-search` (not `CAP-SRCH-document-search`, the
  ranker).
- **Rules** (open: q5): `RULE-document-reference` resolves backtick-quoted IDs in foundation files the way it resolves
  root glossary Owners, with the same alias check, no autofix and no graph edges; legacy-reference checks already
  apply (F2).
- **Glossary move** (open: q3): `glossary.md` and `glossary.yaml` move into the root group, and the repository's own
  glossary moves in the same change. Every literal path of F3 is one acceptance item with a test that the old path is
  no longer read: `RULE-document-reference` Owner check, search `GLOSSARY_PATH` and `SPEC_GLOSSARY_INVALID`
  (`base/errors.py`), the `docs-skeleton` seed and its README tables, `living-spec-writing` (including the package
  glossary rule), `architecture-writing`, `spec-sync`, `adr-compaction`, the brownfield `migration.md`, rule guides,
  viewer `bookGroup` (front end and committed build), `docs/README.md`, `docs/architecture/README.md` and the
  capabilities naming the path (`CAP-DOCS-document-model`, `CAP-DOCS-document-search`, `CAP-GOV-spec-rules`,
  `CAP-HARN-agent-guidance`, `CAP-DLV-release-handbook`, `CAP-DLV-delivery-workflows`). The receipt
  `.devkit/installation.json` follows `devkit sync`. The handoff ADR declares that it amends the
  glossary paths that `ADR-spec-package-on-devkit` and `ADR-writing-and-terminology-guidance` fix.
- **Release handbook**: `scripts/handbook.py` reads the glossary at the pinned commit from the new path, falls back to
  `docs/glossary.md` for a commit before the move, and fails with a code when neither exists; its tests cover both
  layouts. This reads Git history, not a current format, so it is no legacy reader under the Compatibility section of
  `AGENTS.md`. The handbook pages themselves are not refreshed.
- **Existing consumers**: no migration and no notice (Compatibility): a consumer that selects `docs-skeleton` gets the
  seed at the new path on its next sync and moves its own glossary.
- Non-goals: no new ID-bearing kind, no relation fields to or from foundation documents, no change to the glossary
  table columns, the Owner check's semantics or the search ranker.

### Order with parallel proposals

- `PROP-table-driven-document-kinds` lands first (`depends_on`); a directory this proposal adds to the viewer or the
  rules is read from its kind and directory definitions, never added as a constant beside them.
- `PROP-ux-documentation` follows this proposal (open: q6), so its guidance names the glossary at its new path and
  points to foundation style documents instead of restating them; its option 6b (an object table in the glossary)
  would change the glossary table format, which this proposal excludes.

### Planning decisions

- Planning (`policy`): search capability citation corrected to `CAP-DOCS-document-search`; `docs/capabilities/search/`
  removed from owns; the owns list extended to every path F3 names; `depends_on` on
  `PROP-table-driven-document-kinds` per the user's ordering decision.

## 4. Lifecycle & Retirement Criteria

- On acceptance: recorded with `devkit spec proposal accept`, then handed off to a spec bundle on
  `dev-foundation-documents`; the proposal is deleted there and its decisions become ADRs.
- On rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
