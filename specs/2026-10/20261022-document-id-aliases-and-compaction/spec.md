---
id: SPEC-document-id-aliases-and-compaction
title: Document and Playbook ID Aliases
summary: Introduces an optional aliases frontmatter field of previous or alternate IDs on every ID-bearing document, resolved through one alias-aware DocumentIndex lookup and rewritten to canonical IDs by devkit rules fix, and gives playbook aliases the same identifier meaning.
status: in-progress
created: 2026-10-22
related_capabilities:
  - CAP-DOCS-document-model
  - CAP-DOCS-document-lookup
  - CAP-DOCS-document-search
  - CAP-DLV-proposal-incubation
  - CAP-DIST-context-and-playbooks
  - CAP-SRCH-document-search
related_stories: []
workflow: sdd-spec-feature
---

# [SPEC-document-id-aliases-and-compaction] Document and Playbook ID Aliases

## 1. Problem Statement & Motivation

Handed off from proposal PROP-document-id-aliases-and-compaction on 2026-10-22.
- **Preserved Materials**: `docs/materials/2026-10/20261022-document-id-aliases-and-compaction`

A document is found only by its exact ID. Renaming or merging a capability, story, architecture document, milestone
or any other ID-bearing document breaks every reference written with the old ID: `RULE-document-reference` reports
each as unresolved and `devkit spec resolve` finds nothing. The only rename devkit handles is the handed-off
`PROP-<slug>` to `SPEC-<slug>` rewrite of the proposals lifecycle.

Playbooks already have an `aliases` frontmatter field, but it holds English search keywords that
`devkit playbook search` ranks. Document ID aliases under the same name with another meaning would give one field
two concepts.

The accepted design is `ADR-document-id-aliases` (document aliases) and `ADR-playbook-aliases-as-identifiers`
(playbook aliases). This spec implements exactly that design; the proposal's Proposed Design (sections 3.1 to 3.4)
and Lifecycle & Verification (section 4) are readable at historical Git
`2963ae20:docs/proposals/PROP-document-id-aliases-and-compaction/proposal.md`.

## 2. User Stories

- **US-1**: As an agent renaming a Living Spec document, I want to keep the old ID in `aliases`, so that existing
  references keep resolving and one `devkit rules fix` moves current documents to the new ID.
- **US-2**: As an agent reading documents, I want `devkit spec resolve`, `refs` and `search` to accept an alias, so
  that an old ID found in history leads to the current document.
- **US-3**: As a bundle author renaming a playbook, I want its old asset ID kept as an alias, so that published
  `<bundle>/<old-id>` selectors keep working, and search ranks only `name` and `description`.

## 3. Non-Goals

1. **Scope Excluded**: ADR compaction, an append-only amendment procedure and ADR supersession checking
   (`supersedes`/`superseded_by` parsing, pairing, status checks, correcting drifted ADRs).
   - **Rationale**: withdrawn in Planning; the ledger survey stays as Planning history only.
2. **Scope Excluded**: editing any existing file under `docs/decisions/`.
3. **Scope Excluded**: alias-aware lookup in the devkit-agt rules catalog (`RULE-` IDs stay exact) and in app-common.
4. **Scope Excluded**: migration or compatibility for keyword playbook aliases: a keyword list is refused in place
   (no external consumers).
5. **Scope Excluded**: renaming any existing document of this repository; the procedure is documented, not applied.

## 4. Acceptance Criteria & Behavioral Contracts

Example IDs in the scenarios (CAP-X-new, CAP-X-old and the like) are plain-text fixtures, not references.

### [AC-01] Alias shape on every ID-bearing kind
- **Given** a document of any kind (CAP, US, ARCH, ADR, MS, MAT, PROP, PADR, SPEC, PLAN, TASKS, REC through
  `reconcile_id`, FB) whose frontmatter has `aliases`
- **When** the index loads it and `devkit rules check` runs `RULE-document-reference`
- **Then** each well-formed alias with the declaring document's own prefix is indexed, and the rule reports one
  violation per malformed item: a value that is not a list, a non-string item, an item that is not a full ID, a
  foreign prefix, the document's own ID, a repeated item, or a legacy date- or number-based form that
  `RULE-id-convention` reports; materials included, `aliases` entries never counted as references

### [AC-02] Declared ID precedence and collisions
- **Given** an alias that another document declares as its ID (of any status), or that two documents declare as an
  alias
- **When** `RULE-document-reference` runs
- **Then** a collision violation is reported at line 1 of every document involved, the target resolves as it would
  without the alias (or stays unresolved), and `devkit rules fix` leaves references to it unchanged

### [AC-03] Alias references are fixable errors in current documents
- **Given** a current document referencing a uniquely resolving alias in a relation field or prose (an ADR's alias
  included)
- **When** `devkit rules check` then `devkit rules fix` run
- **Then** the check reports a fixable error naming the canonical ID, the fix rewrites the reference to the
  canonical ID (frontmatter and prose, quote style kept), and a recheck reports no `RULE-document-reference`
  violation; relation-field prefix typing is unchanged

### [AC-04] Historical files and decision records are never rewritten
- **Given** a completed spec bundle file, a done or dropped milestone, an ADR and a PADR, each citing an alias
- **When** `devkit rules check` and `devkit rules fix` run
- **Then** no alias violation is reported for them and each file is byte-identical after the fix

