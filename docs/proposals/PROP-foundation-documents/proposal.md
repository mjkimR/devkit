---
id: PROP-foundation-documents
title: Foundation documents for project-wide background
summary: "Adds a foundation group under docs/ (and per namespace) for project-wide background documents such as the glossary, product vision and style guides, which agents read when a work unit starts and search covers, and moves the glossary into it."
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
    - packages/devkit-spec/src/devkit_spec/bundles/spec/bundle/
    - packages/devkit-spec/tests/
    - docs/capabilities/documents/
    - docs/capabilities/governance/
    - docs/capabilities/search/
    - docs/glossary.md
    - docs/glossary.yaml
    - docs/README.md
    - guides/
  excludes:
    - A new ID-bearing document kind
    - Product, brand or style content of any particular project
    - Changes to the glossary table format
task_kind: feature                    # feature | bugfix: the spec follows sdd-spec-<task_kind>
workflow: sdd-proposal
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

- A foundation group at `docs/foundation/` and `docs/packages/<name>/foundation/`, documented in
  `CAP-DOCS-document-model` and `CAP-DOCS-namespaces`; the documents carry an English `summary` and no ID.
- The glossary (`glossary.md` and `glossary.yaml`) moves into the group; every consumer named in Q4 reads the new
  path. The repository's own glossary moves in the same change.
- The `spec` bundle's guidance tells agents when to read the group, and the `docs-skeleton` preset seeds it.
- Document search indexes the group (`CAP-SRCH-document-search`).
- Non-goals: no new ID-bearing kind, no relation fields to or from foundation documents, no change to the glossary
  table columns or the owner check itself.

## 4. Lifecycle & Retirement Criteria

- On acceptance: recorded with `devkit spec proposal accept`, then handed off to a spec bundle on
  `dev-foundation-documents`; the proposal is deleted there and its decisions become ADRs.
- On rejection: `status: rejected` only, with the user's reason in the commit message; a later hygiene pass writes
  the rejection ADR and deletes the proposal.
