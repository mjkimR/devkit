---
id: ADR-namespace-steering-registers
title: Namespace vocabulary registers follow shared and local steering
summary: "For namespace vocabulary, we place optional glossary and UX object registers in steering and read global plus selected local files, to keep one layout and scoped search, accepting explicit legacy glossary migration."
status: accepted
created_at: 2026-11-04
supersedes: [ADR-namespace-steering-directories, ADR-ux-screens]
---

# [ADR-namespace-steering-registers] Namespace vocabulary registers follow shared and local steering

- **Status**: Accepted
- **Date**: 2026-11-04
- **Involved Components/Capabilities**: `CAP-DOCS-namespaces`, `CAP-DOCS-document-search`, `CAP-GOV-spec-rules`,
  `CAP-HARN-agent-guidance`

## 1. Context & Problem Statement

Namespace UX documents and background have independent roots, while their terminology still points to global
registers and package glossaries use a different layout. `ADR-namespace-steering-directories` excluded namespace
glossary files and deferred local UX objects and search synonyms. That exception prevents the existing shared-plus-
local steering convention from applying to vocabulary.

## 2. Decision Drivers

- One steering layout for global and registered namespaces.
- Shared vocabulary stays visible while local definitions apply to their own namespace.
- Search expansion follows the namespace selection already used for document candidates.
- Project-authored registers remain optional and are never copied or moved automatically.

## 3. Considered Options

- **Root plus selected local registers in steering (selected)**: one directory contract and bounded vocabulary
  context; existing package glossary content needs an explicit move or merge.
- **Keep root-only UX objects and separate package glossary paths**: no migration, but vocabulary remains an
  exception to namespace ownership and search ignores local synonyms.
- **Copy root registers to every namespace**: independent files, but duplicates shared definitions and invites drift.

## 4. Decision Outcome

- Optional namespace glossary and UX object registers live in `docs/packages/<name>/steering/`, under the root
  Markdown contract; `glossary.yaml` is accepted there. The partial-supersession statement below names the replaced namespace clauses.
  → `CAP-DOCS-namespaces` 3.4 (MAY), `CAP-GOV-spec-rules` 3.14 (MUST).
- This decision replaces only `ADR-ux-screens` clauses requiring one root-only register, unconditional root
  creation with the first UX document, and root-only writes of drafted register rows by `spec-sync`. Shared rows
  stay in the root register, namespace rows stay in its local register, and either file is created only when its rows
  are needed. Its screen format, register contents and caps, review rubric, timing and link/coverage rules remain.
  → `CAP-HARN-agent-guidance` 4.3 (SHOULD), `CAP-DLV-delivery-workflows` rule 9 (MUST).
- Agents read the root glossary/register with the selected namespace files, keep shared rows global, and put local
  rows in the namespace; a local glossary definition applies only to that namespace. No empty register is seeded.
  → `CAP-HARN-agent-guidance` Shared writing instructions (SHOULD).
- Search loads root synonyms followed by selected registered namespace files in name order and unions token
  clusters without leaking unselected namespaces; global mode uses only root.
  → `CAP-DOCS-document-search` rule 4 (MUST).
- Registered canonical glossary Owner cells receive the root reference and alias-fix behavior.
  → `CAP-GOV-spec-rules` 3.3 (MUST).
- A legacy package glossary receives a manual move/merge finding, without automatic data changes or a second
  canonical location. → `CAP-GOV-spec-rules` 3.14 (MUST).
- UX object representations and calls to action remain agent review concerns; link and coverage rules do not parse
  those registers. → `CAP-HARN-agent-guidance` Shared writing instructions (SHOULD).

- Supersedes in part `ADR-namespace-steering-directories`: the namespace glossary locations and exclusions, the root-only search synonyms, and the deferred namespace UX object register; its other decisions remain in force.

- Supersedes in part `ADR-ux-screens`: the clauses requiring one root-only register, unconditional root creation with the first UX document, and root-only writes of drafted register rows by `spec-sync`. Shared rows stay global, namespace rows stay local, and files are created only when needed; other screen and register contracts remain.

## 5. Consequences

- Global terms remain shared, while package terms and UX vocabulary stay with package background.
- Search in all namespaces can expand ambiguous shared words to several clusters; union order is deterministic.
- Existing package glossaries need an explicit move into steering and title/summary frontmatter; merge content
  when both paths exist. No automatic move or generated copy risks replacing project-authored definitions.

## 6. Confirmation

Namespace register search tests cover explicit/cwd/global/all selection, absent files, unregistered directories and
actual-file errors. Deployed `RULE-steering-documents` and `RULE-document-reference` tests cover canonical layout,
limits, legacy migration, Owner checks and fixes. Context and docs/spec guidance tests cover optional root-plus-local
register reads and all UX agent consumers. UX object semantics: Review only.