### [AC-05] Glossary Owner naming an alias
- **Given** a `docs/glossary.md` Owner cell naming an alias
- **When** `devkit rules check` and `devkit rules fix` run
- **Then** a non-fixable violation names the canonical ID and the glossary is unchanged by the fix

### [AC-06] One canonical mapping across identity checks
- **Given** references written with an alias in a milestone `depends_on`, a unit anchor `depends_on`, a story or
  capability traceability field, a proposal's `milestone` field and a late `PROP-<slug>` whose `SPEC-<slug>` is an
  alias
- **When** the spec rules and hygiene run
- **Then** a `depends_on` cycle through an alias is reported, a traceability pair linked through an alias is not
  reported as one-sided and its fix adds no duplicate entry, milestone membership counts the alias, and
  `devkit rules fix` rewrites the late `PROP-<slug>` to the canonical `SPEC-` ID in one pass

### [AC-07] Lookup commands accept aliases
- **Given** a document declaring an alias
- **When** `devkit spec resolve <alias>`, `devkit spec refs <canonical> --direction in|out`, `devkit spec search
  <alias>` and `devkit spec entrypoints --target <alias>` run
- **Then** `resolve` prints the canonical `[DOCUMENT: ...]` line with `alias=<alias>` (JSON: `"alias": "<alias>"`,
  `null` on an exact hit) with no notice; `refs --direction in` includes alias-written references; `refs
  --direction out` groups an alias with its canonical ID as one target; `search` pins the document; `--target`
  selects the canonical document

### [AC-08] Handoff carries and translates aliases
- **Given** an accepted proposal declaring a PROP- alias and a PADR declaring a PADR- alias, with a PADR, an existing
  ADR and another unit's `depends_on` citing the carried aliases
- **When** `devkit spec proposal handoff` runs
- **Then** `spec.md` declares the alias with `SPEC-`, the promoted ADR declares it with `ADR-`, each citation is
  rewritten to the new canonical ID, and `devkit rules check` reports no `RULE-document-reference` violation

### [AC-09] Handoff and scaffolding refuse alias clashes
- **Given** a graduating `SPEC-<slug>` or `ADR-<slug>` or a translated alias that equals an existing ID or alias, or
  two PADRs of one handoff declaring the same alias, or a new proposal whose `SPEC-<slug>` is an existing alias
- **When** the handoff, `devkit spec proposal new`, `devkit spec proposal padr` or `devkit spec new` runs
- **Then** it exits 2 with its existing conflict code before writing any file

### [AC-10] Playbook aliases are identifiers
- **Given** a bundle whose playbook declares `aliases`
- **When** the bundle manifest is validated
- **Then** an item outside the `[a-z][a-z0-9-]*` slug grammar is refused with `BUNDLE_INVALID`, and an alias equal to
  a playbook asset ID of the bundle (its own included), repeated, or declared by another playbook of the bundle is
  refused with `BUNDLE_INVALID`

### [AC-11] Playbook search ignores aliases
- **Given** synchronized playbooks whose aliases contain a query term that their name and description lack
- **When** `devkit playbook search <term>` runs
- **Then** those playbooks are not returned because of the alias, and returned candidates still carry `aliases`

### [AC-12] Playbook get resolves aliases
- **Given** synchronized playbooks of one bundle
- **When** `devkit playbook get <bundle>/<selector>` runs
- **Then** an exact asset ID is served with `"alias": null` even when another playbook's override declares a
  colliding alias; an alias declared by exactly one effective header is served as the canonical `id` with
  `"alias": "<selector>"`; an alias declared by more than one effective header exits 2 with
  `PLAYBOOK_ALIAS_AMBIGUOUS` and a deterministic `[ACTION]`; an undeclared selector keeps `SELECTION_INVALID`

### [AC-13] Bundled playbooks and contracts follow
- **Given** the repository after the change
- **When** `just rules-check` and `uv run devkit status` run after `uv run devkit sync`
- **Then** both report no problem, the seven bundled playbooks carry no keyword `aliases`, and no file under
  `docs/decisions/` is in the diff

## 5. Assumptions

- `devkit playbook get` has JSON output only (`CAP-DIST-context-and-playbooks` section 4), so the alias used is
  reported in the `alias` JSON field; there is no text sentinel to carry `alias=`.
- A malformed `aliases` field drops the bad items and keeps the good ones; the rule reports each bad item. Alias shape
  issues are reported like duplicate IDs: on every targeted document, materials and completed specs included.
- A reference to a colliding alias is reported as an ambiguous target naming the declaring documents, never silently
  resolved.
- The legacy date- or number-based pattern moves from `RULE-id-convention` into the document ID grammar module so
  both rules read one definition.
- Playbook alias uniqueness at manifest validation compares against the bundle's playbook asset IDs only (other asset
  kinds live in other selector namespaces). A clash refused at handoff reuses `SPEC_PROPOSAL_TARGET_EXISTS`; at
  scaffolding it reuses `SPEC_PROPOSAL_SLUG_CONFLICT`, `SPEC_PROPOSAL_EXISTS` and `SPEC_EXISTS`.
- Handoff carries the proposal's and PADRs' validated aliases only (the parsed document's alias list), so a malformed
  item reported by the rule is not translated.
